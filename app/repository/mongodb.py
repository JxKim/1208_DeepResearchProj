from pymongo import AsyncMongoClient
from app.config.config import get_setting
_mongo_client : AsyncMongoClient | None = None



def get_mongo_client()->AsyncMongoClient:

    global _mongo_client

    if _mongo_client is None:
        setting = get_setting()
        _mongo_client = AsyncMongoClient(
            setting.mongodb_uri

        )

    return _mongo_client

def get_database():

    setting = get_setting()
    db_name = setting.mongodb_database

    return get_mongo_client()[db_name]

