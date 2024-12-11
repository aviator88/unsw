import asyncio
import os
from datetime import datetime, timedelta

from playwright.async_api import Page
from loguru import logger

import data.config as conf
import pw_utils, explorer
import db_utils
from db_api.models import Wallet


async def login(page: Page, account: Wallet):
    try:
        await page.wait_for_load_state()
        await page.locator('//*[@id="gb"]/div[2]/div[3]/div[1]/a').click(delay=await pw_utils.random_delay())
        await page.wait_for_load_state()
        menu = await page.query_selector_all('.VV3oRb.YZVTmd.SmR8')
        print(menu)
        for punkt in menu:
            print(str(await punkt.text_content()).find(account.google_acc))
            if str(await punkt.text_content()).find(account.google_acc) >= 0:
                await punkt.click()
                break
        await page.wait_for_load_state()
        await page.locator('//*[@id="password"]/div[1]/div/div[1]/input').type(account.google_pass)
        await page.locator('//*[@id="passwordNext"]/div/button').click(delay=await pw_utils.random_delay())
        logger.success(f'Success login {account.name} in Google')
    except:
        logger.warning(f'Failed login {account.name} in Google')

async def faucet(page: Page, account: Wallet):
    await page.wait_for_load_state()
    try:
        await page.locator('//*[@id="mat-input-0"]').type(account.address)
        await page.locator('//*[@id="drip"]/cw3-faucet-drip-form/form/button').click(delay=await pw_utils.random_delay())
        logger.info('Drop attempt, wait 5 minutes...')
        await asyncio.sleep(5*60)
        time_last_tx = await explorer.get_time_last_tx(account.address)
        delta_time = datetime.now() - datetime.fromtimestamp(int(time_last_tx))
        text = await page.locator('//*[@id="main-content"]/cw3-faucet-page').text_content()
        if (delta_time <= timedelta(hours=1)) or (text.find('Drip complete') >= 0):
            db_utils.update_farming_time(account.address)
            logger.success(f'Success Token claim on account {account.name}')
            return
        logger.warning(f'Token claim failed on account {account.name}')
    except:
        logger.warning(f'Token claim failed on account {account.name}')
        return

async def profile_rename():
    accounts = db_utils.find_accounts_profile()
    for account in accounts:
        profile_path, extetion_version, extetion_path = await pw_utils.get_profile(account.profile)
        print(profile_path)
        new_profile_path = f'{conf.PROFILES_PATH}/{account.name}'
        print(new_profile_path)
        os.rename(profile_path, new_profile_path)

async def logout(page: Page):
    try:
        await page.wait_for_load_state()
        await page.locator('//*[@id="gb"]/div[2]/div[3]/div[1]/div[2]/div/a').click(delay=await pw_utils.random_delay())
        await asyncio.sleep(5)
        button = await page.query_selector('a.V5tzAf.jFfZdd.Dn5Ezd')
        button.click(delay=await pw_utils.random_delay())
        input('>')
        if str(await page.title).find('Вход – Google Аккаунты') >= 0:
            logger.success(f'Success logout Account in Google')
        else:
            logger.warning(f'Failed logout Account in Google')
    except:
        logger.warning(f'Failed logout Account in Google')