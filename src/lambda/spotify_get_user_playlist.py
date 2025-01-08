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
        # The endpoint to call on Spotify, e.g., '/search'
        endpoint = "/users/jiwanheo123/playlists"

        # # Get query parameters, if provided
        # query_params = event.get("queryStringParameters", {})

        # Make the request to Spotify API
        # response = make_spotify_request(endpoint, query_params)

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