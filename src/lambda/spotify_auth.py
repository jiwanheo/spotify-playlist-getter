import boto3
import requests

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
    Generate Spotify API token using client credentials.
    """
    client_id, client_secret = get_spotify_credentials()
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"], token_data["expires_in"]

# Test function
if __name__ == "__main__":
    token, ttl = get_spotify_token()
    print(f"Spotify API Token: {token}")
    print(f"Token Expires In: {ttl} seconds")
