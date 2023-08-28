from models import item
from db import database


class ItemManager:
    """Manages all queries for the items table."""

    @staticmethod
    async def get_item_by_id(item_id):
        """Fetch one item by id."""
        q = item.select()
        q = q.where(item.c.id == item_id)
        return await database.fetch_one(q)

    @staticmethod
    async def get_item_by_code(item_code):
        """Fetch one item by code."""
        q = item.select()
        q = q.where(item.c.code == item_code)
        return await database.fetch_one(q)

    @staticmethod
    async def create_item(item_data):
        """Insert a new item in items table and return the item."""
        id_ = await database.execute(item.insert().values(item_data))
        q = item.select()
        q = q.where(item.c.id == id_)
        return await database.fetch_one(q)

    # TODO: delete_item
    # TODO: get_all_items
