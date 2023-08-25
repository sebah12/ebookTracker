from models import price
from db import database


class PriceManager:
    """Manages all queries for the prices table."""

    @staticmethod
    async def get_all_item_prices(item_id):
        """Fetch all prices for the given item."""
        q = price.select()
        q = q.where(price.c.item_id == item_id)
        return await database.fetch_all(q)

    @staticmethod
    async def get_all_item_prices_newest_first(item_id):
        """Fetch all prices for the given item ordered by date."""
        q = price.select()
        q = q.where(price.c.item_id == item_id).order_by(price.c.date.desc())
        return await database.fetch_all(q)

    @staticmethod
    async def get_latest_item_price(item_id):
        """Fetch the most recent price of the given item."""
        q = price.select()
        q = q.where(price.c.item_id == item_id).order_by(price.c.date.desc())
        return await database.fetch_one(q)

    @staticmethod
    async def insert_item_price(price_data):
        """Insert a new price in the prices table and return the row."""
        id_ = await database.execute(price.insert().values(price_data))
        q = price.select()
        q = q.where(price.c.id == id_)
        return await database.fetch_one(q)

    # TODO: get_lowest_item_price
    # TODO: delete_price
