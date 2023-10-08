# from utils.Utils import run_phase
import os
from datetime import datetime, timedelta

class Phase_Constants:
    CURRENT_PHASE_NUMBER = 4
    PHASE1 = 1
    PHASE2 = 2
    PHASE3 = 3
    PHASE4 = 4


class FolderPath():
    Folder_Home_Path = os.path.join(os.getcwd(), '../')
    Bank_Folder = os.path.join(Folder_Home_Path, 'BANK STATEMENT REPORT FOR RECONCILE Phase1')
    SOA_Folder = os.path.join(Folder_Home_Path, 'SOA REPORT FOR RECONCILE Phase1')
    # LWT_Folder = os.path.join(Folder_Home_Path, 'LOAD WALLET FOR RECONCILE Phase1')
    # FT_Folder = os.path.join(Folder_Home_Path, 'Merchant Bank for Fund Transfer')

    if Phase_Constants.CURRENT_PHASE_NUMBER==Phase_Constants.PHASE4:
        Folder_Home_Path = os.path.join(os.getcwd(), 'output')
        Bank_Folder = os.path.join(Folder_Home_Path, 'BANK STMT PHASE 4')
        SOA_Folder = os.path.join(Folder_Home_Path, 'SOA STMT PHASE 4')

        if not os.path.exists(Bank_Folder):
            os.mkdir(Bank_Folder)
        elif not os.path.exists(SOA_Folder):
            os.mkdir(SOA_Folder)
        # elif not os.path.exists(LWT_Folder):
        #     os.mkdir(LWT_Folder)
        # elif not os.path.exists(FT_Folder):
        #     os.mkdir(FT_Folder)


