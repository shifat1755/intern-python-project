from pyjokes import get_joke
from util import NetworkRequest, retry_with_token_refresh
from getpass import getpass
from time import sleep, time

def login():
    print("Please login to your account..")
    network_request = NetworkRequest()
    username = input("Username: ")
    password = getpass("Password: ")
    print("loggin in ...")
    response = network_request.post("/api/auth", {
        "username": username,
        "password": password
    })
    if response.get('code') == 200:
        print("log in successful")
        return response['body']
    else:
        print("Login failed:", response.get('error'))
        return None

@retry_with_token_refresh
def fetch_tweets(headers):
    print("checking recent tweets ...")
    start_time = time()
    response = NetworkRequest.get("/api/tweets", headers=headers)
    end_time = time()
    print(f"(time taken: {(end_time - start_time) * 1000:.4f} ms)")
    return response

def main():
    user = login()
    if not user:
        return

    access_token = user['access_token']
    refresh_token = user['refresh_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = fetch_tweets(headers=headers, refresh_token=refresh_token)

    if response.get('code') != 200:
        print("Failed to fetch tweets:", response.get('error'))
        return

    tweets = response['body'][:5]
    for i, tweet in enumerate(tweets[::-1], start=20):
        print(f"({tweet['id']}) {tweet['author']['firstname'].title()} tweeted at {tweet['created_at']}:")
        print(f"{tweet['text']}\n")

    posted_jokes = set()
    for i in range(2):
        joke = None
        while not joke or joke in posted_jokes:
            joke = get_joke()
        posted_jokes.add(joke)

        print("posting tweet..")
        start_time = time()
        post_response = NetworkRequest.post("/api/tweets", {"text": joke}, headers=headers)
        end_time = time()

        if post_response.get('code') == 201:
            print(f"(time taken: {(end_time - start_time) * 1000:.4f} ms)")
            print("posted tweet. sleeping 1 min now\n")
        else:
            print(f"Failed to post tweet {i + 1}: {post_response.get('error')}")

        sleep(60)

if __name__ == '__main__':
    main()
