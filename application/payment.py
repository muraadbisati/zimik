from fastapi import APIRouter, Request,Header
from fastapi.responses import RedirectResponse
import shortuuid
import json
import base64
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


import asyncio



import os


router = APIRouter()
#stop_event = asyncio.Event()




# Helper functions
def calculate_sha256_string(input_string: str) -> str:
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()

def base64_encode(input_dict: dict) -> str:
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')

def base64_decode(input_string: str) -> dict:
    data_bytes = base64.b64decode(input_string)
    return json.loads(data_bytes.decode('utf-8'))
# Set up Jinja2 templates directory
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "static"))

# Mount static directory for serving static files (if needed)
router.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")
# Routes
@router.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "page_respond_data": {}, "page_respond_data_varify": ""})

user_events = {}

@router.get("/pay")
async def pay_route(total_price,to_number,stop_event=None):
    MAINPAYLOAD = {
        "merchantId": "PGTESTPAYUAT86",
        "merchantTransactionId": shortuuid.uuid(),
        "merchantUserId": "MUID",
        "amount": total_price,
        "redirectUrl": "https://6a9f-103-50-21-38.ngrok-free.app/return-to-me",
        "redirectMode": "POST",
        "callbackUrl": "https://6a9f-103-50-21-38.ngrok-free.app/return-to-him",
        "mobileNumber": to_number,
        "paymentScope": "PHONEPE",
        #"expiresIn":60, works in prod , time in sec
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }
    
    INDEX = "1"
    ENDPOINT = "/pg/v1/pay"
    SALTKEY = "96434309-7796-489d-8924-ab56988a6076"

    base64String = base64_encode(MAINPAYLOAD)
    mainString = base64String + ENDPOINT + SALTKEY
    sha256Val = calculate_sha256_string(mainString)
    checkSum = sha256Val + '###' + INDEX

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': checkSum,
        'accept': 'application/json',
    }
    json_data = {
        'request': base64String,
    }
    response = requests.post('https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay',headers=headers,json=json_data)
    responseData = response.json()
    redirect_url = responseData['data']['instrumentResponse']['redirectInfo']['url']
    transaction_id=responseData['data']['merchantTransactionId']
    print(transaction_id)
    user_events[transaction_id] = stop_event
    print(user_events)
    return redirect_url,transaction_id

#redirect url
@router.post("/return-to-me")
async def payment_return(request: Request):

    
     

    form_data = await request.form()
    form_data_dict = dict(form_data)
    
    return templates.TemplateResponse('response.html', {"request": request, "page_respond_data": form_data_dict})


#callback url
@router.post("/return-to-him")
async def call_back(request: Request, x_verify: str = Header(None)):
    
    
    callback_data = await request.json()
    response = callback_data.get("response")
    decoded_response = base64_decode(response)
    transaction_id=decoded_response['data']['merchantTransactionId']
    stop_event = user_events.get(transaction_id)
    print(user_events)
    

    # Log the decoded response for debugging
    print("return-to-him")
    print("Decoded Callback Response:", decoded_response)
    
    # Verify the X-VERIFY header
    SALTKEY = "96434309-7796-489d-8924-ab56988a6076"  # Use your actual SALT key
    SALT_INDEX = "1"  # Use your actual SALT index
    calculated_verify = calculate_sha256_string(response + SALTKEY) + '###' + SALT_INDEX

    if x_verify == calculated_verify:
        print(user_events)
        stop_event.set()
        del user_events[transaction_id]
        print(user_events)
        

        return ()
    else:
        del user_events[transaction_id]
        raise asyncio.CancelledError()




#ADD in case of callback failure  manual recheck
# if transactionId:
#         request_url = f'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/status/PGTESTPAYUAT86/{transactionId}'
#         sha256_Pay_load_String = f'/pg/v1/status/PGTESTPAYUAT86/{transactionId}{SALTKEY}'
#         sha256_val = calculate_sha256_string(sha256_Pay_load_String)
#         checksum = sha256_val + '###' + INDEX

#         headers = {
#             'Content-Type': 'application/json',
#             'X-VERIFY': checksum,
#             'X-MERCHANT-ID': transactionId,
#             'accept': 'application/json',
#         }
#         response = requests.get(request_url, headers=headers)
#         data=response.json()
#         If data['code]=='PAYMENT_SUCCESS'





#ADD TO CHECK PENDING TRANSACTIONS 
# def handle_payment_pending(transactionId, db):
#     intervals = [
#         (3, 10),  # Every 3 seconds for the next 30 seconds
#         (6, 10),  # Every 6 seconds for the next 60 seconds
#         (10, 6),  # Every 10 seconds for the next 60 seconds
#         (30, 2),  # Every 30 seconds for the next 60 seconds
#         (60, 19)  # Every 1 minute for the next 19 minutes
#     ]

#     # First check after 20-25 seconds
#     time.sleep(20)
#     check_payment_status(transactionId, db)
#     time.sleep(5)

#     # Iterate over each interval and check payment status
#     for interval, count in intervals:
#         for _ in range(count):
#             check_payment_status(transactionId, db)
#             time.sleep(interval)
    
#     # Continue checking every 1 minute until timeout (20 mins total)
#     start_time = time.time()
#     timeout = 20 * 60  # 20 minutes in seconds
#     while time.time() - start_time < timeout:
#         check_payment_status(transactionId, db)
#         time.sleep(60)


