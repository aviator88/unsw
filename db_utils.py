import json, csv, random
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from loguru import logger
from fake_useragent import FakeUserAgent

from db_api.models import Base, Wallet
import data.config as conf


engine = create_engine(conf.DB_PATH, echo=True)
Base.metadata.create_all(engine)

def db_insert(from_csv: bool = True):
    if from_csv:
        csv_to_json()

    with open(conf.WALLET_PATH) as fp:
        wallets_list = json.load(fp)
    
    session = Session(bind=engine)

    for item in wallets_list:
        wallet = Wallet(
            name = item['name'],
            private_key = item['private_key'],
            address = item['address'],
            proxy_pk = item['proxy_pk'],
            proxy_address = item['proxy_address'],
            google_acc = item['google_acc'],
            google_pass = item['google_pass'],
            next_farming_time = datetime.now(),
            next_unichain_time = datetime.now(),
            proxy = item['proxy'],
            useragent = ''
        )
        session.add(wallet)
        
        # try:
        session.commit()
        # except:
            # logger.warning(f'Failed add wallet {wallet} in DB')
            # continue
        logger.success(f'Wallet {wallet} add in DB')

def csv_to_json(path: str=conf.CSV_PATH, path_json: str=conf.WALLET_PATH):
    accounts = []
    with open(path) as f:
        reader = csv.reader(f,delimiter=';')
        logger.info(f'File {f.name} open')
        count = 0
        for row in reader:
            if count == 0:
                count += 1
                continue
            account = {
                'name': row[0],
                'private_key': row[1],
                'address': row[2],
                'proxy_pk': row[3],
                'proxy_address': row[4],
                'google_acc': row[5],
                'google_pass': row[6],
                # 'next_farming_time': row[7],
                # 'next_unichain_time': row[8],
                'proxy': row[7],
                # 'useragent': row[10],
            }
            accounts.append(account)
            count += 1
        logger.info(f'{len(accounts)} accounts add in list')
    list_to_json(accounts)
    logger.info(f'Accounts import to JSON')

def list_to_json(accounts: list, path: str=conf.WALLET_PATH):
    with open(path, 'w') as fp:
	    json.dump(accounts, fp)

def read_accounts() -> list:
    logger.info('Reading accounts from the DB')
    with Session(engine) as session:
        accounts = session.query(Wallet)

    return accounts

def find_accounts_profile(no_account: bool = False) -> list[Wallet]:
    if no_account:
        logger.info(f'Reading accounts without profile from DB')
        criterion = (Wallet.profile == '')
        with Session(engine) as session:
            accounts = session.query(Wallet).filter(criterion).all()
        logger.info(f'{len(accounts)} accounts without profile found in DB')
    else:
        logger.info(f'Reading accounts with profile from DB')
        criterion = (Wallet.profile != '')
        with Session(engine) as session:
            accounts = session.query(Wallet).filter(criterion).all()
        logger.info(f'{len(accounts)} accounts with profile found in DB')
    return accounts

def update_farming_time(address: str):
    criterion = (Wallet.address == address)
    with Session(engine) as session:
        account = session.query(Wallet).filter(criterion).first()
        logger.info(f'Update next farming time for account {account}')
        account.next_farming_time = datetime.now() + timedelta(days=1)
        session.commit()

def update_unichain_time(address: str):
    criterion = (Wallet.address == address)
    with Session(engine) as session:
        account = session.query(Wallet).filter(criterion).first()
        logger.info(f'Update next unichain time for account {account}')
        days = random.randint(1,7)
        account.next_unichain_time = datetime.now() + timedelta(days=days)
        session.commit()

def ready_for_farming() -> list:
    logger.info('Looking for accounts ready for farming')
    criterion = (Wallet.next_farming_time < datetime.now())
    with Session(engine) as session:
        accounts = session.query(Wallet).filter(criterion).all()
    logger.info(f'Found {len(accounts)} accounts ready for farming')
    return accounts

def ready_for_unichain() -> list:
    logger.info('Looking for accounts ready for unichain')
    criterion = (Wallet.next_unichain_time < datetime.now())
    with Session(engine) as session:
        accounts = session.query(Wallet).filter(criterion).all()
    logger.info(f'Found {len(accounts)} accounts ready for unichain')
    return accounts

def write_useragent(address: str, useragent: str):
    criterion = (Wallet.address == address)
    with Session(engine) as session:
        account = session.query(Wallet).filter(criterion).first()
        logger.info(f'Write useragent for account {account}')
        account.useragent = useragent
        session.commit()