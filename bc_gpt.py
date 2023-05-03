import os
import json
import openai
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

client_id = os.getenv("BIGCOMMERCE_CLIENT_ID")
access_token = os.getenv("BIGCOMMERCE_ACCESS_TOKEN")
store_hash = os.getenv("BIGCOMMERCE_STORE_HASH")

# Define the BigCommerce API endpoints
base_url = f"https://api.bigcommerce.com/stores/{store_hash}"
orders_url = f"{base_url}/v2/orders"

def get_tracking_number_by_order_id(order_id):
    shipments = requests.get(f"{orders_url}/{order_id}/shipments", headers={
            "Accept": "application/json",
            "X-Auth-Client": client_id,
            "X-Auth-Token": access_token
        })
    print(f'url:  {orders_url}/{order_id}/shipments')
    print(f'tracking > order_id:  {order_id}')
    print(f'shipments.status_code{shipments.status_code}')
    if shipments.status_code != 200:
        return None
    first_shipment = shipments.json()[0]
    tracking_info = first_shipment["tracking_number"]
    # carrier = first_shipment["tracking_carrier"]
    # tracking_link = f"https://www.{carrier.lower()}.com/tracking/{tracking_info}"
    tracking_link = f"https://www.aftership.com/track/ups/{tracking_info}"
    print(tracking_link)
    return tracking_link

# Define a function to check if an order has shipped and get the tracking information
def get_order_status_by_order_id(order_id):
    response = requests.get(f"{orders_url}/{order_id}", headers={
        "Accept": "application/json",
        "X-Auth-Client": client_id,
        "X-Auth-Token": access_token
    })

    print(f"order id: {order_id}")
    print(f"status code: {response.status_code}")
    print(f"{orders_url}/{order_id}")
    if response.status_code != 200:
        return None, None

    order = response.json()
    if order["status"] != "Shipped" and order["status"] != "Completed":
        return order["status"], None
    tracking_link = get_tracking_number_by_order_id(int(order_id))
    return order["status"], tracking_link

def get_order_status_by_email(email):
    response = requests.get(f"{orders_url}?email={email}&sort=date_created:desc&limit=1", headers={
        "Accept": "application/json",
        "X-Auth-Client": client_id,
        "X-Auth-Token": access_token
    })
    print(f'email: {email}')
    print('email: status code')
    print(response.status_code)
    if response.status_code != 200:
        return None, None

    orders = response.json()
    order = orders[0]
    order_id = int(orders[0]["id"])
    if order["status"] != "Shipped" and order["status"] != "Completed":
        return order["status"], None

    tracking_link = get_tracking_number_by_order_id(int(order_id))
    return order["status"], tracking_link

# Define a webhook endpoint for Dialog Flow
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    req = request.get_json(force=True)
    action = req.get("queryResult").get("action")
    if action == "check_order_status":
        parameters = req.get("queryResult").get("parameters")
        order_id = parameters.get("order_id") if parameters.get("order_id") else None
        email = parameters.get("email") if "email" in parameters else None
        if (order_id is not None):
            order_status, tracking_link = get_order_status_by_order_id(order_id)
        elif(email is not None):
            order_status, tracking_link = get_order_status_by_email(email)
        # ---
        if tracking_link is None:
            if order_status is None:
                response_text = "I'm sorry, I couldn't find any shipping information for that order."
            else:
                if (order_status == "Shipped" or order_status == "Completed"):
                    response_text = f"Great news! Your order is already {'Delivered' if order_status == 'Completed' else order_status }."
                else:  
                    response_text = f"Your order status is {order_status}."
        else:
            response_text = f"Great news! Your order has shipped! Here's the tracking information: \n{tracking_link}"
        response_text += "\n\n Is there anything else I can help you with?"
    else:
        response_text = "I'm sorry, I don't understand. Could you provide more information?"
    
    response = { "fulfillmentText": response_text  }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
