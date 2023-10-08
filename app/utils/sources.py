from app.banks.Sanima import SanimaBank
from app.banks.Everest import EverestBank
from app.banks.NIBL import NIBLBank
from app.banks.Siddhartha import SiddharthaBank
# from app.banks.Ncc import NCCBank
from app.banks.Rbb import RBBBank
from app.banks.ADBL import ADBLBank
from app.banks.NICAsia import NICAsiaBank
from app.banks.Shangrilla import ShangrillaBank
# from app.banks.CivilBank import CivilBank
# from app.banks.MegaBank import MegaBank
from app.banks.Kumari import KumariBank
from app.banks.Laxmi import LaxmiBank
from app.banks.Global import GlobalBank
from app.banks.Citizen import CitizenBank
# from app.banks.Saptakoshi import SaptaKoshiBank
# from app.banks.Sunrise import SunriseBank
from app.banks.jyotibikash import JyotiBikashBank
from app.banks.NepalBank import NepalBank
from app.banks.Kamana import KamanaBank
# from app.banks.Century import CenturyBank
from app.banks.PrabhuBank import PrabhuBank
from app.banks.Mbl import MblBank
from app.banks.ICFC import ICFC
from app.banks.Nabil import NabilBank
from app.banks.Prime import PrimeBank
from app.banks.Muktinath import MuktiNathBank
from app.banks.Lumbini import LumbiniBank
from app.banks.Green import GreenBank
from app.banks.Manjushree import ManjuShreeBank
from app.banks.NepalFinance import NepalFinance
from app.banks.Sindhubikash import SindhubikashBank
from app.banks.Miteri import MiteriBank
from app.banks.Excelbank import ExcelBank
from app.banks.BestFinance import BestFinance
from app.banks.Garima import GarimaBank
from app.banks.Mahalaxmi import MahaLaxmi
from app.banks.NMB import NMBBank
'''
Comment all sources except for the bank that you are about to reconcile.
Ucomment all sources while pushing into the branch or requesting a pull request.
'''
sourcess = [
        {
            "name":"ManjuShreeBank",
            "instance":ManjuShreeBank # NP
        }
]

sources = [
        {
            "name":"MahaLaxmiBank",
            "instance":MahaLaxmi #no b
        },
        {
            "name":"GarimaBank",
            "instance":GarimaBank #no b
        },
          {
            "name":"Sindhubikash",
            "instance":SindhubikashBank #no b
        },
        {
            "name":"Miteribank",
            "instance":MiteriBank #no b
        },
        {
            "name":"excelBank",
            "instance":ExcelBank  #no b
        },
        {
            "name":"NepalFinance",
            "instance":NepalFinance #NP
        },
        {
            "name":"ManjuShreeBank",
            "instance":ManjuShreeBank # NP
        },
        {
            "name":"GreenBank",
            "instance":GreenBank # nothing
        },
        {
            "name":"LumbiniBank",
            "instance":LumbiniBank #NP
        },
        {
            "name":"MuktiNathBank",
            "instance":MuktiNathBank #no b
        },
        {
            'name':'nabil',
            'instance':NabilBank #NP
        },
        {
            'name':'prime',
            'instance':PrimeBank #NP
        },
        {
            'name':'ICFC',
            'instance':ICFC #NP
        },
        {
            "name":"laxmibank",
            "instance":LaxmiBank #NP
        },
        {
            "name":"shangrilla",
            "instance":ShangrillaBank #NP
        },
        {
            "name":"nicasia",
            "instance":NICAsiaBank #NM
        },
        {
            "name":"sanima",
            "instance":SanimaBank #NP
        },
        {
            "name":"everest",
            "instance":EverestBank #P
        },
        {
            "name":"siddhartha",
            "instance":SiddharthaBank #NP
        },
         {
            "name":"adbl",
            "instance":ADBLBank # no b
        },
        {
            "name":"global",
            "instance":GlobalBank #NP
        },
        {
            "name":"rbb",
            "instance":RBBBank #NP  
        },
        # {
        #     "name":"saptakoshi",
        #     "instance":SaptaKoshiBank
        # },
        # {
        #     "name":"sunrise",
        #     "instance":SunriseBank
        # },
        {
            "name":"jyotibikash",
            "instance":JyotiBikashBank #NP
        },
        # {
        #     "name":"century",
        #     "instance":CenturyBank
        # },
        {
            "name":"prabhubank",
            "instance":PrabhuBank #NP
        },
        {
            "name":"niblbank",
            "instance":NIBLBank # p
        },
        # {
        #     "name":"megabank",
        #     "instance":MegaBank
        # },
        # {
        #     "name":"nccbank",
        #     "instance":NCCBank
        # },
         {
            "name":"kamanabank",
            "instance":KamanaBank #NP
        },
        # {
        #     "name":"civilbank",
        #     "instance":CivilBank
        # },
        {
            "name":"kumari",
            "instance":KumariBank #NP
        },
        {
            "name":"citizen",
            "instance":CitizenBank #NP
        },
        {
            "name":"nepalbank",
            "instance":NepalBank
        },
        {
            "name":"mblbank",
            "instance":MblBank
        },
        {
            "name":"bestfinance",
            "instance":BestFinance 
        },
        {
            "name":"NMBbank",
            "instance":NMBBank #NP
        }
]
