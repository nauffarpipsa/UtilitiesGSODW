from fastapi import APIRouter, status, Query, Body, HTTPException

from db.client import db
from models.label import LabelAccess, LabelAccessResponse, LabelBranch, LabelLocation, Label, PrintLabel, LabelQuantity
from services.label import get_labels

from typing import Annotated
from dotenv import load_dotenv
import os


load_dotenv()

router = APIRouter(prefix='/label', tags=['Label'])

# post's
@router.post('/create_access', status_code=status.HTTP_201_CREATED)
async def create_access(access: Annotated[LabelAccess, Body()]):

    try:
        branchs: list[LabelBranch] = []
        
        data_dict = dict(access)
        data_dict['user'] = str(data_dict.get('user')).lower()

        user = db.local.labels.find_one(
            {
                'user': data_dict.get('user')
            }
        )

        if not user:
            for branch in data_dict.get('branchs'):
                branch = dict(branch)
                locations: list[LabelLocation] = []

                for location in branch.get('locations'):
                    location_dict = dict(location)
                    location_dict['active'] = True
                    locations.append(location_dict)

                branch['locations'] = locations
                branch['active'] = True
                branchs.append(branch)

            data_dict['branchs'] = branchs
            data_dict['active'] = True

            db.local.labels.insert_one(data_dict)

            return {
                'message': 'ok'
            }
        
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f'user {data_dict.get('user')} already exists')
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')


@router.post('/add_branch_by_user', status_code=status.HTTP_201_CREATED)
async def add_branch_by_user(user: Annotated[str, Query()], branch: Annotated[LabelBranch, Body()]):
    
    try:
        branch_dict = dict(branch)
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user, 'active': True
            }
        )

        # validate user db
        if user_db:     

            user_db_dict = dict(user_db)
            branch_db_list = list(user_db_dict['branchs'])

            branch_found = [branch for branch in branch_db_list if branch['branch_code'] == branch_dict['branch_code']]
            
            if branch_found: 
                raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'branch code {branch_dict.get('branch_code')} already exists')

            else:
                location_list = []
                                
                for location in branch_dict['locations']:

                    location_dict = dict(location)
                    location_dict['active'] = True
                    location_list.append(location_dict)
                            
                    branch_dict['locations'] = location_list
                    branch_dict['active'] = True
                    branch_db_list.append(branch_dict)

                    db.local.labels.update_one(
                        {
                            "user": user
                        },
                        {
                            '$set': {
                                'branchs': branch_db_list,
                            }
                        }
                    ) 
                    
            return {
                'message': 'ok'
            }
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found or not active')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')


@router.post('/add_location_by_branch_and_user', status_code=status.HTTP_200_OK)
async def add_location_by_branch_and_user(user: Annotated[str, Query()], branch_code: Annotated[str, Query()], location: Annotated[LabelLocation, Body()]):
    
    try:
        location_dict = dict(location)
        location_dict['active'] = True

        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user, 'active': True
            }
        )

        # validate user db
        if user_db:     

            user_db_dict = dict(user_db)
            branch_db_list = list(user_db_dict['branchs'])

            branch_found = [branch_search for branch_search in branch_db_list if branch_search['branch_code'] == branch_code]
            
            if branch_found:

                if branch_found[0]['active']:
                    location_found = [location_search for location_search in branch_found[0]['locations'] if location_search['description'] == location_dict['description']]

                    if location_found:
                        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'location {location_dict.get('description')} already exists')
                        
                    else:
                        location_list = branch_found[0]['locations']
                        location_list.append(location_dict)
                        branch_found[0]['locations'] = location_list                    

                        db.local.labels.update_one(
                            {
                                "user": user
                            },
                            {
                                '$set': {
                                    'branchs': branch_db_list,
                                }
                            }
                        )
                else:
                    raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'branch code {branch_code} not active')

            else:
                raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'branch code {branch_code} not found')
                    
            return {
                'message': 'ok'
            }
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found or not active')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')


