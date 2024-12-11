import asyncio

from playwright.async_api import Page
from loguru import logger

import data.config as conf
from db_api import db_utils
from eth_async.data.models import Network, Networks


async def init_metamask(page: Page):
    await page.wait_for_load_state()
    await restore_wallet(page)
    accounts = db_utils.find_accounts_profile()
    acc_amount = len(accounts)
    await add_account(page, acc_amount)
    await add_network(page, Networks.Unichain_Sepolia)

async def unlock_wallet(page: Page):
    await page.wait_for_load_state()
    await page.locator('//*[@id="password"]').type(conf.MM_PASS)
    await page.locator('//*[@id="app-content"]/div/div[2]/div/div/button').click()

async def get_address(page: Page, acc_amount: int) -> str:
    await page.locator('//*[@id="app-content"]/div/div[2]/div/div[2]/button').click()
    await page.locator(f'//html/body/div[3]/div[3]/div/section/div[2]/div[{acc_amount+1}]/div/button/span').click()
    await page.locator('//html/body/div[4]/div[2]/div/button[1]/div/div/p').click()
    address = await page.locator('//html/body/div[3]/div[3]/div/section/div/div/div[2]/p').text_content()
    return address

async def restore_wallet(page: Page):
    for count in range(1, conf.ATTEMPTS_NUMBER + 1):
        try:
            logger.info('Starting to restore wallets')
            await page.wait_for_load_state()
            common_path = '//*[@id="app-content"]/div/div[2]/div/div/div'

            #Confirm 1st page
            await page.locator('//*[@id="onboarding__terms-checkbox"]').click()
            await page.locator(f'{common_path}/ul/li[3]/button').click()

            #Confirm 2nd page
            await page.locator('//*[@id="metametrics-opt-in"]').click()
            await page.locator(f'{common_path}/div[2]/button[2]').click()

            #Enterpassphrase
            passphrase = str(conf.PASSPHRASE).split(' ')
            num = 0
            for word in passphrase:
                await page.locator(f'//*[@id="import-srp__srp-word-{num}"]').type(word)
                num += 1
            await page.locator(f'{common_path}/div[4]/div/button').click()

            #Enter password
            await page.locator(f'{common_path}/div[2]/form/div[1]/label/input').fill(conf.MM_PASS)
            await page.locator(f'{common_path}/div[2]/form/div[2]/label/input').fill(conf.MM_PASS)
            await page.locator(f'{common_path}/div[2]/form/div[3]/label/span[1]/input').click()
            await page.locator(f'{common_path}/div[2]/form/button').click()

            #Last page
            await page.locator(f'{common_path}/div[2]/button').click()
            await page.locator(f'{common_path}/div[2]/button').click()
            await page.locator(f'{common_path}/div[2]/button').click()

            await asyncio.sleep(5)

            try:
                await page.locator('//*[@id="popover-content"]/div/div/section/div[2]/div/div[2]/div/button').click()
            except:
                pass

            #"No,thanks"
            await page.locator('//html/body/div[3]/div[3]/div/section/div/button[2]').click()
            await asyncio.sleep(5)
            logger.success(f'Successful wallet recovery from seed phrase')
            break
        
        except Exception as err:
            logger.error(f'Failed to restore ({err})')
            logger.info(f'Error when getting an account, trying again, attempt No.{num}')
        
        logger.info('Ending recover wallet')

async def add_account(page: Page, acc_amount: int):
    #Add wallet
    for acc_count in range(acc_amount-1):
        for attempt in range(conf.ATTEMPTS_NUMBER):
            try:
                await page.reload()
                common_path = '//html/body/div[3]/div[3]/div/section'
                await asyncio.sleep(1+attempt)
                await page.locator('//*[@id="app-content"]/div/div[2]/div/div[2]/button').click()
                await asyncio.sleep(1+attempt)
                try:
                    await page.locator(f'{common_path}/div[3]/button').click()
                except:
                    try:
                        await page.locator(f'{common_path}/div[2]/button').click()
                    except:
                        continue
                
                await page.locator(f'{common_path}/div/div[1]/button').click()

                await page.locator('//*[@id="account-name"]').type(f'Account {acc_count+2}')
                text = await page.locator(f'{common_path}/div/form/div[1]/p').text_content()
                if text == 'Такое имя счета уже существует':
                    logger.info(f'Error adding Account {acc_count+2}: {text}')
                    await page.locator(f'{common_path}/header/div[3]').click()
                else:
                    await page.locator(f'{common_path}/div/form/div[2]/button[2]').click()
                    logger.success(f'Successfully added account {acc_count+2}')
                break
            except:
                logger.warning(f'Failed to add account {acc_count+2}')

async def add_network(page: Page, network: Network):
    common_path = '//html/body/div[3]/div[3]/div/section'
    await page.locator('//*[@id="app-content"]/div/div[2]/div/div[1]/button').click()
    await page.locator(f'{common_path}/div[2]/button').click()
    await page.locator(f'//*[@id="networkName"]').type(network.name)
    await page.locator(f'{common_path}/div/div[1]/div[2]/div/button/span').click()
    await page.locator(f'{common_path}/div/div[1]/div[2]/div[2]/div/div/button').click()
    await page.locator(f'//*[@id="rpcUrl"]').type(network.rpc)
    await page.locator(f'//*[@id="rpcName"]').type(network.rpc)
    await page.locator(f'{common_path}/div/div[2]/button').click()
    await page.locator(f'//*[@id="chainId"]').type(str(network.chain_id))
    await page.locator(f'//*[@id="nativeCurrency"]').type(network.coin_symbol)
    await page.locator(f'{common_path}/div/div[1]/div[5]/div[1]//button/span').click()
    await page.locator(f'{common_path}/div/div[1]/div[5]/div[2]/div/div/button').click()
    await page.locator('//*[@id="additional-rpc-url"]').type(network.explorer)
    await page.locator(f'{common_path}/div/div[2]/button').click()
    await page.locator(f'{common_path}/div/div[2]/button').click()
    logger.success(f'Successfully added {network.name}')
    await switch_network(page, network)

async def switch_network(page: Page, network: Network):
    await page.locator('//*[@id="app-content"]/div/div[2]/div/div[1]/button').click()
    networks = await page.query_selector_all('div.mm-box--justify-content-flex-start')
    for net in networks:
        network_name = await net.text_content()
        if network_name.lower() == network.name.lower():
            await net.click()
            logger.success(f'Successful switch to {network.name}')
            return
    await page.locator('//html/body/div[3]/div[3]/div/section/header/div[2]/button/span').click()
    await add_network(page, network)
    
async def choose_account(page: Page, acc_num: int):
    await page.wait_for_load_state()
    await page.locator('//*[@id="app-content"]/div/div[2]/div/div[2]/button').click()
    await page.locator(f'//html/body/div[3]/div[3]/div/section/div[2]/div[{acc_num}]/div').click()
    logger.success(f'Successfully selected account {acc_num} in Metamask')
