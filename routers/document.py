from fastapi import APIRouter, Path, Query, Body, File, UploadFile, status, HTTPException
from models.document import DocumentRequest, DocumentResponseByNumber, DocumentResponseByNumberDetail, DocumentResponseByDate, DocumentResponseByDateDetail, DocumentDetailProduct
from db.client import db
from bson.objectid import ObjectId

from typing import Annotated
from datetime import datetime
import os
import shutil


router = APIRouter(prefix='/document', tags=['Document'])

@router.post(path='/create', status_code=status.HTTP_201_CREATED, description='Endpoint for Marvin')
async def create(documents: Annotated[DocumentRequest, Body()]):
    try:
        autorization_list = []

        data_dict = dict(documents)
        data_dict['requested_date'] = datetime.now().date().strftime('%Y-%m-%d')
        data_dict['canceled_date'] = None
        data_dict['canceled'] = False

        for autorization in list(data_dict['authorization_detail']):
            product_list = []
            auth_dict = dict(autorization)
            auth_dict['approver_comment'] = None
            auth_dict['authorized_date'] = None
            auth_dict['autorized'] = False
            auth_dict['refused_date'] = None
            auth_dict['refused'] = False

            if auth_dict['products_detail']:
                for product in list(auth_dict['products_detail']):
                    product_dict = dict(product)
                    product_list.append(product_dict)
                
                auth_dict['products_detail'] = product_list
            autorization_list.append(auth_dict)

        data_dict['authorization_detail'] = autorization_list
        db.local.documents.insert_one(data_dict)

        return {
            'message': 'ok'
        }
    
    except:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail='documento no creado')


@router.get(path='/get_by_number/{number}', response_model=DocumentResponseByNumber | None, status_code=status.HTTP_200_OK, description='Endpoint for Marvin')
async def get_by_number(
    number: Annotated[str, Path()],
    country: Annotated[str, Query()],
    company: Annotated[str, Query()],
    branch: Annotated[str, Query()],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10
):
    try:
        document: DocumentResponseByNumber = None
        request_filter = dict()
        request_filter['country'] = country
        request_filter['company'] = company
        request_filter['branch'] = branch
        request_filter['number'] = number
        request_filter['canceled'] = False

        documents_db_list = db.local.documents.find(request_filter).skip(skip).limit(limit)
        data_db_list = list(documents_db_list)

        if (data_db_list):
            data_db_dict = dict(data_db_list[0])

            document = DocumentResponseByNumber(
                number = data_db_dict.get('number'), 
                amount = data_db_dict.get('total_amount'), 
                detail=[]
            )
                                                    
            for document_db in data_db_list:
                data_dict = dict(document_db)

                for autorization in data_dict['authorization_detail']:
                    data_detail = DocumentResponseByNumberDetail(
                        authorization_description = autorization.get('authorization_description'),
                        approver_comment = autorization.get('approver_comment'),
                        autorized = autorization.get('autorized'),
                        refused = autorization.get('refused')
                    )
                    document.detail.append(data_detail)
        return document
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')


