import asyncio
import random
import os

from playwright.async_api import BrowserContext, Page
from loguru import logger
from fake_useragent import FakeUserAgent

import data.config as conf
from db_api import db_utils
from db_api.models import Wallet


async def get_profile(profile: str) -> list[str]:
    profile_path = f'{conf.PROFILES_PATH}/{profile}'
    extetion_version = os.listdir(f'{profile_path}/Extensions/{conf.EXTENTION_IDENTIFIER}')[0]
    extetion_path = f'{profile_path}/Extensions/{conf.EXTENTION_IDENTIFIER}/{extetion_version}'
    return profile_path, extetion_version, extetion_path

async def get_browser_args(extetion_path: str) -> list:
    args: list = [
            f"--disable-blink-features=AutomationControlled",
            f"--disable-extensions-except={extetion_path}",
            f"--load-extension={extetion_path}"
        ]
    if conf.HEADLESS:
        args.append(f"--headless=new")

    return args

def get_useragent(account: Wallet) -> str:
    if account.useragent == None:
        useragent = FakeUserAgent().random
        print(f'User agent: {useragent}')
        action = int(input('Save (Yes-1, No-0)? > '))
        if action == 1:
            db_utils.write_useragent(account.address, useragent)
    else:
        useragent = account.useragent
    return useragent

async def random_delay() -> float:
    delay = float(str(f'0.{random.randint(3,7)}'))
    return delay

async def open_page(context: BrowserContext, search_str: str, reload: bool = True) -> Page:
    await asyncio.sleep(5)
    titles = [await p.title() for p in context.pages]
    page_index = 0

    for title in titles:
        if title.lower().find(search_str.lower()) >= 0:
            page = context.pages[page_index]
            if reload == True:
                await page.reload()
            return page
        page_index += 1

    page = await context.new_page()
    return page

async def wait_page(context: BrowserContext, search_str: str, attempts: int = conf.ATTEMPTS_NUMBER) -> Page:
    for attempt in range(attempts):
        logger.debug(f'Find page of {search_str}, attempt: {attempt}')
        await asyncio.sleep(1*attempt)
        titles = [await p.title() for p in context.pages]
        page_index = 0
        for title in titles:
            if title.lower().find(search_str.lower()) >= 0:
                page = context.pages[page_index]
                return page
            page_index += 1
    return

async def close_all(context: BrowserContext, search_str: str):
    await asyncio.sleep(5)
    titles = [await p.title() for p in context.pages]
    page_index = 0

    for title in titles:
        if search_str.lower() in title.lower():
            page = context.pages[page_index]
            await page.close()
        page_index += 1
