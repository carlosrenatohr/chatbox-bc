
# Dialog Flow <> BigCommerce Integration for Chatbot :speech_balloon:

A project created with [Flask](https://flask.palletsprojects.com/en/2.3.x/) and using the [BigCommerce API](https://developer.bigcommerce.com/docs/rest-management) to work as the webhook required in the Dialog Flow project started where the chatbox is hosted for [B2C Candy Club](https://candy-club-sandbox.mybigcommerce.com/).


## Getting started

First of all, make sure you have Python 3.8 or higher installed on your machine and pip installed globally, which is a package manager for the language. 

After you clone the repo and move to the folder where the code is, you need to follow the next steps:


### Create a virtual environment

This is relevant to keep the dependencies isolated from your machine and avoid conflicts between them.

```bash
  python -m venv venv
```

### Install the dependencies


```bash
  pip install -r requirements.txt
```

Also, you need to crete your own `.env` file with the following variables:

```bash
  BIGCOMMERCE_STORE_HASH=
  BIGCOMMERCE_CLIENT_ID=
  BIGCOMMERCE_ACCESS_TOKEN=
```

## Running local

Once you have the dependencies installed, you can run the project locally with the following command:

```bash
  flask run --debug
```
OR 

```bash
  python -m flask --app app --debug run
```

This should start the server on port 5000. You can access the app on http://localhost:5000 and you can see the logs on the terminal.

However, Dialog Flow needs to be able to access the app, so you need to expose it to the internet. For that, you can use [ngrok](https://ngrok.com/) and link it to the port 5000. 

```bash
  ngrok http 5000
```

Take in account you need to have the app running locally before you run ngrok.

## Deploying to Heroku

You can deploy the app to Heroku with the following command:

Install Heroku CLI
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

Login to Heroku
```bash
  heroku login
```

Add Heroku remote to git
```bash
  heroku git remote add heroku https://git.heroku.com/chatbox-b2c-lambda.git
```


Deploy to Heroku

For new changes, what you need to do is add the changes to git, commit them and push them to Heroku remote.

```bash
  git add .
  git commit -m "Deploy to Heroku"
  git push heroku main
```
### Heroku Config Vars

In case they the config vars are not added to Heroku, you can add them with the following command:

```bash
  heroku config:set BIGCOMMERCE_STORE_HASH=your_store_hash
  heroku config:set BIGCOMMERCE_CLIENT_ID=your_client_id
  heroku config:set BIGCOMMERCE_ACCESS_TOKEN=your_access_token
```

### Heroku Logs

You can check the logs of the app running on Heroku with the following command:

```bash
  heroku logs --tail
```
OR 
    
Checking the logs on the [Heroku dashboard](https://dashboard.heroku.com/apps/chatbox-b2c-lambda/logs) of the app.