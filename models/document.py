from pydantic import BaseModel


class DocumentHeaderBase(BaseModel):
    country: str
    company: str
    branch: str
    number: str
    type: str
    client_name: str
    total_amount: float
    total_contribution: float
    petitioner: str 


class DocumentDetailProduct(BaseModel):
    code: str
    description:str
    quantity: int
    cost: float
    price: float
    new_price: float
    discount_percent: float
    contribution_percent: float
    price_cost_difference: float


class DocumentDetailAutorization(BaseModel):
    authorization_type: str
    authorization_description: str
    approver_user: str
    petitioner_comment: str | None
    products_detail: list[DocumentDetailProduct] | None


class DocumentRequest(DocumentHeaderBase):
    authorization_detail: list[DocumentDetailAutorization]


class DocumentResponseByNumberDetail(BaseModel):
    authorization_description: str
    approver_comment: str | None
    autorized: bool
    refused: bool


class DocumentResponseByNumber(BaseModel):
    number: str
    amount: float
    detail: list[DocumentResponseByNumberDetail]


class DocumentRequestByDate(BaseModel):
    country: str
    company: str
    approver_user: str
    requested_date_initial: str
    requested_date_end: str


class DocumentResponseByDateDetail(BaseModel):
    authorization_type: str
    authorization_description: str
    autorized: bool
    refused: bool
    petitioner_comment: str | None
    approver_comment: str | None
    products_detail: list[DocumentDetailProduct] | None



class DocumentResponseByDate(BaseModel):
    id: str
    branch_country: str
    requested_date: str
    number: str
    client_name: str
    petitioner: str
    total_amount: float
    total_contribution: float
    authorization_detail: list[DocumentResponseByDateDetail] | None