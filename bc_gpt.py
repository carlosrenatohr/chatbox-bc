import os
import json
import openai
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# openai.api_key = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

client_id = os.getenv("BIGCOMMERCE_CLIENT_ID")
access_token = os.getenv("BIGCOMMERCE_ACCESS_TOKEN")
store_hash = os.getenv("BIGCOMMERCE_STORE_HASH")

# Define the BigCommerce API endpoints
base_url = f"https://api.bigcommerce.com/stores/{store_hash}"
orders_url = f"{base_url}/v2/orders"

# Define a function to check if an order has shipped and get the tracking information
def get_tracking_info(order_id):
    response = requests.get(f"{orders_url}/{order_id}", headers={
        "Accept": "application/json",
        "X-Auth-Client": client_id,
        "X-Auth-Token": access_token
    })

    print(response.status_code)
    print(f"{orders_url}/{order_id}")
    if response.status_code != 200:
        return None, None

    order = response.json()
    if order["status"] != "Shipped":
        return order["status"], None

    shipments = requests.get(f"{orders_url}/{order_id}/shipments", headers={
            "Accept": "application/json",
            "X-Auth-Client": client_id,
            "X-Auth-Token": access_token
        })
    if shipments.status_code != 200:
        return None, None
    first_shipment = shipments.json()[0]
    print(first_shipment)
    tracking_info = first_shipment["tracking_number"]
    carrier = first_shipment["tracking_carrier"]
    # tracking_link = f"https://www.{carrier.lower()}.com/tracking/{tracking_info}"
    tracking_link = f"https://www.aftership.com/track/ups/{tracking_info}"
    print(tracking_link)
    return order["status"], tracking_link

# Define a webhook endpoint for Dialog Flow
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    req = request.get_json(force=True)
    action = req.get("queryResult").get("action")
    if action == "check_order_status":
        parameters = req.get("queryResult").get("parameters")
        order_id = int(parameters.get("order_id"))
        order_status, tracking_link = get_tracking_info(order_id)
        if tracking_link is None:
            if order_status is None:
                response_text = "I'm sorry, I couldn't find any shipping information for that order."
            else:
                response_text = f"Your order status is {order_status}."
        else:
            response_text = f"Your order has shipped! Here's the tracking information: {tracking_link}"
        response = {
            "fulfillmentText": response_text,
            "source": "webhook"
        }
    else:
        response = {"fulfillmentText": "I'm sorry, I don't understand. Could you provide more information?"}
    return jsonify(response)

    # order_id = data["queryResult"]["parameters"]["order_id"]
    order_id = data["order_id"]
    tracking_link = get_tracking_info(order_id)

    if tracking_link is None:
        response_text = "I'm sorry, I couldn't find any shipping information for that order."
    else:
        response_text = f"Your order has shipped! Here's the tracking information: {tracking_link}"

    response_data = {
        "fulfillmentText": response_text,
        "source": "webhook"
    }
    return response_data


@app.route('/webhook_ai', methods=['GET','POST'])
def webhook_ai():
    # Retrieve the JSON data from the request
    data = request.get_json()

    # Process the data using OpenAI's GPT-3
    call_ai()    
    print(response)
    return jsonify(final_message)
    
def call_ai():
    # Retrieve the JSON data from the request
    data = request.get_json()

    # Process the data using OpenAI's GPT-3
    model_engine = "text-davinci-002" #"davinci"
    # prompt = "Generate a response for the following text: " + data['text']
    prompt = data['text']
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=0.05,
        # max_tokens=1024,
        n=1,
        stop=None,
        timeout=30,
        frequency_penalty=0,
        presence_penalty=0
    )

    final_message = response.choices[0].text
    print(response)
    return jsonify(final_message)

if __name__ == '__main__':
    app.run(debug=True)
