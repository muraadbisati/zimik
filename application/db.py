
from typing import List,Dict
from fastapi import  HTTPException, Response, status, Depends,APIRouter
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
#from sqlalchemy.orm.attributes import flag_modified
#from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy.future import select
import models
import schemas
from database import get_db,SessionLocal
from payment import pay_route,user_events
from config import settings
import asyncio
import os
from sqlalchemy.orm.attributes import flag_modified






router=APIRouter()


# READING CUSTOMER TABLE
@router.get('/customers', response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    return customers

# READING MEAL TABLE
@router.get('/meals', response_model=List[schemas.MealResponse])
def get_meals(db: Session = Depends(get_db)):
    meals = db.query(models.Meal).all()
    return meals

# READING ORDER TABLE
@router.get('/orders', response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return orders

# CREATING A CUSTOMER
@router.post('/customers', status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    new_customer = models.Customer(name=customer.name, phone_number=customer.phone_number)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# CREATING A MEAL
@router.post('/meals', status_code=status.HTTP_201_CREATED, response_model=schemas.MealResponse)
def create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    new_meal = models.Meal(name=meal.name, sizes_inventory=meal.sizes_inventory,sizes_price=meal.sizes_price)
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return new_meal

# CREATING AN ORDER
@router.post('/orders', status_code=status.HTTP_201_CREATED, response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    order_items = [models.OrderItem(meal_id=order_item.meal_id, quantity=order_item.quantity) for order_item in order.order_items]
    new_order = models.Order(phone_number=order.phone_number, total_price=order.total_price, order_items=order_items)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

# UPDATING A MEAL
@router.put('/meals/{meal_id}', response_model=schemas.MealResponse)
def change_meal(meal_id: int, meal: schemas.MealCreate, db: Session = Depends(get_db)):
    db_meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meal with id {meal_id} not found")
    db_meal.name = meal.name
    db_meal.sizes_inventory = meal.sizes_inventory
    db_meal.sizes_price = meal.sizes_price
    db.commit()
    db.refresh(db_meal)
    return db_meal

# DELETING A MEAL
@router.delete('/meals/{meal_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    db_meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meal with id {meal_id} not found")
    db.delete(db_meal)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# DELETING A CUSTOMER
@router.delete('/customers/{customer_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with id {customer_id} not found")

    db.delete(db_customer)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#Deleting A Order
@router.delete('/orders/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id {order_id} not found")
    
    db_orders = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    for order in db_orders:
        db.delete(order)

    db.delete(db_order)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)











async def update_meal(params_dict: Dict[str, List[any]], profile_name: str, to_number: str):
   from app import send_whatsapp_message
   
   with SessionLocal() as db:  
    try:
            
        # Extract parameters from params_dict
        pizza_types = params_dict.get('pizza-type',[])
        pizza_sizes = params_dict.get('pizza-size',[])
        amounts =  params_dict.get('amount', [])

        if  len(pizza_types) != len(pizza_sizes) or len(pizza_types) != len(amounts):
            return {"Please explicitly mention the amount, size, and type for each pizza"}

        total_price=0
        order_items=[]
        
        
        
        for pizza_type, pizza_size, quantity in zip(pizza_types, pizza_sizes, amounts):
            
            
            quantity = int(quantity) #float to int 
            
            
            meal = db.query(models.Meal).filter(models.Meal.name == pizza_type).first()

            
            if not meal:
                return {f"Sorry!!We currently do not sell {pizza_type} pizzas!Try ordering something else!"}
            
                # Check if the required quantity is available for the specified size
            if pizza_size not in meal.sizes_inventory or meal.sizes_inventory[pizza_size] < quantity:
                    return {f"{pizza_type} in {pizza_size} is sold out . Try again later"}
            
            # Calculate total price based on the selected size
            total_price += meal.sizes_price[pizza_size] *100* quantity 
                                
                #initiate payment
        stop_event = asyncio.Event()
        
        response_data_url,transaction_id = await pay_route(total_price, to_number,stop_event)
        
        
            #Redirect the user to the payment page
        send_whatsapp_message(f"To place your order ,kindly proceed with the given url and complete the payment!The url will expire in 5 mins\n{response_data_url}",to_number,status_callback_url=settings.STATUS_CALLBACK_URL)
        
        #Include in PROD with expiresIn from pay_route in payment.py to delete the session incase user doesnt proceed with payment 
        # Wait for the payment_return function to be called (after the user completes the payment process) 
        
        # try:
        #         await asyncio.wait_for(stop_event.wait(), timeout=300)  # 5 minutes timeout
        # except asyncio.TimeoutError:
        #         del user_events[transaction_id]
        #         return {f"The payment process timed out for your order{params_dict} Please make a new order."}
       
        await stop_event.wait()
        
        
        for pizza_type, pizza_size, quantity in zip(pizza_types, pizza_sizes, amounts):
            #Update the inventory for the specified size
                quantity = int(quantity) #float to int 
                meal = db.query(models.Meal).filter(models.Meal.name == pizza_type).first()
                print(meal.name)
                #update inventory
                meal.sizes_inventory[pizza_size] -= quantity
                print(meal.sizes_inventory)
                flag_modified(meal, 'sizes_inventory')  # Notify SQLAlchemy of the change
                db.commit()
                db.refresh(meal)

                
                order_item = models.OrderItem(meal_name=meal.name,quantity=quantity,size=pizza_size)
                order_items.append(order_item)

                

                db.commit()
                db.refresh(meal)

        #Create Customer
        stmt = insert(models.Customer).values(name=profile_name, phone_number=to_number)
        stmt = stmt.on_conflict_do_nothing(index_elements=['phone_number'])

        db.execute(stmt)
        db.commit()
        # Create order
        order = models.Order(total_price=total_price,phone_number=to_number,transactionId=transaction_id)
        order.order_items = order_items
        db.add(order)
        db.commit()
        stop_event.clear()
        return(f"Your payment is successful!\nTRANSACTION ID:\n{transaction_id}")
        
            
    except Exception as e:
            print(f"Error in update_meal: {str(e)}")
            
            return {"An unexpected error occurred"}
    