class Banks_FILEPATH():
    PRABHU_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Prabhu Bank 22-11-2020 to 16-07-2021.xlsb')
    RBB_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'RBB 12-04-2021 to 15-07-2021.xlsx')
    SAPTA_KOSHI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Saptakoshi.xlsx')
    CIVIL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'civil bank.xls')
    EVEREST_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Everest Bank Statemtent(15th July 2020-17th July 2021).xlsx')
    SIDDHARTHA_BANK_FILE= os.path.join(FolderPath.Bank_Folder, 'Siddhartha bank.xlsx')
    ADBL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'ADBL 16-07-2020 to 15-07-2021.xlsx')
    JYOTI_BIKASH_BANK= os.path.join(FolderPath.Bank_Folder, 'Jyoti Bikash Bank 16-07-2020 to 15-07-2021.xlsx')
    SHANGRILLA_BANK_FILE =os.path.join(FolderPath.Bank_Folder, 'NPS RECEIVABLE -STATEMENT Shangrilla.xlsx')
    MEGA_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Mega Bank 16-07-2020 to 15-07-2021.xls")
    SUNRISE_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Sunrise bank 15-07-2020 to 15-07-2021.xlsx')
    CENTURY_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Century Bank 12-11-2020 to 15-07-2021.xlsx')
    NCC_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "NCC 25-08-2020 to 14-01-2022.xlsx")
    CITIZEN_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "citizens 15-09-2020 to 15-07-2021.xlsx")
    NIBL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "NIBL Account 16-07-2020 to 15-07-2021.xlsx")
    NICAsia_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "NIC 15-07-2020 to 15-07-2021.xlsx")
    KAMANA_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "STATEMENT OF Kamana.xlsx")
    KUMARI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "kumari bank 31-08-2020 to 15-07-2021.xlsx")
    LAXMI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Laxmi Bank 09-09-2020 to 15-07-2021.xls')
    NEPAL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Nepal Bank 20-10-2020 to 03-06-2021.xlsx")
    SANIMA_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Sanima bank 31-10-2020 to 01-04-2021.xlsx")
    MBL_BANK_FILE =  os.path.join(FolderPath.Bank_Folder, "mbl 16-07-2020 to 21-03-2022.xlsx")
    GLOBAL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "global ime 15-07-2020 to 16-07-2021.xlsx")
    ICFC_BANK_FILE = ''
    NABIL_BANK_FILE = ''

    if Phase_Constants.CURRENT_PHASE_NUMBER==Phase_Constants.PHASE4:
        LAXMI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Laxmi Bank.xlsx')
        NIBL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Bank_NIBL.xls")
        
        
        KAMANA_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"Bank_Kamana Sewa Bikas.xlsx")
        ICFC_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_ICFC.xlsx')
        PRABHU_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"Bank_Prabhu Bank.xlsx")
        NICAsia_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_NIC ASIA BANK.xlsx')
        GLOBAL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Bank_Global IME Bank.xlsx")
        PRIME_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Bank_Prime Commercial Bank Ltd.xlsx")
        JYOTI_BIKASH_BANK = os.path.join(FolderPath.Bank_Folder, 'Bank_Jyoti Bikash.xlsx')
        SHANGRILLA_BANK_FILE =os.path.join(FolderPath.Bank_Folder,'Bank_Shangrila Development Bank.xlsx')
        NABIL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Nabil Bank.xlsx')
        SANIMA_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Bank_Sanima Bank.xlsx")
        MUKTINATH_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"Bank_muktinath.xlsx")
        NEPAL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Bank_Nepal Bank Limited.xlsx")
        CITIZEN_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"Bank_Citizens Bank.xlsx")
        LUMBINI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Lumbini Bikas Bank.xlsx')
        GREEN_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Green.xlsx')
        ManjuShree_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Manjushree Finance Limited.xlsx')
        MBL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Machhapuchchhre Bank.xlsx')
        SIDDHARTHA_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Siddhartha Bank.xlsx')
        EVEREST_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Everest Bank.xlsx')
        RBB_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Bank_RBB.xls')
        SINDHUBIKASH_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Sindhubikash.xlsx')
        EXCEL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_excel.xlsx')
        ADBL_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Bank_Agriculture.xlsx')
        GARIMA_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Bank_Garima.xlsx')
        NEPAL_FINANCE_FILE = os.path.join(FolderPath.Bank_Folder,'Bank_Nepal_Finance.xlsx')
        MITERI_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Bank_miteri.xlsx')
        KUMARI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Bank_Kumari Bank.xlsx")
        BESTFINANCE_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Best Finance.xlsx')
        MAHALAXMI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_Mahalaxmi.xlsx')
        NMB_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Bank_NMB Bank.xlsx')
        # RBB_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'RBB 12-04-2021 to 15-07-2021.xlsx')
        # SAPTA_KOSHI_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Saptakoshi.xlsx')
        # CIVIL_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'civil bank.xls')
        # EVEREST_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Everest Bank Statemtent(15th July 2020-17th July 2021).xlsx')
        # SIDDHARTHA_BANK_FILE= os.path.join(FolderPath.Bank_Folder,'Siddhartha bank.xlsx')
        # JYOTI_BIKASH_BANK= os.path.join(FolderPath.Bank_Folder,'Jyoti Bikash Bank 16-07-2020 to 15-07-2021.xlsx')
        # MEGA_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Mega Bank 16-07-2020 to 15-07-2021.xls")
        # SUNRISE_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Sunrise bank 15-07-2020 to 15-07-2021.xlsx')
        # CENTURY_BANK_FILE = os.path.join(FolderPath.Bank_Folder, 'Century Bank 12-11-2020 to 15-07-2021.xlsx')
        # NCC_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"NCC 25-08-2020 to 14-01-2022.xlsx")
        # NIBL_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"NIBL Account 16-07-2020 to 15-07-2021.xlsx")
        # NICAsia_BANK_FILE = os.path.join(FolderPath.Bank_Folder,"NIC 15-07-2020 to 15-07-2021.xlsx")
        # KUMARI_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "kumari bank 31-08-2020 to 15-07-2021.xlsx")
        # LAXMI_BANK_FILE = os.path.join(FolderPath.Bank_Folder,'Laxmi Bank 09-09-2020 to 15-07-2021.xls')
        # NEPAL_BANK_FILE = os.path.join(FolderPath.Bank_Folder, "Nepal Bank 20-10-2020 to 03-06-2021.xlsx")
        # MBL_BANK_FILE =  os.path.join(FolderPath.Bank_Folder, "mbl 16-07-2020 to 21-03-2022.xlsx")
    

