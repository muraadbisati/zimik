from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey,JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=True,default=None)
    phone_number = Column(Text, nullable=False, unique=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    orders = relationship("Order", back_populates="customer")

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, nullable=False,)
    name = Column(String, nullable=True, unique=True)
    sizes_price = Column(JSON, nullable=False)
    sizes_inventory = Column(JSON,nullable=False)

    order_items = relationship("OrderItem", back_populates="meal")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, nullable=False)
    phone_number = Column(Text,ForeignKey("customers.phone_number",ondelete="Set Null"), nullable=True)
    total_price = Column(Float, nullable=False)
    transactionId=Column(String,nullable=False,unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id",ondelete="CASCADE"))
    #meal_id = Column(Integer, ForeignKey("meals.id",ondelete="Set Null"))
    meal_name = Column(String, ForeignKey("meals.name",ondelete="Set Null"))
    size=Column(String,nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_items")#backwards relationship
    meal = relationship("Meal", back_populates="order_items")#backwards relationship



    