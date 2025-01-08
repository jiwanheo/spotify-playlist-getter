import boto3
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta, timezone
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Spotify API base URL
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
SSM_CLIENT = boto3.client("ssm")
LAMBDA_CLIENT = boto3.client("lambda")

def get_access_token():
    """
    Retrieve the Spotify access token from AWS Systems Manager Parameter Store.
    If the token is missing or stale, invoke the SpotifyAuthLambda to refresh it.
    """
    try:
        # Try to fetch the token from Parameter Store
        token = SSM_CLIENT.get_parameter(Name="/spotify/access_token", WithDecryption=True)["Parameter"]["Value"]
        ttl = SSM_CLIENT.get_parameter(Name="/spotify/token_ttl")["Parameter"]["Value"]

        # Check if the token is stale
        token_expiration_time = datetime.fromisoformat(ttl)
        if datetime.now(timezone.utc) >= token_expiration_time:
            print("Access token is stale. Refreshing...")
            raise ValueError("Token is stale")  # Trigger a refresh

    except SSM_CLIENT.exceptions.ParameterNotFound:
        print("Access token not found in Parameter Store. Fetching a new token...")
        invoke_auth_lambda()
        # Retry fetching the token after it has been generated
        token = SSM_CLIENT.get_parameter(Name="/spotify/access_token", WithDecryption=True)["Parameter"]["Value"]
    except ValueError:
        # If the token is stale, invoke the auth lambda to refresh it
        invoke_auth_lambda()
        # Retry fetching the token after it has been generated
        token = SSM_CLIENT.get_parameter(Name="/spotify/access_token", WithDecryption=True)["Parameter"]["Value"]

    return token

def invoke_auth_lambda():
    """
    Invoke the SpotifyAuthLambda to refresh the token.
    """
    response = LAMBDA_CLIENT.invoke(
        FunctionName="spotify-auth-lambda",  # Update to match the exact name of your auth Lambda
        InvocationType="RequestResponse"
    )

    if response["StatusCode"] != 200:
        raise Exception("Failed to refresh token")
    print("Token refreshed successfully")
    
def make_spotify_request(endpoint, query_params=None):
    """
    Make a request to the Spotify API using the stored access token.
    """
    # Retrieve the access token
    token = get_access_token()
    
    # Set up the Authorization header with the Bearer token
    headers = {"Authorization": f"Bearer {token}"}

    # If query parameters are provided, format the URL accordingly
    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        url = f"{SPOTIFY_API_BASE_URL}{endpoint}?{query_string}"
    else:
        url = f"{SPOTIFY_API_BASE_URL}{endpoint}"

    # Make the request to Spotify's API
    request = urllib.request.Request(url, headers=headers)

    try:
        # Open the URL and get the response
        with urllib.request.urlopen(request) as response:
            response_data = response.read()
            return json.loads(response_data)
    except Exception as e:
        return {
            "error": str(e)
        }

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    try:

        # The endpoint to call on Spotify, e.g., '/search'
        endpoint = event["resource"]

        logger.info(f"endpoint: {endpoint}")

        # Get query parameters, if provided
        query_params = event.get("queryStringParameters", {})

        logger.info(f"query_params: {query_params}")

        endpoint_routes = {
            "/user_playlist": f"hello {endpoint}"
        }


        # Get response based on name, with a default value
        route = endpoint_routes[endpoint]

        
        logger.info(f"route: {route}")

        


        # # Make the request to Spotify API
        # response = make_spotify_request(route, query_params)

        # # Return the response as an API Gateway-friendly response
        # return {
        #     "statusCode": 200,
        #     "body": json.dumps(response),
        #     "headers": {
        #         "Content-Type": "application/json"
        #     }
        # }

        return {
            "statusCode": 200,
            "body": "Hello, World!"
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