class SOA_FILEPATH():
    EVEREST_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (05_29_2021 to 07_17_2021)Everest Bank.csv")
    SIDDHARTHA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (07_15_2021 to 07_18_2021)SiddarthaBank.csv")
    PRABHU_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (11_22_2020 to 04_11_2021)PrabhuBank.csv")
    RBB_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (04_21_2021 to 07_15_2021)RBB Bank.csv")
    SAPTA_KOSHI_SOA = os.path.join(FolderPath.SOA_Folder,"Commission Report (04_29_2021 to 06_03_2022)Saptakoshi Bank.csv")
    CIVIL_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (05_24_2021 to 07_15_2021)Civil Bank.csv")
    ADBL_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (07_16_2020 to 07_15_2021)ADBL.csv")
    JYOTI_BIKASH_SOA_FILE= os.path.join(FolderPath.SOA_Folder,"Commission Report (09_21_2020 to 07_15_2021)Jyoti Bank.csv")
    SHANGRILLA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (05_14_2021 to 07_17_2021)Shangrilla Bank.csv")
    SUNRISE_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (04_06_2021 to 07_15_2021)Sunrise Bank.csv")
    MEGA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (08_25_2020 to 07_15_2021)Mega Bank.csv")
    KAMANA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (12_25_2020 to 07_17_2021)Kamana Bank.csv")
    CENTURY_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission Report (11_12_2020 to 07_15_2021)Century Bank.csv')
    NCC_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (08_25_2020 to 01_14_2022) NCC bank.csv")
    CITIZEN_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Citizen Bank Commission Report (09_15_2020 to 07_15_2021)Citizen Bank.csv")
    NIBL_SOA_FILE =  os.path.join(FolderPath.SOA_Folder,"Commission Report (02_28_2021 to 07_17_2021)NIBL Bank.csv")
    NICAsia_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (01_06_2021 to 07_15_2021)NIC ASIA.csv")
    KUMARI_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission Report (08_31_2020 to 07_15_2021) Kumari Bank.csv")
    Laxmi_SOA_FILE = os.path.join(FolderPath.SOA_Folder,'Laxmi SOA.csv')
    NEPALBANK_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Nepal Bank 11_01_2020 to 07_12_2021).csv")
    SANIMA_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Sanima New 11-21-2020 to 7-16-2021.csv")
    MBL_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission Report (04_30_2021 to 03_21_2022)Machhapuchre Bank.csv")
    GLOBAL_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission Report (09_04_2020 to 07_16_2021)Global Bank.csv")
    ICFC_SOA_FILE = ''
    NABIL_SOA_FILE = ''

    if Phase_Constants.CURRENT_PHASE_NUMBER==Phase_Constants.PHASE4:
        Laxmi_SOA_FILE = os.path.join(FolderPath.SOA_Folder,'Commission_Laxmi Sunrise Settlement Account.csv')
        NIBL_SOA_FILE =  os.path.join(FolderPath.SOA_Folder,"Commission_NPS Settlement Account - NIBL.csv")
        
        KAMANA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_KAMANA(NEPAL PAYMENT PAYABLE).csv")
        ICFC_SOA_FILE = os.path.join(FolderPath.SOA_Folder,'Commission_ICFC - NEPAL PAYMENT SOLUTION RECEIVABLE PAYABLE.csv')
        PRABHU_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_NPS Settlement Account - Prabhu Bank.csv")
        NICAsia_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_NIC (NPS Receivable.csv")
        GLOBAL_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_Global Bank(NPS Settlement Account).csv")
        JYOTI_BIKASH_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_NPS Settlement Account -Jyoti Bikash Bank.csv')
        SHANGRILLA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_Shangrila - NPS RECEIVABLE.csv")
        PRIME_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_Prime Bank Rx.csv")
        NABIL_SOA_FILE = os.path.join(FolderPath.SOA_Folder,'Commission_Nabil Bank Settlement Account.csv')
        SANIMA_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_NPS Settlement Account - Sanima Bank.csv")
        MUKTINATH_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_Muktinath - NPS SETTLEMENT ACCOUNT.csv")
        NEPALBANK_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_NPS Settlement Account - Nepal Bank.csv")
        CITIZEN_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_Citizens(NPS Settlement Account).csv")
        LUMBINI_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Lumbini Bikas Bank Ltd Rx.csv')
        GREEN_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_N P SOLUTION PAYABLE-Green Dev.csv')
        MANJUSHREE_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Manjushree Finance RX.csv')
        MBL_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Machhapuchhre(NPS SETTLEMENT ACCOUNT-DBD).csv')
        SIDDHARTHA_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Everest Bank(NEPAL PAYMENT PAYABLE.csv')
        EVEREST_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Everest Bank(NEPAL PAYMENT PAYABLE.csv')
        GARIMA_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Garima Bikas Bank Rx.csv')
        NEPALFINANCE_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Nepal Finance NPS Settlement AC.csv')
        SINDHUBIKASH_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_SINDHU Bikash Bank NP PMT SOLUTION PVT AC PAYABLE.csv')
        EXCEL_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Excel Development Bank - NPS Account.csv')
        MITERI_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Miteri Development Bank NPS Acc.csv')
        BESTFINANCE_SOA_FILE = os.path.join(FolderPath.SOA_Folder, 'Commission_Best Finance- NPS SETTLEMENT.csv')
        KUMARI_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_NPS Settlement Account - Kumari Bank.csv")
        MAHALAXMI_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_Mahalaxmi Bikas Bank.csv")
        # EVEREST_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (05_29_2021 to 07_17_2021)Everest Bank.csv")
        # SIDDHARTHA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (07_15_2021 to 07_18_2021)SiddarthaBank.csv")
        RBB_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_RBB-Rx.csv")
        # SAPTA_KOSHI_SOA = os.path.join(FolderPath.SOA_Folder,"Commission Report (04_29_2021 to 06_03_2022)Saptakoshi Bank.csv")
        # CIVIL_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (05_24_2021 to 07_15_2021)Civil Bank.csv")
        ADBL_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission_NPS Settlement Account- ADBL.csv")
        NMB_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission_NPS Settlement Account - NMB Bank.csv")
        # JYOTI_BIKASH_SOA_FILE= os.path.join(FolderPath.SOA_Folder,"Commission Report (09_21_2020 to 07_15_2021)Jyoti Bank.csv")
        # SUNRISE_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (04_06_2021 to 07_15_2021)Sunrise Bank.csv")
        # MEGA_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (08_25_2020 to 07_15_2021)Mega Bank.csv")
        # CENTURY_SOA_FILE = os.path.join(FolderPath.SOA_Folder,'Commission Report (11_12_2020 to 07_15_2021)Century Bank.csv')
        # NCC_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (08_25_2020 to 01_14_2022) NCC bank.csv")
        # NIBL_SOA_FILE =  os.path.join(FolderPath.SOA_Folder,"Commission Report (02_28_2021 to 07_17_2021)NIBL Bank.csv")
        # NICAsia_SOA_FILE = os.path.join(FolderPath.SOA_Folder,"Commission Report (01_06_2021 to 07_15_2021)NIC ASIA.csv")
        # KUMARI_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission Report (08_31_2020 to 07_15_2021) Kumari Bank.csv")
        # Laxmi_SOA_FILE = os.path.join(FolderPath.SOA_Folder,'Laxmi SOA.csv')
        # MBL_SOA_FILE = os.path.join(FolderPath.SOA_Folder, "Commission Report (04_30_2021 to 03_21_2022)Machhapuchre Bank.csv")

# class PHASE1_LWT_FILEPATH():
#     LWT_FILE = os.path.join(FolderPath.LWT_Folder,"Load Wallet Data Till Date.xlsx")
    
# class PHASE1_FT_FILEPATH():
#     LAXMI_FT_FILE = os.path.join(FolderPath.FT_Folder, 'Fund Transfer Report (2023-08-20 16_13_02)Laxmi Bank.csv')
#     GLOBAL_FT_FILE = os.path.join(FolderPath.FT_Folder, 'Fund Transfer Report (2023-08-20 16_48_29)Global Bank.csv')

class PHASE_1RECONCILIATION_REPORT():
    today_date = str(datetime.today() - timedelta(days=1)).split()[0]
    yesterday_date = today_date.replace("-", "_")
    
    RECONCILIATION_UnMatched_REPORT_PATH = os.path.join('output',f"Reconciliation_Unmatched_report_{yesterday_date}.xlsx")
    RECONCILIATION_Matched_REPORT_PATH = os.path.join('output',f"Reconciliation_Matched_report_{yesterday_date}.xlsx")


class Constant:
    link = 'https://outlook.office365.com'
    username = 'reconciliation@nepalpayment.com'
    password = 'x3Ww68b.xDv;42n#'

    #signin path
    signin_xpath ='//input[@id="idSIButton9"]'
    uname_xpath ='//input[@name="loginfmt"]'
    
    #password xpath
    password_xpath ='//input[@name="passwd"]'
    pass_button_xpath='//input[@id="idSIButton9"]'

    final_signin_xpath ='//input[@id="idSIButton9"]'

    filter_xpath = '//div[contains(text(), "Filter")]'
    has_att_xpath = '//li[2]'

#  email_xpath = '//div[@class="EeHm8"]/div'
    email_xpath = '//div[contains(@class, "customScrollBar")]//div[contains(@class, "customScrollBar")]//div[contains(@class, "customScrollBar")]//div[contains(@aria-label, "attachment")]'

    xpathforfirstemail = f'({email_xpath})[1]'

    option_xpath ='//button[@aria-label="More actions"]'
    download_xpath ='//button[@name="Download"]'

    read_unread_path = "//button/span/span[contains(text(), 'Read / Unread')][1]"