import sqlalchemy

from db import metadata


item = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("code", sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column("title", sqlalchemy.String(250), nullable=False),
    sqlalchemy.Column("author", sqlalchemy.String(125), nullable=False),
    sqlalchemy.Column("href", sqlalchemy.String(125), nullable=False)
)
