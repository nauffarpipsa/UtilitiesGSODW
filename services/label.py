import requests
import os

from dotenv import load_dotenv


load_dotenv()

def get_labels(branch_code: str):
    odata_env = os.getenv('LINK_ODATA')
    odata_user = os.getenv('USER_ODATA')
    odata_pass = os.getenv('PASS_ODATA')

    odata_link = odata_env.format(branch_code)
    
    request = requests.get(
            url=odata_link,
            auth=(odata_user, odata_pass)
        )
    
    result = request.json()
    return result['d']['results']