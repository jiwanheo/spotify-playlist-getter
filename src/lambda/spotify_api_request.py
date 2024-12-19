import boto3
import urllib.request
import urllib.parse
import json

# Spotify API base URL
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

def get_access_token():
    """
    Retrieve the Spotify access token from AWS Systems Manager Parameter Store.
    """
    ssm_client = boto3.client("ssm")
    token = ssm_client.get_parameter(Name="/spotify/access_token", WithDecryption=True)["Parameter"]["Value"]
    return token

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
        endpoint = event["rawPath"]

        # Get query parameters, if provided
        query_params = event.get("queryStringParameters", {})

        # Make the request to Spotify API
        response = make_spotify_request(endpoint, query_params)

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
