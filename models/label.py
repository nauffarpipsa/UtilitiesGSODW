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


class LabelLocation(BaseModel):
    description: str
    path: str


class LabelLocationResponse(LabelLocation):
    active: bool | None = None


class LabelBranch(BaseModel):
    branch_code: str
    branch_description: str
    locations: list[LabelLocation]


class LabelBranchResponse(BaseModel):
    branch_code: str
    branch_description: str
    locations: list[LabelLocationResponse]
    active: bool | None = None


class LabelAccess(BaseModel):
    user: str
    branchs: list[LabelBranch]


class LabelAccessResponse(BaseModel):
    user: str
    branchs: list[LabelBranchResponse]
    active: bool | None = None


class LabelQuantity(BaseModel):
    quantity_printer: int
    label: Label


class PrintLabel(BaseModel):
    path: str
    labels: list[LabelQuantity]
    