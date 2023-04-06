import os
import json
import openai
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/webhook_ai', methods=['GET','POST'])
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
    