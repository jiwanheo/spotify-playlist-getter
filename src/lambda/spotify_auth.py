import boto3
import urllib.request
import urllib.parse
import base64
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

def get_spotify_credentials():
    """
    Retrieve Spotify API credentials from AWS Systems Manager Parameter Store.
    """

    ssm_client = boto3.client("ssm")
    client_id = ssm_client.get_parameter(Name="/spotify/client_id", WithDecryption=True)["Parameter"]["Value"]
    client_secret = ssm_client.get_parameter(Name="/spotify/client_secret", WithDecryption=True)["Parameter"]["Value"]
    return client_id, client_secret

def get_spotify_token():
    """
    Generate Spotify API token using client credentials and urllib.
    """
    client_id, client_secret = get_spotify_credentials()

    # Encode credentials for Basic Auth
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")

    # Prepare the request payload
    payload = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")

    # Prepare and send the HTTP request
    request = urllib.request.Request(
        SPOTIFY_TOKEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }
    )

    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        token_data = json.loads(response_data)
        print(f"token_data: {token_data}")

    return token_data["access_token"], token_data["expires_in"]

def store_token_in_parameter_store(token, ttl):
    """
    Store the Spotify token and its TTL in AWS Systems Manager Parameter Store.
    """
    ssm_client = boto3.client("ssm")
    # Store the token
    ssm_client.put_parameter(
        Name="/spotify/access_token",
        Value=token,
        Type="SecureString",
        Overwrite=True
    )
    # Store the token expiration time
    ssm_client.put_parameter(
        Name="/spotify/token_ttl",
        Value=str(ttl),
        Type="String",
        Overwrite=True
    )

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    try:
        token, ttl = get_spotify_token()
        print(f"From auth: ttl: {ttl}")
        store_token_in_parameter_store(token, ttl)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Token stored successfully",
                "access_token": token,
                "expires_in": ttl
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
