#!/usr/bin/env python

import sys
import inspect
import os
import asyncio
import logging
from decouple import config
from db import database
from managers.item import ItemManager
from managers.price import PriceManager
from utils.scraper import WishlistScraper
from utils.email_formatter import EmailFormatter
from services.ses import SESService


EMAIL = config("EMAIL")
PASSWORD = config("PASSWORD")
WISHLIST_URL = "https://www.amazon.com/hz/wishlist/ls/3I84B5IFV53GK/"
CONNECTION_ATTEMPTS = 10
LOG_LEVEL = "INFO"
FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
BASE_DIR = os.path.dirname(os.path.abspath(FILENAME))
SOURCE_EMAIL = config("EMAIL_SOURCE")
DESTINATION_EMAIL = config("EMAIL_DESTINATION")


def scrape_wishlist():
    """Connect to wishlist and performs scrape of items."""
    # connect to wishlist page
    signed_in = False
    conn_count = 0
    while not signed_in and conn_count < CONNECTION_ATTEMPTS:
        driver = WishlistScraper.connect(WISHLIST_URL)
        # Sign in
        signed_in = WishlistScraper.log_in(driver, EMAIL, PASSWORD)
        conn_count += 1
    if conn_count == 10:
        logging.warning("Maximum connection attempts reached. Ending program.")
        sys.exit(1)
    # #### Back in Wishlist page ####
    # Get items in Wishlist
    items = WishlistScraper.get_items(driver)
    # Close driver
    driver.quit()
    return items


async def startup():
    """Connect to database."""
    await database.connect()


async def shutdown():
    """Disconect database."""
    await database.disconnect()


async def main():
    """Excecute main function."""
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.INFO,
        filename=os.path.join(BASE_DIR, 'ebookTracker.log')
    )
    print(os.path.join(BASE_DIR, 'ebookTracker.log'))
    # Configure selenium logger
    logger_selenium = logging.getLogger('selenium')
    logger_selenium.setLevel(logging.WARNING)
    # Configure SQLalchemy logger
    logger_SQLalchemy = logging.getLogger('sqlalchemy.engine')
    logger_SQLalchemy.setLevel(logging.INFO)
    # Start script
    logging.info('STARTING. Connecting to DB')
    await startup()
    # Instantiate a SES Service
    ses = SESService()
    # Get Items from Amazon wishlist
    items_ = scrape_wishlist()
    for key, value in items_.items():
        # Extract price value from dict
        price = value.pop('price')
        # Search for the item in the db
        it = await ItemManager.get_item_by_code(value['code'])
        # If item not already in db, insert new row
        if not it:
            it = await ItemManager.create_item(value)
        # Format price_data
        price_data = {
            'price': price,
            'item_id': it['id']
        }
        # Get latest_price
        latest_price = await PriceManager.get_latest_item_price(it['id'])
        # If no latest_price or price different than latest_price, insert price
        if not latest_price:
            item_price = await PriceManager.insert_item_price(price_data)
            logging.info(f"No price, inserting: {it['title']}, ${item_price['price']}")
        elif latest_price['price'] != price:
            item_price = await PriceManager.insert_item_price(price_data)
            logging.info(f"Diff price, inserting: {it['title']}, ${item_price['price']}")
            # If price is lower log it and send email
            if price < latest_price['price']:
                logging.info(f"Price for {it['title']} dropped from ${latest_price['price']} to ${price}")
                # SEND MAIL if price dropped more than 10% or price < $3
                if price < 3 or (price / latest_price['price']) < 0.9:
                    # Format text message body
                    text_body = EmailFormatter.format_html(
                        item_price['date'],
                        it['title'],
                        it['author'],
                        latest_price['price'],
                        price,
                        it['href'])
                    # Format html message body
                    html_body = EmailFormatter.format_html(
                        item_price['date'],
                        it['title'],
                        it['author'],
                        latest_price['price'],
                        price,
                        it['href'])
                    # send mail
                    ses.send_email(
                        SOURCE_EMAIL,
                        [DESTINATION_EMAIL],
                        "New ebook Price Alert",
                        text_body,
                        html_body)

    logging.info("Ending program normally.")
    await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
