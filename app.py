from fastapi import FastAPI, Request
import requests
import uvicorn
import json
 
app = FastAPI()
 
# Define the target webhook URLs where you want to send the modified JSON
TARGET_WEBHOOK_URL_1 = 'https://webhook.site/a98f6beb-e975-4af1-9083-991be92600b4'
TARGET_WEBHOOK_URL_2 = 'https://webhook.site/a98f6beb-e975-4af1-9083-991be92600b4'
 
# GET method to return a simple response for testing
@app.get("/receive-json")
async def get_json():
    return {
        'status': 'success',
        'message': 'This is a GET request. Use POST to send JSON data.'
    }
 
# POST method to receive and modify JSON
@app.post("/receive-json")
async def receive_json(request: Request):
    try:
        # Read raw data from the request body
        raw_data = await request.body()
 
        # Convert bytes to string and remove leading '%' if present
        json_string = raw_data.decode('utf-8').lstrip('%')
 
        # Parse the string into a Python dictionary (JSON)
        incoming_json = json.loads(json_string)
 
        # Create a modified payload by replacing '%' with an empty string
        def replace_percent(value):
            if isinstance(value, str):
                return value.replace('%', '')
            elif isinstance(value, dict):
                return {k: replace_percent(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_percent(item) for item in value]
            else:
                return value
 
        modified_json = replace_percent(incoming_json)
 
        # Send the modified JSON to the target webhook URLs
        try:
            response_1 = requests.post(TARGET_WEBHOOK_URL_1, json=modified_json)
            response_1.raise_for_status()  # Raise an exception for HTTP errors
        except requests.RequestException as e:
            return {'status': 'error', 'message': f'Failed to send to webhook 1: {str(e)}'}
 
        try:
            response_2 = requests.post(TARGET_WEBHOOK_URL_2, json=modified_json)
            response_2.raise_for_status()  # Raise an exception for HTTP errors
        except requests.RequestException as e:
            return {'status': 'error', 'message': f'Failed to send to webhook 2: {str(e)}'}
 
        # Return a success response to the original sender
        return {
            'status': 'success',
            'message': 'JSON forwarded successfully to both webhooks',
            'target_response_1': response_1.text,
            'target_response_2': response_2.text
        }
 
    except Exception as e:
        # Handle exceptions
        return {'status': 'error', 'message': str(e)}
 
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
 
 
