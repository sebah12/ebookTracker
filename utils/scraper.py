import logging
from random import choice
from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


WINDOW_SIZES = ["352, 480",
                "640,480",
                "1280, 720",
                "1280, 1080",
                "1440, 1080",
                "1920, 1080"]


class WishlistScraper:
    """Performs connection and extraction of webpage data."""

    def connect(url):
        """Connect to driver and go to wishlist page."""
        # Create window of random size
        options = webdriver.ChromeOptions()
        window_size = choice(WINDOW_SIZES)
        print(window_size)
        options.add_argument("--window-size=" + window_size)
        logging.info(f"Connecting to {url} with WINDOW_SIZE = {window_size}")
        driver = webdriver.Chrome(options=options)
        # Implicit wait
        driver.implicitly_wait(3)   # seconds

        # Navigate to the url
        driver.get(url)

        # #### In Whishlist page ####
        return driver

    def log_in(driver, username, password):
        """Access sign in page and log in with username and password."""
        # Find sign in button and go to sign in page
        try:
            signIn_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID,
                                                "nav-link-accountList"))
                )
        except TimeoutException:
            logging.info("Couldn't find Log in button.")
            driver.quit()
            return False

        signIn_button.click()

        # #### In sign in Page ####

        # Find email input box and submit button
        input_box = driver.find_element(by=By.ID, value="ap_email")
        submit_button = driver.find_element(by=By.ID, value="continue")

        # Enter email and click submit
        input_box.send_keys(username)
        submit_button.click()

        # Find password input and submit button
        input_box = driver.find_element(by=By.ID, value="ap_password")
        submit_button = driver.find_element(by=By.ID, value="signInSubmit")

        # Enter password and click submit
        input_box.send_keys(password)
        submit_button.click()

        # Once logged in
        # Find Footer and return True, else return False
        try:
            _ = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID,
                                                "navFooter"))
                )
        except TimeoutException:
            logging.info("Exiting after Signing in because additional information was required.")
            driver.quit()
            return False
        return True

    def get_items(driver):
        """
        Get items from Wishlist with the following info.

        items_dict{id:{data-itemid, data-price, title, href}}
        """
        # Scroll to the bottom of the page to load all items in wishlist
        footer = driver.find_element(By.ID, "navFooter")
        ActionChains(driver).scroll_to_element(footer).perform()
        # Wait for all items in list to appear
        sleep(10)

        # Find items in wishlist (id and price info)
        items = driver.find_elements(
            by=By.CLASS_NAME,
            value="a-spacing-none.g-item-sortable",
        )
        items_dict = dict()

        # Get price
        items_prices = [item.get_attribute("data-price") for item in items]

        # Get id
        items_ids = [item.get_attribute("data-itemid") for item in items]
        items_names = ["itemName_" + item_id for item_id in items_ids]

        # Get title
        items_titles_element = [driver.find_element(by=By.ID, value=item_name)
                                for item_name in items_names]
        items_titles = [item_title.get_attribute("title")
                        for item_title in items_titles_element]

        # Get href
        items_href = [item_title.get_attribute("href")
                      for item_title in items_titles_element]

        # Get author
        items_byline = ["item-byline-" + item_id for item_id in items_ids]
        items_authors = [driver.find_element(by=By.ID, value=item_byline).text
                         for item_byline in items_byline]

        # return a dictionary with all the items and their attributes
        for i in range(len(items)):
            items_dict[items_ids[i]] = {"code": items_ids[i],
                                        "title": items_titles[i],
                                        "price": float(items_prices[i]),
                                        "href": items_href[i],
                                        "author": items_authors[i],
                                        }
        return items_dict
