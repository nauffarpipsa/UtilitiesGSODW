from fastapi import APIRouter, status, Query, Body, HTTPException

from db.client import db
from models.label import LabelAccess, LabelBranch, LabelLocation, Label
from services.label import get_labels

from typing import Annotated
import json


router = APIRouter(prefix='/label', tags=['Label'])


@router.post('/create_access', status_code=status.HTTP_201_CREATED)
async def create_access(access: Annotated[LabelAccess, Body()]):

    try:
        branchs: list[LabelBranch] = []
        locations: list[LabelLocation] = []

        data_dict = dict(access)
        
        for branch in data_dict['branchs']:
            branch = dict(branch)
            for location in branch['locations']:
                locations.append(dict(location))
            branch['locations'] = locations
            branchs.append(branch)

        data_dict['branchs'] = branchs
        db.local.labels.insert_one(data_dict)

        return {
            'message': 'ok'
        }   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')


@router.get('/get_access', response_model=LabelAccess, status_code=status.HTTP_200_OK)
async def get_access(user: Annotated[str, Query()]):

    label_db = db.local.labels.find_one({ 'user': user })

    if label_db:
        data_dict = dict(label_db)
        user_access = LabelAccess(
            user=data_dict.get('user'),
            branchs=data_dict.get('branchs')
        )
        return user_access

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"error, {str(e)}")
    

@router.get('/get_all', response_model=list[Label], status_code=status.HTTP_200_OK)
async def get_all(branch_code: Annotated[str, Query()]):
    try:
        label_list: list[Label] = []
        label_list_odata = get_labels(branch_code)

        if label_list_odata:
            for label_odata in label_list_odata:
                data_dict = dict(label_odata)

                label = Label(
                    branch_code = data_dict.get('CSITE_UUID'),
                    branch_description = data_dict.get('TSITE_UUID'),
                    product_code = data_dict.get('CMATERIAL_UUID'),
                    product_description = data_dict.get('TMATERIAL_UUID'),
                    serie_code = data_dict.get('CISTOCK_UUID'),
                    quantity = data_dict.get('KCON_HAND_STOCK'),
                    unit = data_dict.get('TON_HAND_STOCK_UOM'),
                    production_date = data_dict.get('CLAST_PUTAWAY_DT')
                )

                if label.production_date:
                    label.production_date = label.production_date.replace(' UTC-6', '')

                label_list.append(label)
        return label_list

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')