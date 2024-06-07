from pydantic import BaseModel, Field
from typing import Optional, List,Dict
from datetime import datetime
class MealBase(BaseModel):
    name: str
    sizes_inventory: Dict[str, int] = Field(..., description="Inventory counts for different sizes")
    sizes_price: Dict[str, int] = Field(..., description="Price for different sizes")

class MealCreate(MealBase):
    # Schema for creating a new meal
    pass

class MealResponse(MealBase):
    id: int
    #inventory: int

    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    meal_id: int
    size:str
    quantity: int
    

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    meal: "MealResponse"  # Replace with the actual MealResponse schema

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    total_price: float
    order_items: List[OrderItemCreate] = []

class OrderCreate(OrderBase):
    phone_number: Optional[str]

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    phone_number: Optional[str]
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    phone_number: str = Field(..., min_length=10, max_length=12)

class CustomerCreate(CustomerBase):
    # Schema for creating a new customer
    pass

class CustomerResponse(CustomerBase):
    id: int
    #created_at: str
    #orders: List[OrderResponse] = []

    class Config:
        from_attributes = True