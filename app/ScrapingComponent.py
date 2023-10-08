from RPA.Browser.Selenium import Selenium, ChromeOptions
from ExcelComponent import Excel
from qrlib.QRComponent import QRComponent
from qrlib.QRUtils import display
import shutil
import os
import time
from Constants import Constant
from datetime import datetime, timedelta


# executable_path = os.path.join(os.environ['USERPROFILE'], 'chromedriver.exe')
executable_path = f'{os.getcwd()}\\chromedriver.exe'
display(f"ttttttttt{executable_path}")
SOA_PATH = os.path.join(os.getcwd(), 'output', "CURRENT_PHASE",'SOA Bank Names with ACC no.xlsx')
BANK_PATH = os.path.join(os.getcwd(), 'output', "CURRENT_PHASE",'Bank_statement.xlsx')
bank_folder = os.path.join(os.getcwd(), 'output', "BANK STMT PHASE 4")
soa_folder = os.path.join(os.getcwd(), 'output', "SOA STMT PHASE 4")

class Scraping_process(QRComponent):
    def __init__(self) -> None:
        self.browser = Selenium()
        
        download_dir = f'{os.getcwd()}\\output\\source'
        self.b = ChromeOptions()
        prefs = {
            'download.default_directory': download_dir
        }
        
        self.b.add_argument('--start-maximized')
        self.b.add_experimental_option('prefs', prefs)
        
        self.URL = 'https://adminonepg.nepalpayment.com/'
        self.URL_NIBL = 'https://www.nibl.com.np/intranet/Login.aspx'
        self.URL_RBB = 'https://smartbanking.rbb.com.np/#/login'
        self.URL_EMAIL = 'https://outlook.office365.com'
        self.SOA_data = Excel(SOA_PATH)
        self.BANK_data = Excel(BANK_PATH)



    def open_website(self):
        # self.browser.set_download_directory(directory= f'{os.getcwd()}\\output\\source')
        
        # option = "add_argument('--ignore-certificate-errors');add_argument('--start-maximized')"
        # option = f"add_argument('--download.default-directory={os.getcwd()}\\output\\source')"
        
        display(f'{os.getcwd()}\\output\\source')
        self.browser.open_browser(self.URL, browser='chrome',executable_path=executable_path, options=self.b)
        # time.sleep(100)
        # self.browser.open_available_browser(self.URL, browser_selection='Chrome', download=False, maximized=True)
        self.browser.wait_until_page_contains('Login')

    def sign_in(self):
        self.browser.input_text("//input[@id='user_name']",'kushal')
        self.browser.input_text("//input[@id='user_password']",'KuSh@LNp5')
        self.browser.input_text("//input[@id='access_code']",'KUH74')
        self.browser.click_button("//button[@type='submit']")

    def soa_stmt_scraping(self):
        try:
            # self.browser.set_download_directory(directory=soa_folder)
            self.browser.go_to("https://adminonepg.nepalpayment.com/MerchantBalanceSOA/SOA")
            
            self.browser.wait_until_element_is_visible('//legend[contains(text(), "Statement of Accounts")]', 60)
            for p in range(2):
                if p == 0:
                    self.browser.click_element_when_visible('//input[@id="FromDate"]')
                else:
                    self.browser.click_element_when_visible('//input[@id="ToDate"]')
                time.sleep(.25)
                today_day = str(self.browser.get_text('//td[contains(@class, "datepicker-today")]/a'))
                int_today = int(''.join([i for i in today_day if i.isnumeric()]))
                if int_today == 1:
                    self.browser.click_element_when_visible('//a[@data-handler="prev"]')
                    time.sleep(1)
                    tr_count = self.browser.get_element_count('//table[@class="ui-datepicker-calendar"]/tbody/tr')
                    td_count = self.browser.get_element_count(f'//table[@class="ui-datepicker-calendar"]/tbody/tr[{tr_count}]/td[@data-handler="selectDay"]')
                    self.browser.click_element_when_visible(f'//table[@class="ui-datepicker-calendar"]/tbody/tr[{tr_count}]/td[@data-handler="selectDay"][{td_count}]')
                else:
                    yesterday = int_today - 1
                    self.browser.click_element_when_visible(f'//td/a[text()="{yesterday}"]')
                    time.sleep(1)
            
            
            self.browser.click_element("//span[@role='combobox']/span[@id='select2-AccountType-container']")
            self.browser.input_text("//input[@class='select2-search__field']",'NPS Account')
            self.browser.press_keys(None, "RETURN")
            self.worksheet = self.SOA_data.read_excel()
            # print(f"soa-------->{self.worksheet}")
            for data in self.worksheet:
                try:
                    self.browser.click_element("//span[@id='select2-AccountId-container']")
                    # print(f"soa-------->{self.worksheet}")
                    # print('soa statement data ===>',data['Dispay Name'])
                    time.sleep(2)
                    self.browser.wait_until_element_is_visible("//input[@class='select2-search__field']")
                    self.browser.input_text("//input[@class='select2-search__field']",data['Dispay Name'])
                    self.browser.press_keys(None, "RETURN")
                    
                    self.browser.click_button("//button[@value ='CSV']")
                    time.sleep(5)
                    download_directory = os.path.join(os.getcwd(),'output','source')
                    files_in_directory = os.listdir(download_directory)
                    sorted_list = sorted(files_in_directory, key=lambda x: os.path.getctime(os.path.join(download_directory, x)))
                    sorted_list.reverse()

                # Rename the latest downloaded file
                    new_filename = f"Commission_{data['Dispay Name']}.csv"  # Replace with your desired new filename pattern
                    renamed_file = os.path.join(soa_folder, new_filename)
                    nps_commission_filepath = os.path.join(download_directory, sorted_list[0])
                    # display(f'nps commision report file path of {data["Dispay Name"]}  ===  {nps_commission_filepath}')
                    os.rename(nps_commission_filepath, renamed_file)

                    if "Commission" in renamed_file:
                        destination_path = os.path.join(soa_folder, renamed_file)
                        shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
                    elif "Bank" in renamed_file:
                        destination_path = os.path.join(bank_folder, renamed_file)
                        shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
                except Exception as e:
                    print(f'file not found ===\n {e}')
                    continue
        except Exception as e:
            print(f'Error in soa statement scraping ===\n {e}')  
        
       

    def bank_statement_scraping(self):
        try:
            self.browser.set_download_directory(directory=bank_folder)
            self.browser.go_to("https://adminonepg.nepalpayment.com/BankStatementView/Index")
            self.worksheet_bank = self.BANK_data.read_excel()
            print(f"bank statement from nps portal->{self.worksheet_bank}")
            
            self.browser.wait_until_element_is_visible('//legend[contains(text(),"Bank Statement View")]')
            for p in range(2):
                if p == 0:
                    self.browser.click_element_when_visible('//input[@id="FromDate"]')
                else:
                    self.browser.click_element_when_visible('//input[@id="ToDate"]')
                time.sleep(.25)
                today_day = str(self.browser.get_text('//td[contains(@class, "datepicker-today")]/a'))
                int_today = int(''.join([i for i in today_day if i.isnumeric()]))
                if int_today == 1:
                    self.browser.click_element_when_visible('//a[@data-handler="prev"]')
                    time.sleep(1)
                    tr_count = self.browser.get_element_count('//table[@class="ui-datepicker-calendar"]/tbody/tr')
                    td_count = self.browser.get_element_count(f'//table[@class="ui-datepicker-calendar"]/tbody/tr[{tr_count}]/td[@data-handler="selectDay"]')
                    self.browser.click_element_when_visible(f'//table[@class="ui-datepicker-calendar"]/tbody/tr[{tr_count}]/td[@data-handler="selectDay"][{td_count}]')
                else:
                    yesterday = int_today - 1
                    self.browser.click_element_when_visible(f'//td/a[text()="{yesterday}"]')
                    time.sleep(1)
            
            for bank_data in self.worksheet_bank:
                try:
                    # self.browser.click_element("//input[@id ='FromDate']")
                    # self.browser.click_element("//td[contains(@class,'datepicker-today')]")
                    # self.browser.click_element("//input[@id ='ToDate']")
                    # self.browser.click_element("//td[contains(@class,'datepicker-today')]")
                    
                    self.browser.click_element("//span[@id='select2-ddlInstrument-container']")
                    time.sleep(1)
                    self.browser.input_text("//input[@class='select2-search__field']",bank_data['Banks'])
                    time.sleep(1)
                    self.browser.press_keys(None, "RETURN")
                    self.browser.click_element("//input[@id='AccountNumber']")
                    
                    bank_acc_no = str(bank_data['Account_Number']).replace("'", "").strip()
                    
                    self.browser.input_text("//input[@id='AccountNumber']", bank_acc_no)
                    self.browser.click_button("//button[@type='submit']")
                    time.sleep(1)
                    self.browser.click_button("//button[contains(@class,'buttons-excel')]")
                    time.sleep(1)
                    
                    download_directory = f'{os.getcwd()}\\output\\source'
                    while True:
                        list = os.listdir(download_directory)
                        extension = list[0].endswith(".csv") or list[0].endswith(".xlsx")
                        if extension:
                            break
                        time.sleep(1)
                    files_in_directory = os.listdir(download_directory)
                    sorted_list = sorted(files_in_directory, key=lambda x: os.path.getctime(os.path.join(download_directory, x)))
                    sorted_list.reverse()

                    # Rename the latest downloaded file
                    new_filename = f"Bank_{bank_data['Banks']}.xlsx"  # Replace with your desired new filename pattern
                    renamed_file = os.path.join(bank_folder, new_filename)
                    os.rename(os.path.join(download_directory, sorted_list[0]), renamed_file)

                    if "Commission" in renamed_file:
                        destination_path = os.path.join(soa_folder, renamed_file)
                        shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
                    elif "Bank" in renamed_file:
                        destination_path = os.path.join(bank_folder, renamed_file)
                        shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)

                    
                except Exception as e:
                    print(f'file not found ===\n {e}')
                    continue
            self.browser.close_browser()
        except Exception as e:
                print(f'Error in bank statement scraping ==\n {e}')
        self.browser.close_browser()
        
    def open_website_of_NIBL(self):
        self.browser.set_download_directory(directory= f'{os.getcwd()}\\output\\source')
        self.browser.open_browser(self.URL_NIBL, browser='chrome',executable_path=executable_path, options=self.b)
        
        # self.browser.open_available_browser(self.URL_NIBL,maximized=True)

    def sign_in_NIBL(self):
        self.browser.wait_until_element_is_visible("//td[@class='rubrik']", 30)
        self.browser.input_text("//input[@id='txtUser']",'neps')
        self.browser.input_text("//input[@id='txtPwd']",'P2ym3ent@1')
        time.sleep(.5)
        self.browser.click_button("//input[@id='Button1']")
        
    def NIBL_bank_statement_scraping(self):
        try:
            self.browser.wait_until_element_is_visible("//a[normalize-space()='* Bank Statement']")
            self.browser.click_element_when_visible("//a[normalize-space()='* Bank Statement']")
            self.browser.wait_until_element_is_visible("//span[normalize-space()='Account Statement']")
            
            today_date = self.browser.get_element_attribute('//input[@id="ctl00_ContentPlaceHolder1_calStart_textBox"]', 'value')
            display(today_date)
            just_day_arr = str(today_date).split('/')
            just_day = just_day_arr[1]
            display(just_day)
            
            for a in range(2):
                if a == 0:
                    self.browser.click_element_when_visible('//input[@id="ctl00_ContentPlaceHolder1_calStart_button"]')
                else:
                    self.browser.click_element_when_visible('//input[@id="ctl00_ContentPlaceHolder1_calEnd_button"]')
                time.sleep(1)
                if int(just_day) == 1:
                    self.browser.click_element_when_visible('//span[text()="<"]')
                    rows = self.browser.get_element_count('//div[@id="ctl00_ContentPlaceHolder1_calStart_calendar"]//tbody/tr')
                    # horizons = self.browser.get_element_count(f'//div[@id="ctl00_ContentPlaceHolder1_calStart_calendar"]//tbody/tr[{rows}]/td')
                    horizon_elements = self.browser.get_webelements(f'//div[@id="ctl00_ContentPlaceHolder1_calStart_calendar"]//tbody/tr[{rows}]/td')
                    num_arr = []
                    for horizon in horizon_elements:
                        num = self.browser.get_text(horizon)
                        num_arr.append(num)
                    max_day = max(num_arr)
                    self.browser.click_element_when_visible(f'//div[@id="ctl00_ContentPlaceHolder1_calStart_calendar"]//tbody/tr[{rows}]/td[text()="{max_day}"]')
                elif int(just_day)>20:
                    yesterday = int(just_day) - 1
                    day_elements = self.browser.get_webelements(f'//td[text()="{yesterday}"]')
                    display(day_elements)
                    self.browser.click_element_when_visible(day_elements[-1])
                    
                else:
                    yesterday = int(just_day) - 1
                    day_elements = self.browser.get_webelements(f'//td[text()="{yesterday}"]')
                    self.browser.click_element_when_visible(day_elements[0])
                time.sleep(2)
                    
            self.browser.click_element("//input[@id='ctl00_ContentPlaceHolder1_Button1']")#click on view button
            self.browser.click_element("//input[@id='ctl00_ContentPlaceHolder1_btnExport']")#clcikc on export button
            time.sleep(2)
            download_directory = f'{os.getcwd()}\\output\\source'
            while True:
                bank_list = os.listdir(download_directory)
                extension = bank_list[0].endswith(".csv") or bank_list[0].endswith(".xlsx") or bank_list[0].endswith(".xls")
                if extension:
                    break
                time.sleep(1)
            files_in_directory = os.listdir(download_directory)
            sorted_list = sorted(files_in_directory, key=lambda x: os.path.getctime(os.path.join(download_directory, x)))
            sorted_list.reverse()

            # Rename the latest downloaded file
            new_filename = f"Bank_NIBL.xls"  # Replace with your desired new filename pattern
            renamed_file = os.path.join(bank_folder, new_filename)
            time.sleep(5)
            os.rename(os.path.join(download_directory, sorted_list[0]), renamed_file)
            if "Commission" in renamed_file:
                destination_path = os.path.join(soa_folder, renamed_file)
                shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
            elif "Bank" in renamed_file:
                destination_path = os.path.join(bank_folder, renamed_file)
                shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
            self.browser.close_browser()
        except Exception as e:
            print(f'Error in NIBL scraping===\n {e}')
            self.browser.close_browser()
            
    def open_website_of_RBB(self):
        self.browser.set_download_directory(directory= f'{os.getcwd()}\\output\\source')
        
        self.browser.open_browser(self.URL_RBB, browser='chrome',executable_path=executable_path, options=self.b)

        # self.browser.open_available_browser(self.URL_RBB,maximized=True)

    def sign_in_RBB(self):
        self.browser.wait_until_element_is_visible("//div[@class='login-panel-header']", 60)
        time.sleep(5)
        self.browser.input_text("//input[@id='username']",'NPAY49')
        self.browser.input_text("//input[@id='password']",'Rbbnps@1122#')
        self.browser.click_button("//button[@type='submit']")
        
    def RBB_bank_statement_scraping(self):
        try:
            self.browser.wait_until_element_is_visible("//span[normalize-space()='Switch Account']",timeout=60)
            self.browser.click_element("//i[@class='main-nav-icon account']")
            # self.browser.go_to("https://smartbanking.rbb.com.np/#/account")
            self.browser.wait_until_element_is_visible("//button//span[text()='Statement']", timeout=5*60)
            self.browser.click_element_when_visible("//button//span[text()='Statement']")
            
            self.browser.wait_until_element_is_visible('//input[@id="fromDateId"]', 60*5)
            
            
            from_date = str(datetime.today()).split()[0].replace('-', '/')
            today_dt = datetime.strptime(from_date, '%Y/%m/%d')
            yesterday_date = today_dt - timedelta(days=1)
            yesterday_str = yesterday_date.strftime("%Y/%m/%d")
            
            self.browser.input_text('//input[@id="fromDateId"]', yesterday_str, clear=True)
            self.browser.input_text('//input[@id="toDateId"]', yesterday_str, clear=True)
            self.browser.click_element_when_visible('//label[@for="toDate"]')
            
            time.sleep(2)
            self.browser.click_element_when_visible('//button[text()="Show"]')
            time.sleep(2)
            self.browser.wait_until_element_is_visible('//div[text()="Opening Balance"]', 60 *5)
            
            self.browser.wait_until_element_is_visible('''//button[@ng-click="accountStatementCtrl.downloadAccountStatement('EXCEL')"]''', timeout=60 * 5)
            self.browser.click_element_when_visible('''//button[@ng-click="accountStatementCtrl.downloadAccountStatement('EXCEL')"]''')
            time.sleep(2)
            download_directory = f'{os.getcwd()}\\output\\source'
            while True:
                file_list = os.listdir(download_directory)
                if len(file_list)==0:
                    continue
                extension = file_list[0].endswith(".csv") or file_list[0].endswith(".xlsx") or file_list[0].endswith(".xls")
                if extension:
                    break
                time.sleep(1)
            files_in_directory = os.listdir(download_directory)
            sorted_list = sorted(files_in_directory, key=lambda x: os.path.getctime(os.path.join(download_directory, x)))
            sorted_list.reverse()

            # Rename the latest downloaded file
            new_filename = f"Bank_RBB.xls"  # Replace with your desired new filename pattern
            renamed_file = os.path.join(bank_folder, new_filename)
            os.rename(os.path.join(download_directory, sorted_list[0]), renamed_file)

            if "Commission" in renamed_file:
                destination_path = os.path.join(soa_folder, renamed_file)
                shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
            elif "Bank" in renamed_file:
                destination_path = os.path.join(bank_folder, renamed_file)
                shutil.move(os.path.join(f'{os.getcwd()}\\output\\source', renamed_file), destination_path)
            self.browser.close_browser()
        except Exception as e:
            print(f'Error in RBB scraping  ===\n {e}')
            self.browser.close_browser()

    def open_website_of_OUTLOOK_EMAIL(self):
        self.browser.set_download_directory(directory= f'{os.getcwd()}\\output\\BANK STMT PHASE 4')
        
        options = ChromeOptions()
        prefs = {
            'download.default_directory': f'{os.getcwd()}\\output\\BANK STMT PHASE 4'
        }
        
        options.add_argument('--start-maximized')
        options.add_experimental_option('prefs', prefs)
        self.browser.open_browser(self.URL_EMAIL, browser='chrome',executable_path=executable_path, options=options)
        
        # self.browser.open_available_browser(self.URL_EMAIL,maximized=True)
        self.browser.wait_until_element_is_visible("//div[@class='background-logo-holder']",timeout=60*5)


    def sign_in_to_Outlook_Email(self):
        # insert username and click
        self.browser.wait_until_element_is_visible(Constant.uname_xpath, 30)
        self.browser.input_text(Constant.uname_xpath, Constant.username)
        self.browser.click_element_when_visible(Constant.signin_xpath)
        # insert password and click
        self.browser.wait_until_element_is_visible(Constant.password_xpath, 30)
        self.browser.input_text(Constant.password_xpath, Constant.password)
        self.browser.click_element_when_visible(Constant.pass_button_xpath)
        # confirm click
        self.browser.wait_until_element_is_visible(Constant.final_signin_xpath, 30)
        self.browser.click_element_when_visible(Constant.final_signin_xpath)
        self.browser.wait_until_element_is_visible(Constant.filter_xpath,timeout=15)
        # time.sleep(5)
    
    def bank_statement_scraping_through_email(self):
        try:
            # filter click
            
            self.browser.click_element_when_visible(Constant.filter_xpath)
            # self.browser.wait_until_page_contains_element(Constant.has_att_xpath,timeout=30)
            self.browser.wait_until_element_is_visible(Constant.has_att_xpath, 30)
            # filter attachment
            self.browser.click_element_when_visible(Constant.has_att_xpath)
            time.sleep(5)
            emails_els = self.browser.get_webelements(Constant.email_xpath)
            display(emails_els)
            print(f"list of email  {emails_els}")
            for emails in emails_els:
                try:
                    
                    self.browser.click_element_when_visible(Constant.xpathforfirstemail)
                    time.sleep(5)
                    self.browser.wait_until_element_is_visible(Constant.option_xpath,timeout=30)
                    self.browser.click_element_when_clickable(Constant.option_xpath)
                    # self.browser.click_element(Constant.option_xpath)
                    time.sleep(5)
                    self.browser.wait_until_element_is_visible(Constant.download_xpath,timeout=30)
                    self.browser.click_element_when_visible(Constant.download_xpath)
                    time.sleep(5)
                    self.browser.click_element_when_visible(Constant.read_unread_path)#mark as read
                    time.sleep(3)
                except Exception as e:
                    # Handle exceptions and continue processing other emails
                    print(f"Error processing email: {str(e)}")
                    continue
            self.browser.close_browser()
        except Exception as e:
            print(f'Error in Email Scraping ===\n {e}')
            self.browser.close_browser()



   