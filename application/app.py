

from fastapi import  Request,APIRouter
import os
from twilio.rest import Client
from google.cloud.dialogflow_v2 import types, SessionsClient
from config import settings
from datetime import datetime
from logs.log import logger, log_error
from db import update_meal
import asyncio



router = APIRouter()

# Dialog flow credential setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(os.getcwd()),"Dialog_Key.json")
project_id = settings.project_id


# Twilio credential setup

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
status_callback_url = settings.STATUS_CALLBACK_URL

# Declare global variables
language_code = "en-US"
dialogflow_response = ""
to_number=""
media_url=""



# Dialogflow API setup
async def detect_intent_texts(project_id, session_id, text,profile_name,to_number,language_code):
    global dialogflow_response,media_url
    
    try:
        session_client = SessionsClient()
        session = session_client.session_path(project_id, session_id)
        logger.info(f"Session path: {session}")

        text_input = types.TextInput(text=text, language_code=language_code)#packaging the raw text and its language information into a format that the API can understand.
        query_input = types.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        logger.info("=" * 20)
        logger.info(f"Query text: {response.query_result.query_text}")
        logger.info(
            f"Detected intent: {response.query_result.intent.display_name} (confidence: {response.query_result.intent_detection_confidence})"
        )
        logger.info(f"Fulfillment text: {response.query_result.fulfillment_text}")
        
        params_dict={} 
        #Format message body for whatsapp
        if response.query_result.intent.display_name in ["item.start.generic", "item.size.change", "item.type.change", "item.amount.change"]:
            query_params = response.query_result.parameters
            params_dict = {}
            for key, value in query_params.items():
                params_dict[key] = value
            dialogflow_response =  await format_message_body(params_dict) + "\n\n"+ response.query_result.fulfillment_text
            
            return dialogflow_response
            





        # Extract parameters
        if response.query_result.intent.display_name == "item.confrim.yes":
            query_params = response.query_result.parameters
            params_dict = {}
            for key, value in query_params.items():
                params_dict[key] = value
            logger.info("=" * 20)
            logger.info(f"Query Parameters: {params_dict}")
            
            task=asyncio.create_task(update_meal(params_dict,profile_name,to_number))
            try:
                dialogflow_response=await task
                print(dialogflow_response)
                return dialogflow_response
            except asyncio.CancelledError:
              dialogflow_response="Payment Failed"
              return dialogflow_response

            
            
        if response.query_result.intent.display_name=="show.menu":
          media_url='https://6a9f-103-50-21-38.ngrok-free.app/images/menu.jpg'
             


        dialogflow_response = response.query_result.fulfillment_text
        
        return dialogflow_response,media_url
    
    except Exception as e:
        log_error(f"Error in detect_intent_texts: {str(e)}")
        raise e



def send_whatsapp_message(message_body, to_number, status_callback_url, media_url=None):
    try:
        client = Client(account_sid, auth_token)
        
        # Create the message with conditional media_url
        if media_url:
            message = client.messages.create(
                body=message_body,
                from_="whatsapp:+14155238886",
                to=f"whatsapp:{to_number}",
                media_url=[media_url],  
                status_callback=status_callback_url
            )
        else:
            message = client.messages.create(
                body=message_body,
                from_="whatsapp:+14155238886",
                to=f"whatsapp:{to_number}",
                status_callback=status_callback_url  # No media_url when it's not provided
            )
        
        return message.sid
    except Exception as e:
        print(f"Error: {e}")
        return None






async def format_message_body(params_dict):
    # Extract the values from the dictionary
    pizza_types = params_dict.get('pizza-type', [])
    pizza_sizes = params_dict.get('pizza-size', [])
    amounts = params_dict.get('amount', [])

      # Find the maximum length to iterate through
    max_len = max(len(pizza_types), len(pizza_sizes), len(amounts))

    # Ensure all lists are the same length by padding with '?'
    pizza_types.extend(['?'] * (max_len - len(pizza_types)))
    pizza_sizes.extend(['?'] * (max_len - len(pizza_sizes)))
    amounts.extend(['?'] * (max_len - len(amounts)))

    # Create the header
    table_str = "{:<10} {:<10} {:<10}\n".format('Pizza', 'Size', 'Qty')

    # Add each row to the string
    for i in range(len(pizza_types)):
        table_str += "{:<10} {:<10} {:<10}\n".format(pizza_types[i], pizza_sizes[i], amounts[i])

    # Wrap the table with monospace formatting
    table_str = "```\n" + table_str + "```"

    

    return table_str





@router.post('/reply')
async def reply(request: Request):
    global media_url
    
    try:
        form = await request.form()
        to_number=form.get("WaId")
        session_id=to_number
        profile_name=form.get("ProfileName")
        message = form.get('Body')
        logger.info(f"Received message: {message}")
        
        

        start_time = datetime.now()
        await detect_intent_texts(project_id, session_id, message,profile_name,to_number,language_code)
        message_body = dialogflow_response
        print(message_body)
        message_sid = send_whatsapp_message(message_body,to_number,status_callback_url,media_url)
        media_url=""
        

        end_time = datetime.now()
        time_taken = end_time - start_time
        logger.info(f"Sent WhatsApp message with SID: {message_sid}")
        logger.info(f"Time taken: {time_taken}")

        
        return {"message_sid": message_sid}
    except Exception as e:
        log_error(f"Error in reply: {str(e)}")
        return {"error": "An error occurred while processing the request."}
    




@router.post("/status")
async def incoming_sms(request: Request):
    form = await request.form()
    message_status = form.get('MessageStatus', None)
    logger.info('Status: {}'.format(message_status))
   

    return "Success"
    


    
