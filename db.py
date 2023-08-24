import databases
import sqlalchemy
from decouple import config


DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:{config('DB_PORT')}/ebooks"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
