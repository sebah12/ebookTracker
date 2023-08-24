import sqlalchemy

from db import metadata


price = sqlalchemy.Table(
    "prices",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("price", sqlalchemy.Float(), nullable=False),
    sqlalchemy.Column("date", sqlalchemy.DateTime,
                      server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("item_id", sqlalchemy.ForeignKey("items.id"),
                      nullable=False)
)
