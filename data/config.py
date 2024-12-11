import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from loguru import logger

load_dotenv()

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

FILES_DIR = os.path.join(ROOT_DIR, 'files')

logger.add(
    sink=f'{FILES_DIR}/debug.log',
    format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
    level='DEBUG'
)


#General
PASSPHRASE = os.getenv('passphrase')

#wallet DB
WALLET_PATH = './files/wallets.json'
CSV_PATH = './files/accounts.csv'
JSON_PATH = './files/account.json'
TXT_PATH = './files/accounts.txt'
DB_PATH = 'sqlite:///files/wallet.db'

#playwright
HEADLESS = False
ATTEMPTS_NUMBER = 10
PROFILE_PATH = '/Users/dolgoarsinnyhdmitrij/Library/Application Support/Google/Chrome/Default'
PROFILES_PATH = '/Users/dolgoarsinnyhdmitrij/Library/Application Support/Google/Chrome'
EXTENTION_IDENTIFIER = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
EXTENTION_VERSION = '12.5.0_0'
EXTENTION_PATH = f'{PROFILE_PATH}/Extensions/{EXTENTION_IDENTIFIER}/{EXTENTION_VERSION}'
MM_PASS = '***********'
# SLOW_MO = None
SLOW_MO = 200

#eth_async
ABIS_DIR = os.path.join(ROOT_DIR, 'eth_async', 'abis')

ETHEREUM_API_KEY = str(os.getenv('ETHEREUM_API_KEY'))
ARBITRUM_API_KEY = str(os.getenv('ARBITRUM_API_KEY'))
ARBITRUMNOVA_API_KEY = str(os.getenv('ARBITRUMNOVA_API_KEY'))
OPTIMISM_API_KEY = str(os.getenv('OPTIMISM_API_KEY'))
BSC_API_KEY = str(os.getenv('BSC_API_KEY'))
POLYGON_API_KEY = str(os.getenv('POLYGON_API_KEY'))
AVALANCHE_API_KEY = str(os.getenv('AVALANCHE_API_KEY'))
MOONBEAM_API_KEY = str(os.getenv('MOONBEAM_API_KEY'))
FANTOM_API_KEY = str(os.getenv('FANTOM_API_KEY'))
CELO_API_KEY = str(os.getenv('CELO_API_KEY'))
GNOSIS_API_KEY = str(os.getenv('GNOSIS_API_KEY'))
HECO_API_KEY = str(os.getenv('HECO_API_KEY'))
GOERLI_API_KEY = str(os.getenv('GOERLI_API_KEY'))
SEPOLIA_API_KEY = str(os.getenv('SEPOLIA_API_KEY'))
LINEA_API_KEY = str(os.getenv('LINEA_API_KEY'))
BASE_API_KEY = str(os.getenv('BASE_API_KEY'))
OKLINK_API_KEY = str(os.getenv('OKLINK_API_KEY'))
UNI_SEPOLIA_API_KEY = str(os.getenv('UNI_SEPOLIA_API_KEY'))