@router.get(path='/get_by_date', response_model=list[DocumentResponseByDate], status_code=status.HTTP_200_OK, description='Endpoint for Peter')
async def get_by_date(
    country: Annotated[str, Query()],
    company: Annotated[str, Query()],
    approver_user: Annotated[str, Query()],
    requested_date_initial: Annotated[str, Query()],
    requested_date_end: Annotated[str, Query()],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10
):
    try:
        documents_list: list[DocumentResponseByDate] = []
        request_filter = dict()

        request_filter['country'] = country
        request_filter['company'] = company
        request_filter['requested_date'] = { '$gte': requested_date_initial, '$lte': requested_date_end }
        request_filter['canceled'] = False
        request_filter['authorization_detail.approver_user'] = approver_user
        
        documents_db_list = db.local.documents.find(request_filter).skip(skip).limit(limit)
        data_db_list = list(documents_db_list)

        if data_db_list:
            for document_db in data_db_list:
                data_dict = dict(document_db)

                document = DocumentResponseByDate(
                    id = str(ObjectId(data_dict.get('_id'))),
                    branch_country = f"{data_dict.get('branch')} / {data_dict.get('country')}",
                    requested_date = data_dict.get('requested_date'),
                    number = data_dict.get('number'),
                    client_name = data_dict.get('client_name'),
                    petitioner = data_dict.get('petitioner'),
                    total_amount = data_dict.get('total_amount'),
                    total_contribution = data_dict.get('total_contribution'),
                    authorization_detail = []
                )

                if data_dict.get('authorization_detail'):
                    for autorization in data_dict['authorization_detail']:
                        auth_dict = dict(autorization)

                        if auth_dict.get('approver_user') == approver_user:
                            auth_detail = DocumentResponseByDateDetail(
                                authorization_type = auth_dict.get('authorization_type'),
                                authorization_description = auth_dict.get('authorization_description'),
                                autorized = auth_dict.get('autorized'),
                                refused = auth_dict.get('refused'),
                                approver_comment = auth_dict.get('approver_comment'),
                                petitioner_comment = auth_dict.get('petitioner_comment'),
                                products_detail = []                       
                            )

                            if auth_dict['products_detail']:
                                for product in auth_dict['products_detail']:
                                    product_detail = DocumentDetailProduct(
                                        code = product['code'],
                                        description = product['description'],
                                        quantity = product['quantity'],
                                        cost = product['cost'],
                                        price = product['price'],
                                        new_price = product['new_price'],
                                        discount_percent = product['discount_percent'],
                                        contribution_percent = product['contribution_percent'],
                                        price_cost_difference = product['price_cost_difference']
                                    )
                                    auth_detail.products_detail.append(product_detail)
                            document.authorization_detail.append(auth_detail)
                    documents_list.append(document)
        return documents_list
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found')
    

@router.put(path='/update_autorized/{id}', status_code=status.HTTP_200_OK, description='Endpoint for Peter')
async def update_autorized(
    id: Annotated[str, Path()], 
    authorization_type: Annotated[str, Query()],
    comment: Annotated[str | None, Query()] = None
):
    try:
        db.local.documents.find_one_and_update(
            {
                '_id': ObjectId(id),
                'authorization_detail': {'$elemMatch': { 'authorization_type': authorization_type }}
            },
            {
                '$set': {
                    'authorization_detail.$.autorized': True, 
                    'authorization_detail.$.approver_comment': comment,
                    'authorization_detail.$.authorized_date': datetime.now().date().strftime('%Y-%m-%d')
                }
            }
        )
        return 'autorized'
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='error, not autorized')


@router.put(path='/update_refused/{id}', status_code=status.HTTP_200_OK, description='Endpoint for Peter')
async def update_refused(
    id: Annotated[str, Path()], 
    authorization_type: Annotated[str, Query()],
    comment: Annotated[str | None, Query()] = None
): 
    try:
        db.local.documents.find_one_and_update(
            {
                '_id': ObjectId(id),
                'authorization_detail': {'$elemMatch': { 'authorization_type': authorization_type }}
            }, 
            {
                '$set': {
                    'authorization_detail.$.refused': True, 
                    'authorization_detail.$.approver_comment': comment, 
                    'authorization_detail.$.refused_date': datetime.now().date().strftime('%Y-%m-%d')
                }
            }
        )
        return 'refused'
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='error, not refused')


@router.put(path='/update_canceled/{number}', status_code=status.HTTP_200_OK, description='Endpoint for Marvin')
async def update_canceled(
    number: Annotated[str, Path()],
    country: Annotated[str, Query()],
    company: Annotated[str, Query()]
):    
    try:
        db.local.documents.update_many(
            {
                'number': number, 'country': country, 'company': company
            },
            {
                '$set': {
                    'canceled': True,
                    'canceled_date': datetime.now().date().strftime('%Y-%m-%d')
                }
            }
        )
        return 'canceled'
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='error, not canceled')
    

@router.post(path='/uploadfile', status_code=status.HTTP_200_OK, description='Endpoint for Peter')
async def upload_file(file: UploadFile):
    try:
        file_location = os.path.join('./uploads', file.filename)

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        return {"filename": file.filename, "location": file_location}
    except Exception as e:
        return {"error": str(e)}