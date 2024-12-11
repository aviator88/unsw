from eth_async.data.models import RawContract, DefaultABIs
from eth_async.utils.utils import read_json
from eth_async.classes import Singleton

from data.config import ABIS_DIR


class Contracts(Singleton):

    SUPER_BRIDGE = RawContract(
        title='Super Bridge',
        address='0xea58fcA6849d79EAd1f26608855c2D6407d54Ce2',
        abi=read_json(path=(ABIS_DIR, 'superbridge.json'))
    )
