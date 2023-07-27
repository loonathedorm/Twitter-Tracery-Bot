import os
import time
import sys
import json
import requests
from datetime import datetime
import tweepy
import tracery
from tracery.modifiers import base_english
import configparser

version = "v2.1"

# Version check
latest_version = requests.get("https://raw.githubusercontent.com/loonathedorm/Twitter-Quotes-Bot/main/version")
if latest_version.text != version:
    print(f"####---> Current Version = {version}, Latest Version = {latest_version.text}")
    print("####---> Please update the bot to continue with latest fixes and features.")
    print("####---> To update, type 'git pull' and hit enter inside the shell tab and then restart the bot.")
    sys.exit()
else:
    print(f"####---> Current Version = {version}")

# Initialising settings file
config = configparser.ConfigParser()
config.read("settings")
settings = config['BotSettings']
time_between_tweets = int(settings["time_between_tweets"])
using_replit = settings["using_replit"]

# Checking for server or replit mode
if using_replit.lower() == "true":
  # Running flask web server to indicate bot status
    import keep_alive
    keep_alive.keep_alive()
    print("####---> Running in replit mode...")
elif using_replit.lower() == "false":
    print("Running in local/server mode...")
else:
    print("Please set 'using_server' value in setting file to 'True' or 'False'")
    sys.exit()

# Getting Twitter API Keys
consumer_key = settings["consumer_key"] if settings["consumer_key"] != "" else os.getenv("consumer_key")
consumer_secret = settings["consumer_secret"] if settings["consumer_secret"] != "" else os.getenv("consumer_secret")
access_token = settings["access_token"] if settings["access_token"] != "" else os.getenv("access_token")
access_token_secret = settings["access_token_secret"] if settings["access_token_secret"] != "" else os.getenv("access_token_secret")
print("####---> Obtained Credentials...")

# Initialising Twitter API Client
Client = tweepy.Client(consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret)

print("####---> Starting loop...")

# Main Loop that selects random quote and posts it on Twitter
print(f'####---> Time between tweets set to {time_between_tweets} seconds...')

with open("bot.json", 'r', encoding="utf-8") as quotesjson_raw:
    quotesjson = json.load(quotesjson_raw)
    grammar = tracery.Grammar(quotesjson)
    grammar.add_modifiers(base_english)

while True:
    quote = grammar.flatten("#origin#")
    # Calculating time difference between tweets
    time_now = datetime.now()
    with open("settings", 'r', encoding="utf-8") as settings_file:
        lines = settings_file.readlines()
    last_line_time_string = lines[-1].split("= ")[-1].split('\n')[0]
    last_tweet_time = datetime.strptime(last_line_time_string, "%Y-%m-%d %H:%M:%S.%f")
    time_diff = int(((time_now) - last_tweet_time).total_seconds())

    # Tweet decision based on time difference
    if time_diff >= time_between_tweets or "-" in str(time_diff):
        tweet = Client.create_tweet(text=quote)
        print(f'\n####---> Posted: ID={tweet[0]["id"]}, QUOTE={quote}')
        quotesjson_raw.close()
        lines[-1] = "last_tweet_time = " + str(time_now)    
        with open("settings", 'w', encoding="utf-8") as settings_file:
            settings_file.writelines(lines)
        time.sleep(time_between_tweets)
    else:
        diff = time_between_tweets - time_diff
        print(f'####---> Sleeping for {diff} seconds...')
        time.sleep(diff)
