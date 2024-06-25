from playwright.async_api import async_playwright
import asyncio
import logging
import pandas as pd

class Bot:
    def __init__(self, business_name, headless: bool):
        self.business_name = business_name
        self.url = 'https://ner.economy.ae/Search_By_BN.aspx'
        self.headless = headless
        self.data_list = []
        # Logging:
        logging.basicConfig(
            filemode='a',
            filename=f'{self.business_name}_data_logs.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%m/%d/%Y %H:%M:%S',
        )

    async def run(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(self.url)
            logging.info('The bot reached the site successfully')

            # Filling Form:
            await page.fill(
                'xpath=//input[@name="ctl00$MainContent$View_ucSearch_By_BN$cbpBreadCrumbOverAll_BAs$txtBNEnglish"]',
                self.business_name
            )
            logging.info('The form was filled; now solve the human authentication!')
            
            # Click inquiry button and wait for the bot to take action again.
            try:
                await page.wait_for_selector('xpath=//td[@class="dxgvHeader"]', timeout=150000)
                logging.info('Inquiry Page found!')
                total_pages = await page.locator('//td[@class="dxpPageNumber"][last()]').text_content()

            except Exception as e:
                logging.error(f'Unable to find inquiry page: {e}')
                return

            total_pages = int(total_pages)

            # Clicking Detail Buttons and extracting data:
            for p in range(1, total_pages + 1):
                logging.info(f'---------------------------------->On Page: {p} <-----------------------------')
                for x in range(9, 18):
                    try:
                        await page.wait_for_selector(f'xpath=(//a)[position()={x}]', timeout=30000)
                        detail_btn = page.locator(f'xpath=(//a)[position()={x}]')
                        detail_class = await detail_btn.get_attribute('class')
                        if detail_class:
                            logging.warning(f'This btn was disabled')
                            continue
                        
                        await detail_btn.click()
                        logging.info(f'Clicked on detail btn successfully: {x}')
                        
                        y = [a for a in range(11, 29)]
                        for i in y:
                            try:
                                await page.wait_for_selector(
                                    f'//input[@name="ctl00$MainContent$View_ucSearch_By_BN$popupBL_Detail$callbackPanel_BL_Detail$btnDetailOKExit"]',
                                    timeout=150000,
                                    )

                                data = {
                                    'CBLs No': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[0]}]').get_attribute('value'),
                                    'BL Local No': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[1]}]').get_attribute('value'),
                                    'Bussiness Name': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[3]}]').get_attribute('value'),
                                    'Legal Type': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[4]}]').get_attribute('value'),
                                    'Is Branch': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[5]}]').get_attribute('value'),
                                    'Parent BL NO': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[6]}]').get_attribute('value'),
                                    'ES.DATE': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[7]}]').get_attribute('value'),
                                    'Expiry Date': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[8]}]').get_attribute('value'),
                                    'BA Description': await page.locator(f'(//textarea)[position()=2]').text_content(),
                                    'Economic Department': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[9]}]').get_attribute('value'),
                                    'Registration ED Branch': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[10]}]').get_attribute('value'),
                                    'Mobile No': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[11]}]').get_attribute('value'),
                                    'Phone NO': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[12]}]').get_attribute('value'),
                                    'Status': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[13]}]').get_attribute('value'),
                                    'PO Box': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[14]}]').get_attribute('value'),
                                    'Email': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[15]}]').get_attribute('value'),
                                    'Website': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[16]}]').get_attribute('value'),
                                    'Full Address': await page.locator(f'(//input[@class="dxeEditArea dxeEditAreaSys"])[position()={y[17]}]').get_attribute('value')
                                }
                                logging.info(f'Found data: {data}')
                                self.data_list.append(data)
                            except Exception as e:
                                logging.error(f'Error in extracting data: {e}')
                                continue
                            finally:
                                await page.locator('//input[@name="ctl00$MainContent$View_ucSearch_By_BN$popupBL_Detail$callbackPanel_BL_Detail$btnDetailOKExit"]').click()
                    except Exception as e:
                        logging.error(f'Error finding or clicking detail link: {e}')
                        continue
                
                # Click next page button
                try:
                    await page.wait_for_selector('//td[@class="dxpButton"]', timeout=50000)
                    await page.locator('//td[@class="dxpButton"]').click()
                    logging.info('-------------------------> Moved to Next Page<-----------------------------')
                    await page.wait_for_selector('xpath=//td[@class="dxgvHeader"]', timeout=50000)
                except Exception as e:
                    logging.error(f'Error clicking next page button: {e}')
                    break

            await browser.close()

    def data_storing(self):
        df = pd.DataFrame(self.data_list)
        df.to_csv(f'{self.business_name}_data.csv', index=False,mode='a')
        logging.info('Data saved to data.csv')

async def main():
    business_name = input('Type the business name: ')
    bot = Bot(
        headless=False,
        business_name=business_name,
    )
    await bot.run()
    bot.data_storing()

asyncio.run(main())
