import sys
import asyncio

from decouple import config
from db import database
from managers.item import ItemManager
from managers.price import PriceManager
from utils.scraper import WishlistScraper


EMAIL = config("EMAIL")
PASSWORD = config("PASSWORD")
WISHLIST_URL = "https://www.amazon.com/hz/wishlist/ls/3I84B5IFV53GK/"


def scrape_wishlist():
    """Connect to wishlist and performs scrape of items."""
    # connect to wishlist page
    sign_in = False
    while not sign_in:
        driver = WishlistScraper.connect(WISHLIST_URL)
        # Sign in
        sign_in = WishlistScraper.log_in(driver, EMAIL, PASSWORD)

    # #### Back in Wishlist page ####
    # Get items in Wishlist
    items = WishlistScraper.get_items(driver)
    # Close driver
    driver.quit()
    return items


async def startup():
    await database.connect()


async def shutdown():
    await database.disconnect()


async def main():
    await startup()
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
            print('No price, inserting:', it['title'], item_price['price'])  # Debug
        elif latest_price['price'] != price:
            item_price = await PriceManager.insert_item_price(price_data)
            print('Diff price, inserting:', it['title'], item_price['price'])  # Debug
            # TODO: if price is lower send email notification
            if price < latest_price['price']:
                print(f"Price for {it['title']} dropped from ${latest_price['price']} to ${price}")

    # DEBUG

    await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
