import asyncio
import random

from playwright.async_api import BrowserContext, Page
from loguru import logger

import pw_utils
import data.config as conf
from db_api import db_utils
from db_api.models import Wallet


async def sign_in(context: BrowserContext, page: Page, acc_count: int):
    metamask_path = '//*[@id="app-content"]/div/div/div'
    for attempt in range(conf.ATTEMPTS_NUMBER):
        try:
            try:
                if await page.querySelector('.fade-in-0.relative'):
                    thirdweb_path = '//html/body/div[2]/main/div/div'
                else:
                    thirdweb_path = '//html/body/div/main/div/div'
            except:
                thirdweb_path = '//html/body/div/main/div/div'
            # MetaMask wallet click
            await page.locator(f'{thirdweb_path}/div/div[1]/div/div/ul/li[2]/button/div[2]').click()
            await page.wait_for_load_state()
            # sign in button click
            try: await page.locator(f'{thirdweb_path}/div/div[2]/div/div[2]/button[1]').click()
            except: pass
            page_metamask = await pw_utils.wait_page(context=context, search_str='MetaMask', attempts=5)
            text = await page_metamask.locator(f'{metamask_path}').text_content()
            if text.find('Подключиться с помощью MetaMask') >= 0:
                #checkbox all click
                await page_metamask.locator(f'{metamask_path}/div[2]/div[2]/div[1]/div/label/span/input').click()
                #next button click
                await page_metamask.locator(f'{metamask_path}/div[3]/div[2]/footer/button[2]').click()
                #confirm button click
                await page_metamask.locator(f'{metamask_path}/div[3]/div[2]/footer/button[2]').click()
            
            await page_metamask.wait_for_load_state()
            button = await page_metamask.query_selector('button.mm-box.mm-button-base--block.mm-button-primary')
            await button.click()
            await page.wait_for_load_state()
            logger.success(f'Success login Account {acc_count} in Thirdweb')
            break
        except:
            logger.warning('Failed login in Thirdweb')

async def sign_out(context: BrowserContext, page: Page, acc_count: int):
    await page.wait_for_load_state()
    button = await page.query_selector('div.inline-flex.items-center.justify-center')
    await button.click()
    button = await page.query_selector('button.inline-flex.rounded-md.font-medium.py-2')
    await button.click()
    logger.success(f'Success logout Account {acc_count} in Thirdweb')

async def claim_token(context: BrowserContext, page: Page, account: Wallet):
    await page.goto(f'https://thirdweb.com/unichain-sepolia-testnet')
    await page.wait_for_load_state()

    try:
        await asyncio.sleep(5)
        buttons = await page.query_selector_all('button')
        for button in buttons:
            text = await button.text_content()
            if text.find('Get 0.01 ETH') >= 0:
                print(text)
                await asyncio.sleep(10)
                await page.locator('//*[@id="gLIfn4"]/div/label/input').click()
                input('Press Enter >')
                await button.click()
                logger.success(f'The claim for tokens was successful on the account{account}')
                return True
        logger.warning(f'Token claim failed on account {account}')
        return False
    except:
        logger.warning(f'Token claim failed on account {account}')
        return False

async def deploy(context: BrowserContext, page: Page, account: Wallet) -> bool:
    common_path = '//html/body/div[1]'
    try:
        if await page.querySelector('.fade-in-0.relative'):
            common_path = '//html/body/div[2]'
        else:
            common_path = '//html/body/div'
    except:
        common_path = '//html/body/div'

    try:
        await page.goto('https://thirdweb.com/explore')
        await asyncio.sleep(10)
        contracts = await page.query_selector_all('a.bg-primary')
        num = random.randint(1,len(contracts))                      #Choosing a random contract
        await contracts[num].click()
        await asyncio.sleep(10)
        #Title, account and number for the name
        h1 = await page.locator(f'{common_path}/div[2]/div/div/div[1]/div/div[1]/div/div[2]/h1').text_content()
        rand = random.randint(1,10)
        #Fill in the fields
        field = await page.query_selector_all('.chakra-input.css-1e6f5f2')
        await field[0].type(f'Contract {h1}: {account.name} v.{rand}.0')
        await field[1].type('TKN')
        button = await page.query_selector('.inline-flex.bg-foreground')
        await button.click()
        #Confirm in metamask 2 times
        for n in range(2):
            page_metamask = await pw_utils.wait_page(context, 'metamask')
            await page_metamask.wait_for_load_state()
            await asyncio.sleep(5)
            button = await page_metamask.query_selector('.mm-box.mm-text.mm-button-base.mm-button-primary')
            if await button.text_content() != 'Подтвердить':
                await page_metamask.close()
                logger.warning(f'Contract deploy failed on account {account}: Low balance')
                return True
            await button.click()
            await asyncio.sleep(10)
        
        await asyncio.sleep(20)
        await page.wait_for_load_state()
        button = await page.query_selector('.bg-primary')
        await button.click()
        db_utils.update_unichain_time(account.address)
        logger.success(f'Success deploy "Contract {h1}: {account} v.{rand}.0" on account {account}')
        return True
        
    
    except:
        logger.warning(f'Contract deploy failed on account {account}')
        return False
