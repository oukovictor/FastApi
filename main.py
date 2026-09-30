from calendar import month, monthrange
import os
import json
import base64
import datetime
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to daraja api"}

@app.get("/api/v1/access_token")
def get_access_token():
    try:
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")
        credentials = f"{consumer_key}:{consumer_secret}"


        encoded = base64.b64encode(credentials.encode()).decode()




        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        headers = {"Authorization": f"Basic {encoded}"}

        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def fetch_access_token():
    try:
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")
        credentials = f"{consumer_key}:{consumer_secret}"
        
        
        encoded = base64.b64encode(credentials.encode()).decode()
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        headers = {"Authorization": f"Basic {encoded}"}
        
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_month_datetime_range(year:int = None, month:int = None):
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    
    start_date = datetime.datetime(year, month, 1)
    end_date = datetime.datetime(year, month, monthrange(year, month)[1])
    
    return(
            start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            end_date.strftime("%Y-%m-%dT%H:%M:%S")
        )
        


@app.post("/api/v1/stkpush")
async def stk_push(request: Request):
    try:
        shortcode = os.getenv("BUSINESS_SHORTCODE")
        passkey = os.getenv("PASSKEY")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

        request_data = await request.json()
        amount = request_data.get("amount", 1)  # Default amount to 1 if not provided

        phone_number = request_data.get("phone", 254769389071)  # Default phone number if not provided
        print(f"Received amount: {amount}, phone number: {phone_number}")
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://93ixm4-ip-41-139-171-209.tunnelmole.net/api/v1/callback",
            "AccountReference": "Test123",
            "TransactionDesc": "Payment of X"
        }
        data = fetch_access_token()
        access_token = data.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, headers=headers, json=payload)
        try:
            return response.json()
        except ValueError:
            return {
                "error": "Safaricom returned a non-JSON response",
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "response": response.text,
            }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/callback")
async def callback(request: Request):
    try:
        body = await request.body()
        data = json.loads(body)
        print (data)
        print({"message": "Callback received successfully"})
    except Exception as e:
        return {"error": str(e)}
    

@app.post("/api/v1/query")
def query():
    try:
        shortcode = os.getenv("BUSINESS_SHORTCODE")
        passkey = os.getenv("PASSKEY")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": "ws_CO_040820261631098769389071",
        }
        data = fetch_access_token()
        access_token = data.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/transaction_status")
def transaction_status():
    try:
        shortcode = os.getenv("BUSINESS_SHORTCODE")
        passkey = os.getenv("PASSKEY")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
        payload = {
            "Initiator": "testapi",
            "SecurityCredential": password,
            "CommandID": "TransactionStatusQuery",
            "TransactionID": "LGR61H7Q1K",
            "PartyA": shortcode,
            "IdentifierType": 4,
            "ResultURL": "https://93ixm4-ip-41-139-171-209.tunnelmole.net/api/v1/callback",
            "QueueTimeOutURL": "https://93ixm4-ip-41-139-171-209.tunnelmole.net/api/v1/callback",
            "Remarks": "Checking transaction status",
            "Occasion": "Test"
        }
        data = fetch_access_token()
        access_token = data.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query"
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/register_urls")
def register_urls():
    try:
        shortcode = os.getenv("BUSINESS_SHORTCODE")
        passkey = os.getenv("PASSKEY")
        start_date , end_date = get_month_datetime_range()
        payload = {
            "ShortCode": "174379",
            "RequestType": "Pull",
            "NominatedNumber": "254722000000",
            "CallBackURL": "https://93ixm4-ip-41-139-171-209.tunnelmole.net/api/v1/callback"
        }

        data = fetch_access_token()
        access_token = data.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept-Encoding": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/pulltransactions/v1/register"
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/pull_transactions")
def pull_transactions():
    try:
        shortcode = os.getenv("BUSINESS_SHORTCODE")
        passkey = os.getenv("PASSKEY")
        start_date , end_date = get_month_datetime_range()
        payload = {
            "ShortCode": "174379",
            "StartDate": start_date,
            "EndDate": end_date,
            "OffsetValue": 0,
        }

        data = fetch_access_token()
        access_token = data.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept-Encoding": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/pulltransactions/v1/query"
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
