import requests
import os

from dotenv import load_dotenv


load_dotenv()

LINK_ODATA = "https://my431112.businessbydesign.cloud.sap/sap/byd/odata/ana_businessanalytics_analytics.svc/RPSCMINVV02_Q0001QueryResults?$select=CLAST_PUTAWAY_DT,CMATERIAL_UUID,TMATERIAL_UUID,CSITE_UUID,TSITE_UUID,C1ISTOCK_UUIDsISTOCK_ID,TON_HAND_STOCK_UOM,KCON_HAND_STOCK&$filter=(CSITE_UUID eq '{}') and (CPROD_CAT_UUID eq 'PVCVIDRIOS') and (CLOG_AREA_UUID eq '{}/{}-1' or CLOG_AREA_UUID eq '{}/{}-L')&$top=999999&$format=json&sap-language=ES"

def get_labels(branch_code: str):
    odata_user = os.getenv('USER_ODATA')
    odata_pass = os.getenv('PASS_ODATA')

    # 5 placeholders: CSITE_UUID(1) + CLOG_AREA_UUID-1(2) + CLOG_AREA_UUID-L(2)
    odata_link = LINK_ODATA.format(branch_code, branch_code, branch_code, branch_code, branch_code)
    print(odata_link)
    
    request = requests.get(
            url=odata_link,
            auth=(odata_user, odata_pass)
        )
    
    result = request.json()
    return result['d']['results']