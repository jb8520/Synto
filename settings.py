import argparse

import os

from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen = True)
class Settings:
    dev: bool
    

    bot_token: str
    

    bot_id: int
    bot_owner_id: int

    support_server_id: int | None
    supporter_role_id: int | None


    database_host: str
    database_name: str
    database_user: str
    database_password: str


    synto_premium_sku_id: int

    counting_save_1_sku_id: int
    counting_save_3_sku_id: int
    counting_save_10_sku_id: int


def _build_settings() -> Settings:
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--dev',
        action = 'store_true',
        help = 'Run using the DEV bot and DEV database',
    )

    parser.add_argument(
        '--prod-db',
        action = 'store_true',
        help = 'Use production database, even in dev mode',
    )

    args = parser.parse_args()

    use_dev_db = args.dev and not args.prod_db

    return Settings(
        dev = bool(args.dev),
        

        bot_token = str(os.environ['DEV_BOT_TOKEN'] if args.dev else os.environ['BOT_TOKEN']),
        

        bot_id = int(os.environ['DEV_BOT_ID'] if args.dev else os.environ['BOT_ID']),
        bot_owner_id = int(os.environ['BOT_OWNER_ID']),

    
        support_server_id = (
            int(os.environ['SUPPORT_SERVER_ID'])
            if os.environ.get('SUPPORT_SERVER_ID')
            else None
        ),
        supporter_role_id = (
            int(os.environ['SUPPORTER_ROLE_ID'])
            if os.environ.get('SUPPORTER_ROLE_ID')
            else None
        ),


        database_host = str(os.environ['DEV_DATABASE_HOST'] if use_dev_db else os.environ['DATABASE_HOST']),
        database_name = str(os.environ['DEV_DATABASE_NAME'] if use_dev_db else os.environ['DATABASE_NAME']),
        database_user = str(os.environ['DEV_DATABASE_USER'] if use_dev_db else os.environ['DATABASE_USER']),
        database_password = str(os.environ['DEV_DATABASE_PASSWORD'] if use_dev_db else os.environ['DATABASE_PASSWORD']),
        

        synto_premium_sku_id = int(os.environ['DEV_SYNTO_PREMIUM_SKU_ID'] if use_dev_db else os.environ['SYNTO_PREMIUM_SKU_ID']),
        
        counting_save_1_sku_id = int(os.environ['DEV_COUNTING_SAVE_1_SKU_ID'] if use_dev_db else os.environ['COUNTING_SAVE_1_SKU_ID']),
        counting_save_3_sku_id = int(os.environ['DEV_COUNTING_SAVE_3_SKU_ID'] if use_dev_db else os.environ['COUNTING_SAVE_3_SKU_ID']),
        counting_save_10_sku_id = int(os.environ['DEV_COUNTING_SAVE_10_SKU_ID'] if use_dev_db else os.environ['COUNTING_SAVE_10_SKU_ID']),
    )


settings = _build_settings()