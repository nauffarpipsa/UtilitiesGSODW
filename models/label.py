from pydantic import BaseModel


class Label(BaseModel):
    branch_code: str
    branch_description: str
    product_code: str
    product_description: str
    serie_code: str | None
    quantity: str | None
    unit: str | None
    production_date: str | None


class LabelBranch(BaseModel):
    branch_code: str
    branch_description: str


class LabelAccess(BaseModel):
    user: str
    branchs: list[LabelBranch]