@router.post('/print_label', status_code=status.HTTP_200_OK)
def print_label(data: Annotated[PrintLabel, Body()]):

    try:
        data_dict = dict(data)
        path = f'{os.getenv('FOLDER_LABEL')}/{data_dict.get('path')}'
        labels: list[LabelQuantity] = data_dict.get('labels')
        label_text: list[str] = []

        if labels:
            if not os.path.exists(path=path):
                os.makedirs(path)
   
            for label_result in labels:
                quantity = label_result.quantity_printer
                label = label_result.label
                while quantity > 0:
                    label_text.append(f'{label.branch_description};{label.product_code};{label.serie_code};{label.unit};{label.quantity};{label.production_date}\n')
                    quantity -= 1

            with open(f'./{path}/{os.getenv('FILE_LABEL')}', mode='a+', encoding='utf-8') as file:
                for label in label_text:
                    if label:
                        file.write(label)

            return {
                'message': 'ok'
            }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail='error, file not created')


# get's
@router.get('/get_access', status_code=status.HTTP_200_OK)
async def get_access(user: Annotated[str, Query()]):

    label_db = db.local.labels.find_one({ 'user': user.lower(), 'active': True })

    if label_db:
        data_dict = dict(label_db)
        branch_list = []

        for branch in data_dict['branchs']:

            # validate active branch
            if branch['active']:

                location_list = []

                for location in branch['locations']:

                    # validate active location
                    if location['active']:
                        location_list.append(location)
                
                # add active locations
                branch['locations'] = location_list
                branch_list.append(branch)
        
        user_access = LabelAccessResponse(
                    user=data_dict.get('user'),
                    branchs=branch_list,
                    active=data_dict.get('active')
                )
        
        return user_access
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"error, user not found or not active")


@router.get('/get_all', response_model=list[Label], status_code=status.HTTP_200_OK)
async def get_all(branch_code: Annotated[str, Query()]):
    
    try:
        label_list: list[Label] = []
        label_list_odata = get_labels(branch_code)

        if label_list_odata:
            for label_odata in label_list_odata:
                data_dict = dict(label_odata)

                if data_dict.get('C1ISTOCK_UUIDsISTOCK_ID'):
                    label = Label(
                        branch_code = data_dict.get('CSITE_UUID'),
                        branch_description = data_dict.get('TSITE_UUID'),
                        product_code = data_dict.get('CMATERIAL_UUID'),
                        product_description = data_dict.get('TMATERIAL_UUID'),
                        serie_code = data_dict.get('C1ISTOCK_UUIDsISTOCK_ID'),
                        quantity = str(float(data_dict.get('KCON_HAND_STOCK'))),
                        unit = data_dict.get('TON_HAND_STOCK_UOM'),
                        production_date = data_dict.get('CLAST_PUTAWAY_DT')
                    )

                    if label.production_date:
                        label.production_date = label.production_date.replace(' UTC-6', '')

                    label_list.append(label)

        return label_list

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')


# put's
@router.put('/active_user', status_code=status.HTTP_200_OK)
async def active_user(user: Annotated[str, Query()]):
    
    try:
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user
            }
        )

        # validate user db
        if user_db:  
            if user_db['active']:
                raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'user {user} already active')

            else:
                db.local.labels.update_one(
                    {
                        "user": user
                    },
                    {
                        '$set': {
                            'active': True,
                        }
                    }
                )

                return {
                    'message': 'ok'
                }

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')


@router.put('/inactive_user', status_code=status.HTTP_200_OK)
async def inactive_user(user: Annotated[str, Query()]):
    
    try:
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user
            }
        )

        # validate user db
        if user_db:  
            if not user_db['active']:
                raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'user {user} already inactive')

            else:
                db.local.labels.update_one(
                    {
                        "user": user
                    },
                    {
                        '$set': {
                            'active': False,
                        }
                    }
                )

                return {
                    'message': 'ok'
                }

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')
    

