import random

from loguru import logger
from web3.types import TxParams

from eth_async.client import Client
from eth_async.data.models import TxArgs, TokenAmount, Networks
from eth_async.data.contracts import Contracts
from db_api.models import Wallet


async def drop_to_proxy(zero: Wallet, wallets: list):
    client = Client(private_key=zero.proxy_pk, network=Networks.Sepolia)
    balance = await client.wallet.balance()
    for wallet in wallets:
        if str(wallet.proxy_address).lower() == str(client.account.address).lower():
            continue
        
        amount = TokenAmount((0.25 / len(wallets)) * float(str(balance)) * float(f'1.{random.randint(0,99)}'))
        logger.info(f'Try transfert {amount.Ether} ETH from proxy {zero.name} to proxy {wallet.name}')
        reciept = await client.transactions.simple_tx(
            client=client,
            name=zero.name,
            chain=Networks.Sepolia,
            to_address=wallet.proxy_address,
            amount=amount
            )
        if 'status' in reciept and reciept['status'] == 1:
            logger.success(f'Success transfert {amount.Ether} ETH from proxy {zero.name} to proxy {wallet.name}.')
            logger.success(f'https://sepolia.etherscan.io/tx/{reciept["transactionHash"].hex()}')
        else:
            logger.warning(reciept)

async def collect_ETH(wallets: list, proxy: bool = True, multiplier: float = 0.5):
    for wallet in wallets:
        if proxy:
            client = Client(private_key=wallet.proxy_pk, network=Networks.Sepolia)
        else:
            client = Client(private_key=wallet.private_key, network=Networks.Sepolia)

        if str(client.account.address).lower() == str(wallets[0].proxy_address).lower():
            continue
        amount = TokenAmount(multiplier * float(str(await client.wallet.balance())),wei=True)
        logger.info(f'Try transfert {amount.Ether} ETH from {wallet.name} to proxy {wallets[0].name}')
        reciept = await client.transactions.simple_tx(
            client=client,
            chain=Networks.Sepolia,
            to_address=wallets[0].proxy_address,
            amount=amount
            )
        
        if 'status' in reciept and reciept['status'] == 1:
            logger.success(f'Success transfert {amount.Ether} ETH from {client.account.address} to {wallet.proxy_address}.')
            logger.success(f'https://sepolia.etherscan.io/tx/{reciept["transactionHash"].hex()}')
        else:
            logger.warning(reciept)

async def proxy_to_wallet(wallet: Wallet) -> bool:
    client = Client(private_key=wallet.proxy_pk, network=Networks.Sepolia)
    amount = await client.wallet.balance()
    logger.info(f'Try transfert {amount.Ether} ETH from proxy-wallet to wallet {wallet.name}')
    receipt = await client.transactions.simple_tx(
        client=client,
        chain=Networks.Sepolia,
        to_address=wallet.address,
        amount=amount
        )

    if 'status' in receipt and receipt['status'] == 1:
        logger.success(f'Success transfert {amount.Ether} ETH from {client.account.address} to {wallet.proxy_address}.')
        logger.success(f'https://sepolia.etherscan.io/tx/{receipt["transactionHash"].hex()}')
    else:
        logger.warning(receipt)

async def bridge_to_unichain(wallets: Wallet, multiplier: float = 0.5):
    for wallet in wallets:
        logger.info(f'Try brigde fromSepolia to Unichain on {wallet.name}')
        try:
            await proxy_to_wallet(wallet)
        except:
            pass
        client = Client(private_key=wallet.private_key, network=Networks.Sepolia)
        balance = await client.wallet.balance()
        logger.info(f'Client {client.account.address} is OK. Balance: {balance.Ether} ETH')
        if float(str(balance.Ether)) < 0.1:
            logger.warning('Low balance (< 0.1)')
            continue
        bridge_contract = await client.contracts.get(Contracts.SUPER_BRIDGE)
        
        value = TokenAmount(multiplier * float(str(balance)),wei = True)
        failed_text = f'Failed to bridge {value.Ether} ETH to unichain in wallet {client.network.name}'
        logger.info(f'Try bridged {value.Ether} ETH to unichain in wallet {client.network.name}')
        args = TxArgs(
            _to = client.account.address,
            _minGasLimit = 200000,
            _extraData = '0x7375706572627269646765'
        )
        tx_params = TxParams(
            to=bridge_contract.address,
            data=bridge_contract.encodeABI('bridgeETHTo', args=args.tuple()),
            value=value.Wei
        )
        gas_price = await client.transactions.gas_price()
        gas = await client.transactions.estimate_gas(tx_params)
        value = TokenAmount(int(str(value)) - 1.2 * int(str(gas)) * int(str(gas_price)), wei = True)

        print(int(str(gas)) * int(str(gas_price)))

        logger.info(f'Gas: {gas}, gas price: {gas_price}, value: {value.Ether} / {value.Wei} ETH')
        if int(str(value)) <= 0:
                logger.warning(str(f'{failed_text}: Low balance'))
                continue
        
        tx_params['gas'] = int(str(gas.Wei))
        tx_params['value'] = int(str(value.Wei))
        tx_params = await client.transactions.auto_add_params(tx_params=tx_params)

        try:
            tx = await client.transactions.sign_and_send(tx_params=tx_params)
        except ValueError:
            logger.warning(f'{failed_text}: Gas to hight')
            continue
        
        try:
            receipt = await tx.wait_for_receipt(client=client, timeout=600)
            if 'status' in receipt and receipt['status'] == 1:
                logger.success(f'Success transfert {value.Ether} ETH from {Networks.Sepolia.name} to Unichain.')
                logger.success(f'https://sepolia.etherscan.io/tx/{receipt["transactionHash"].hex()}')
                continue
            else:
                logger.warning(receipt)
                continue
        except:
            logger.warning('Transaction is not in the chain after 600 seconds')
            continue

