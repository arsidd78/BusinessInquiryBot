from playwright.async_api import async_playwright
import asyncio
import logging
import time
import pandas as pd

class Bot:
    def __init__(self,business_name,headless:bool,time=30000):
        self.business_name = business_name
        self.time = time
        self.url = 'https://ner.economy.ae/Search_By_BN.aspx'
        self.headless = headless
        self.data_list = []
        # Logging:
        logging.basicConfig(
            filemode='a',
            filename='bot_logs.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )

    async def run(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(self.url)
            logging.info(f'The bot reached to the site successfully')
            # Filling Form:
            await page.fill(
                'xpath=//input[@name="ctl00$MainContent$View_ucSearch_By_BN$cbpBreadCrumbOverAll_BAs$txtBNEnglish"]',
                self.business_name,
                timeout=self.time,
                )
            logging.info('The form was filled now solve the human authentication! ')
            # After human authentication click inquiry button and wait for the bot to take action again.
            try:
                await page.wait_for_selector('xpath=//td[@class="dxgvHeader"]',timeout= 50000)
                page.wait_for_selector('xpath=//td[@class="dxgvHeader"]',timeout= 50000)
                logging.info('Inquiry Page founded !')
            except Exception as e:
                logging.error(f'Unable to find  inquiry page: {e} ')
            for x in range(9,19):
                try:
                    detail_btn = page.locator(f'xpath=(//a)[position()={x}]')
                    await detail_btn.click()
                    logging.info('Clicked on details btn successfully',x)
                    y = [a for a in range(11,29)]
                    for _ in range(11,29):
                        try:
                            page.wait_for_selector(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[16]}]',timeout=50000)
                            cbls_no = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[0]}]').get_attribute('value')
                            logging.info(f'Found CBLs No: {cbls_no}{y[0]}')
                            bl_local_no = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[1]}]').get_attribute('value')
                            logging.info(f'Found BL Local No: {bl_local_no}{y[1]}')
                            business_name_english = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[3]}]').get_attribute('value')
                            logging.info(f'Found Business Name English: {business_name_english}')
                            legal_type = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[4]}]').get_attribute('value')
                            logging.info(f'Found Legal Type: {legal_type}')
                            branch = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[5]}]').get_attribute('value')
                            logging.info(f'Found Branch: {branch}')
                            parent_bl_no = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[6]}]').get_attribute('value')
                            logging.info(f'Found Parent BL No: {parent_bl_no}')
                            description = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[7]}]').text_content()
                            logging.info(f'Found Description: {description}')
                            economic_department = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[8]}]').get_attribute('value')
                            logging.info(f'Found Economic Department: {economic_department}')
                            registration_ed_branch = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[9]}]').get_attribute('value') 
                            logging.info(f'Found Registration Branch: {registration_ed_branch}')
                            mobile_no = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[10]}]').get_attribute('value')
                            logging.info(f' Found Mobile No: {mobile_no}')
                            phone_no = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[11]}]').get_attribute('value')
                            logging.info(f'Found Phone  No: {phone_no}')
                            status = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[12]}]').get_attribute('value')
                            logging.info(f'Found Status: {status}')
                            po_box = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[13]}]').get_attribute('value')
                            logging.info(f'Found PO Box: {po_box}')
                            email = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[14]}]').get_attribute('value')
                            logging.info(f'found Email: {email}')
                            website = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[15]}]').get_attribute('value')
                            logging.info(f'Found Website:{website}')  
                            full_address = await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[16]}]').get_attribute('value')
                            logging.info(f'Found Full Address: {full_address}')


                        except Exception as e:
                            logging.error(f'The Text content was not founded, Error: {e}')
                            continue
                        finally:
                            await page.locator('//td[@class="dxpcCloseButton"]').click()

                except Exception as e:
                    logging.error(f'There was an error finding or clicking detail link error: {e} ')    
                    continue
            await browser.close()

async def main():
    business_name = input('Type the business name  ')
    bot = Bot(
        headless=False,
        business_name = business_name

    )
    await bot.run()            
asyncio.run(main())    
            
        
