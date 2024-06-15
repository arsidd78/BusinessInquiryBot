from playwright.async_api import async_playwright
import asyncio
import logging
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

    async def run(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(self.url)
            await page.fill(
                'xpath=//input[@name="ctl00$MainContent$View_ucSearch_By_BN$cbpBreadCrumbOverAll_BAs$txtBNEnglish"]',
                self.business_name,
                timeout=self.time,
                )
            
        