@router.put('/active_branch', status_code=status.HTTP_200_OK)
async def active_branch(user: Annotated[str, Query()], branch_code: Annotated[str, Query()]):
    
    try:
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user, 'active': True
            }
        )

        # validate user db
        if user_db:
            branch_found = [branch_search for branch_search in user_db['branchs'] if branch_search['branch_code'] == branch_code ]

            if branch_found:         
                if branch_found[0]['active']:
                    raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'branch code {branch_code} already active')

                else:
                    branch_found[0]['active'] = True

                    db.local.labels.update_one(
                        {
                            "user": user
                        },
                        {
                            '$set': {
                                'branchs': user_db['branchs'],
                            }
                        }
                    )

                return {
                    'message': 'ok'
                }

            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'branch code {branch_code} not found')

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found or not active')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')
    

@router.put('/inactive_branch', status_code=status.HTTP_200_OK)
async def inactive_branch(user: Annotated[str, Query()], branch_code: Annotated[str, Query()]):
    
    try:
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user, 'active': True
            }
        )

        # validate user db
        if user_db:
            branch_found = [branch_search for branch_search in user_db['branchs'] if branch_search['branch_code'] == branch_code ]

            if branch_found:
                if not branch_found[0]['active']:
                    raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'branch code {branch_code} already inactive')

                else:
                    branch_found[0]['active'] = False

                    db.local.labels.update_one(
                        {
                            "user": user
                        },
                        {
                            '$set': {
                                'branchs': user_db['branchs'],
                            }
                        }
                    )

                return {
                    'message': 'ok'
                }

            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'branch code {branch_code} not found')

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found or not active')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')
    

@router.put('/active_location', status_code=status.HTTP_200_OK)
async def active_branch(user: Annotated[str, Query()], branch_code: Annotated[str, Query()], location_description: Annotated[str, Query()]):
    
    try:
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user, 'active': True
            }
        )

        # validate user db
        if user_db:
            branch_found = [branch_search for branch_search in user_db['branchs'] if branch_search['branch_code'] == branch_code ]

            if branch_found:         
                if branch_found[0]['active']:
                    location_found = [location_search for location_search in branch_found[0]['locations'] if location_search['description'] == location_description ]

                    if location_found:
                        
                        if location_found[0]['active']:
                            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'location {location_description} already active')
                        
                        else:
                            location_found[0]['active'] = True
                            db.local.labels.update_one(
                                {
                                    "user": user
                                },
                                {
                                    '$set': {
                                        'branchs': user_db['branchs'],
                                    }
                                }
                            )
                            
                            return {
                                'message': 'ok'
                            }
                    
                    else:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'location {location_description} not found')

                else:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'branch code {branch_code} not active')

            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'branch code {branch_code} not found')

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found or not active')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')
    

@router.put('/inactive_location', status_code=status.HTTP_200_OK)
async def inactive_branch(user: Annotated[str, Query()], branch_code: Annotated[str, Query()], location_description: Annotated[str, Query()]):
    
    try:
        user = user.lower()

        # find user db
        user_db = db.local.labels.find_one(
            {
                'user': user, 'active': True
            }
        )

        # validate user db
        if user_db:
            branch_found = [branch_search for branch_search in user_db['branchs'] if branch_search['branch_code'] == branch_code ]

            if branch_found:         
                if branch_found[0]['active']:
                    location_found = [location_search for location_search in branch_found[0]['locations'] if location_search['description'] == location_description ]

                    if location_found:
                        
                        if not location_found[0]['active']:
                            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f'location {location_description} already inactive')
                        
                        else:
                            location_found[0]['active'] = False
                            db.local.labels.update_one(
                                {
                                    "user": user
                                },
                                {
                                    '$set': {
                                        'branchs': user_db['branchs'],
                                    }
                                }
                            )
                            
                            return {
                                'message': 'ok'
                            }
                    
                    else:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'location {location_description} not found')

                else:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'branch code {branch_code} not active')

            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'branch code {branch_code} not found')

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user {user} not found or not active')

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'error, {str(e)}')