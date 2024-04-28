from enum import Enum
from typing import List, Optional

from fastapi import Form, UploadFile
from pydantic import BaseModel, EmailStr

from app.models.users import UserModel


class PaymentStatus(str, Enum):
    paid = "paid"
    unpaid = "unpaid"
    canceled = "canceled"


class FormOrderModel:

    def __init__(
            self,
            customer_name: str = Form(..., description="customer name"),
            customer_email: EmailStr = Form(..., description="customer email"),
            customer_phone: str = Form(..., description="customer phone"),
            customer_country: str = Form(..., description="customer country"),
            customer_address: str = Form(..., description="customer address"),
            total_price: int = Form(..., description="total price"),
            payment_status: PaymentStatus = Form(..., description="payment status"),
            payment_proof: Optional[UploadFile] = Form(None, description="payment proof"),
            user_id: str = Form(..., description="user id"),


    ):
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.customer_country = customer_country
        self.customer_address = customer_address
        self.total_price = total_price
        self.payment_status = payment_status
        self.payment_proof = payment_proof
        self.user_id = user_id


class FormEditOrderModel:

    def __init__(
            self,
            id: str = Form(..., description="order id"),
            customer_name: str = Form(..., description="customer name"),
            customer_email: EmailStr = Form(..., description="customer email"),
            customer_phone: str = Form(..., description="customer phone"),
            customer_country: str = Form(..., description="customer country"),
            customer_address: str = Form(..., description="customer address"),
            total_price: int = Form(..., description="total price"),
            payment_status: PaymentStatus = Form(..., description="payment status"),
            payment_proof: Optional[UploadFile] = Form(None, description="payment proof"),
            user_id: str = Form(..., description="user id"),
    ):
        self.id = id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.customer_country = customer_country
        self.customer_address = customer_address
        self.total_price = total_price
        self.payment_status = payment_status
        self.payment_proof = payment_proof
        self.user_id = user_id


class OrderModel(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_country: str
    customer_address: str
    total_price: int
    payment_status: PaymentStatus
    payment_proof: Optional[str]
    user: UserModel
    created_at: int
    updated_at: int


class OrderPaginationModel(BaseModel):
    page_number: int
    page_size: int
    total: int
    total_pages: int
    orders: List[OrderModel]
