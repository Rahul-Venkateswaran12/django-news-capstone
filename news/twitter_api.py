import requests
import time
from requests_oauthlib import OAuth1Session
import os
import json


class TwitterAPI:
    """API for interacting with Twitter (X) for posting tweets."""
    CONSUMER_KEY = 'CONS_KEY'
    CONSUMER_SECRET = 'CONS_SECRET'

    def __init__(self):
        self.oauth = OAuth1Session(self.CONSUMER_KEY, client_secret=self.CONSUMER_SECRET)
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        token_file = "twitter_tokens.json"
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                return json.load(f)
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        try:
            fetch_response = self.oauth.fetch_request_token(request_token_url)
            resource_owner_key = fetch_response.get("oauth_token")
            resource_owner_secret = fetch_response.get("oauth_token_secret")
            authorize_url = f"https://api.twitter.com/oauth/authorize?oauth_token={resource_owner_key}"
            print(f"Please authorize: {authorize_url}")
            verifier = input("Enter PIN: ")
            access_token_url = "https://api.twitter.com/oauth/access_token"
            self.oauth = OAuth1Session(
                self.CONSUMER_KEY,
                client_secret=self.CONSUMER_SECRET,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                verifier=verifier
            )
            access_token = self.oauth.fetch_access_token(access_token_url)
            with open(token_file, 'w') as f:
                json.dump(access_token, f)
            return access_token
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

    def post_tweet(self, text, media_url=None):
        """Posts a tweet with optional media."""
        if not self.access_token:
            print("No access token available")
            return "Authentication failed"
        oauth = OAuth1Session(
            self.CONSUMER_KEY,
            client_secret=self.CONSUMER_SECRET,
            resource_owner_key=self.access_token['oauth_token'],
            resource_owner_secret=self.access_token['oauth_token_secret']
        )
        tweet_url = "https://api.twitter.com/2/tweets"
        payload = {"text": text}
        if media_url:
            media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            media_data = requests.get(media_url).content
            media_response = oauth.post(media_upload_url, files={'media': media_data})
            if media_response.status_code == 200:
                media_id = media_response.json()['media_id_string']
                payload['media'] = {'media_ids': [media_id]}
            else:
                print(f"Media upload failed: {media_response.text}")
        response = oauth.post(tweet_url, json=payload)
        if response.status_code == 201:
            print("Tweet posted successfully")
            return "Tweet posted!"
        print(f"Tweet failed: {response.status_code} - {response.text}")
        return f"Error: {response.text}"


def tweet_new_article(article):
    twitter = TwitterAPI()
    text = (
        f"New Article: {article.title} - "
        f"{article.content[:100]}..."
    )
    return twitter.post_tweet(text)


def tweet_new_newsletter(newsletter):
    twitter = TwitterAPI()
    text = (
        f"New Newsletter: {newsletter.title} - "
        f"{newsletter.content[:100]}..."
    )
    return twitter.post_tweet(text)
