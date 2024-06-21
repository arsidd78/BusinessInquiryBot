from playwright.async_api import async_playwright
import asyncio
import logging
import time
import pandas as pd
logging.basicConfig(
    filemode='a',
    filename='bot_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    )
class Bot:
    def __init__(self,business_name,headless:bool,time=30000):
        self.business_name = business_name
        self.time = time
        self.url = 'https://ner.economy.ae/Search_By_BN.aspx'
        self.headless = headless
        self.data_list = []

    async def run(self):
        async with async_playwright() as playwright:
            
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(self.url)
            logging.info(f'The bot reached to the site successfully')
            # English Version of the page:
            language_link = page.locator('//a[@id="ctl00_SwitchLanguageButton"]')
            logging.info('Language link founded')
            language = await language_link.text_content()
            if language.strip().lower() != 'english':
                await language_link.click()
                logging.info('English link was founded and was clicked')    
            # Filling Form:
            await page.fill(
                'xpath=//input[@name="ctl00$MainContent$View_ucSearch_By_BN$cbpBreadCrumbOverAll_BAs$txtBNEnglish"]',
                self.business_name,
                timeout=self.time,
                )
            logging.info('The form was filled now solve the human authentication! ')
            # After human authentication click inquiry button and wait for the bot to take action again.
            time.sleep(20)
            try:
                page.locator('xpath=//td[@class="dxgvHeader"]')
                logging.info('Inquiry Page founded !')
                time.sleep(15)
            except Exception as e:
                logging.error(f'Unable to find  inquiry page: {e} ')
            for x in range(9,19):
                try:
                    detail_btn = page.locator(f'xpath=(//a)[position()={x}]')
                    await detail_btn.click()
                    logging.info('Clicked on details btn successfully')

                except Exception as e:
                    logging.error(f'There was an error finding or clicking detail link error: {e} ')    
                time.sleep(15)
            await browser.close()

async def main():
    business_name = input('Type the business name  ')
    bot = Bot(
        headless=False,
        business_name = business_name

    )
    await bot.run()            
asyncio.run(main())    
            
        
