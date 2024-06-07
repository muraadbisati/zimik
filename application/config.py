from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
# Manually load the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))



class Settings(BaseSettings):

    # database_hostname:str
    # database_port:str
    # database_password:str
    # database_password:str
    # database_username:str
  
  #dialogflow  
  
    project_id:str
    private_key_id:str
    client_email:str
    client_id:str
    auth_uri:str
    token_uri:str
    auth_provider_x509_cert_url:str
    client_x509_cert_url:str
    universe_domain:str

    #Twilio KEY

    TWILIO_ACCOUNT_SID:str
    TWILIO_AUTH_TOKEN:str
    TWILIO_FROM_NUMBER:str
    TWILIO_TO_NUMBER:str
    STATUS_CALLBACK_URL:str

    class Config:
        env_file= os.path.join(os.path.dirname(__file__), '..', '.env')
       


settings= Settings()    
