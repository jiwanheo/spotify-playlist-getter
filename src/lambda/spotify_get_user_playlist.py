import boto3
import urllib.request
import urllib.parse
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

LAMBDA_CLIENT = boto3.client("lambda")

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    try:

        # Construct the Spotify API call here, and invoke spotify_api_request.py
        query_params = event.get("queryStringParameters", {})
        route = f"/users/{query_params['userId']}/playlists"

        event['route'] = route
        
        response = LAMBDA_CLIENT.invoke(
            FunctionName="spotify-api-request-lambda",  # Update to match the exact name of your auth Lambda
            InvocationType="RequestResponse",
            Payload=json.dumps(event)
        )

        logger.info(f"response: {response}")

        # Return the response as an API Gateway-friendly response
        return {
            "statusCode": 200,
            "body": json.dumps(response),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        # In case of errors, return a 500 error
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }