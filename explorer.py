import data.config as conf
from eth_async.data.models import Networks
from evm_explorers.explorer_api import APIFunctions
from evm_explorers.models import Sort


async def get_time_last_tx(address: str) -> str:
    api = APIFunctions(url=Networks.Sepolia.api.url, key=conf.SEPOLIA_API_KEY)
    res = await api.account.txlist(address=address, sort=Sort.Desc)
    res = res['result']
    for tx in res:
        if address.lower() == tx['to'].lower():
            return tx['timeStamp']
    return res[0]['timeStamp']