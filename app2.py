import asyncio
import random

from loguru import logger
from playwright.async_api import async_playwright

import data.config as conf
import sepolia, metamask, thirdweb, pw_utils, google, db_utils
from eth_async.data.models import Networks
from data.utils import format_proxy


async def farming_eth():
    logger.info('Start farming sepolia ETH')
    accounts = db_utils.ready_for_farming()
    acc_count = 1
    for account in accounts:
        if account.id < 0:
            acc_count += 1
            continue
        async with async_playwright() as p:
            logger.info(f'Work with account {account}')

            profile_path, extetion_version, extetion_path = await pw_utils.get_profile(account.name)
            proxy = await format_proxy(account.proxy)
            args = await pw_utils.get_browser_args(extetion_path)
            user_agent = pw_utils.get_useragent(account)
            context = await p.chromium.launch_persistent_context(
                # '',
                user_data_dir=profile_path,
                user_agent=user_agent,
                channel='chrome',
                headless=False,
                args=args,
                proxy=proxy,
                slow_mo=conf.SLOW_MO
            )

            try:
                page_google = await pw_utils.open_page(context, 'Ethereum Sepolia Faucet')
                await page_google.goto('https://cloud.google.com/application/web3/faucet/ethereum/sepolia')
                await page_google.wait_for_load_state()
                await asyncio.sleep(random.randint(1,5))
                await google.faucet(page_google, account)
                await page_google.close()
                await context.close()
            except:
                logger.warning(f'Token claim failed on account {account.name}')

            acc_count += 1

async def bridge():
    logger.info('Start bridge ETH from Sepolia to Unichain')
    wallets = db_utils.ready_for_unichain()
    await sepolia.bridge_to_unichain(wallets=wallets, ) #multiplier=1)

async def thirdweb_work():
    accounts = db_utils.ready_for_unichain()
    acc_count = 1
    for account in accounts:
        if account.id < 5:
            acc_count += 1
            continue
        async with async_playwright() as p:
            logger.info(f'Work with account {account}')

            profile_path, extetion_version, extetion_path = await pw_utils.get_profile(account.name)
            proxy = await format_proxy(account.proxy)
            args = await pw_utils.get_browser_args(extetion_path)
            user_agent = await pw_utils.get_useragent(account) #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'    #FakeUserAgent().random
            context = await p.chromium.launch_persistent_context(
                # '',
                user_data_dir=profile_path,
                user_agent=user_agent,
                channel='chrome',
                headless=False,
                args=args,
                proxy=proxy,
                slow_mo=conf.SLOW_MO
            )

            page_metamask = await pw_utils.open_page(context, 'metamask', reload=False)
            await page_metamask.goto(f'chrome-extension://{conf.EXTENTION_IDENTIFIER}/home.html')
            await page_metamask.wait_for_load_state()
            text = await page_metamask.locator('//*[@id="app-content"]/div/div[2]/div/div').text_content()
            if text.find('Давайте приступим к делу') >= 0:
                await metamask.init_metamask(page_metamask)
            else:
                await metamask.unlock_wallet(page_metamask)
            await metamask.choose_account(page_metamask,account.id)
            await metamask.switch_network(page_metamask, Networks.Unichain_Sepolia)
            await page_metamask.close()
            result = False
            attempt = 0
            while not result and attempt <= conf.ATTEMPTS_NUMBER:
                try:
                    attempt += 1
                    logger.info(f'Attempt to deploy a contract #{attempt}')
                    page = await pw_utils.open_page(context, 'thirdweb', reload=False)
                    await page.goto('https://thirdweb.com/login')
                    await page.wait_for_load_state()
                    # await asyncio.sleep(10)
                    title = await page.query_selector('h1')
                    if title == None:
                        logger.info(f'Loging')
                        await thirdweb.sign_in(context, page, acc_count)
                    else:
                        if ((await title.text_content()) == 'Get started with thirdweb'):
                            logger.info(f'Loging')
                            await thirdweb.sign_in(context, page, acc_count)
                    input('>')
                    # logger.info(f'Try to claim tocken on unichain')
                    # await thirdweb.claim_token(context, page, account)
                    result = await thirdweb.deploy(context, page, account)
                except:
                    pass

            acc_count += 1

async def open_browser():
    accounts = db_utils.find_accounts_profile()
    acc_count = 1
    for account in accounts:
        if account.id < 0:
            acc_count += 1
            continue
        async with async_playwright() as p:
            logger.info(f'Work with account {account}')
            profile_path, extetion_version, extetion_path = await pw_utils.get_profile(account.name)
            proxy = await format_proxy(account.proxy)
            args = await pw_utils.get_browser_args(extetion_path)
            user_agent = await pw_utils.get_useragent(account) #FakeUserAgent().random #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
            context = await p.chromium.launch_persistent_context(
                # '',
                user_data_dir=profile_path,
                user_agent=user_agent,
                channel='chrome',
                headless=False,
                args=args,
                proxy=proxy,
                slow_mo=conf.SLOW_MO
            )
            await asyncio.sleep(1)

            page = pw_utils.open_page(context, '')
            input('>')

            page_metamask = pw_utils.open_page(context, 'metamask', reload=False)
            await page_metamask.goto(f'chrome-extension://{conf.EXTENTION_IDENTIFIER}/home.html')
            await page_metamask.wait_for_load_state()
            text = await page_metamask.locator('//*[@id="app-content"]/div/div[2]/div/div').text_content()
            if text.find('Давайте приступим к делу') >= 0:
                await metamask.init_metamask(page_metamask)
            else:
                await metamask.unlock_wallet(page_metamask)

            input('Delay for browser setup >')

            # await page.close()
            await context.close()

async def main():
    print('''  Select the action:
1) Import accounts from CSV or JSON to the DB;
2) Browser setup
3) Work
4) Profile rename
5) Exit.''')
    # try:
    action = int(input('> '))
    if action == 1:
        logger.info('Start importing accounts from CSV or JSON into DB')
        db_utils.db_insert()

    elif action == 2:
        logger.info('The browser opens for configuration')
        await open_browser()

    elif action == 3:
        while True:
            await farming_eth()
            await bridge()
            await thirdweb_work()
            logger.info("Going to sleep for 1 hour")
            await asyncio.sleep(3600)
    
    elif action == 4:
        await google.profile_rename()


if __name__ == '__main__':
    asyncio.run(main())