import boto3
import urllib.request
import urllib.parse
import base64
import json

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

    return token_data["access_token"], token_data["expires_in"]

# Test function
if __name__ == "__main__":
    token, ttl = get_spotify_token()
    print(f"Spotify API Token: {token}")
    print(f"Token Expires In: {ttl} seconds")
