import os
import time
import sys
import json
import requests
import configparser
import argparse
import tweepy
import tracery
from tracery.modifiers import base_english
from datetime import datetime

version = "v3.4"

def version_check():
    """Check for latest version"""
    latest_version = requests.get("https://raw.githubusercontent.com/loonathedorm/Twitter-Quotes-Bot/main/version", timeout=10)
    if latest_version.text != version:
        print(f"####---> Current Version = {version}, Latest Version = {latest_version.text}")
        print("####---> Please update the bot to continue with latest fixes and features.")
        print("####---> To update, type 'git pull' and hit enter inside the shell tab and then restart the bot.")
        sys.exit()
    else:
        print(f"####---> Current Version = {version}")

def replit_check(using_replit):
    """Checking for server or replit mode"""
    if using_replit.lower() == "true":
    # Running flask web server to indicate bot status
        import keep_alive
        keep_alive.keep_alive()
        print("####---> Running in replit mode...")
    elif using_replit.lower() == "false":
        print("####---> Running in local/server mode...")
    else:
        print("####---> Please set 'using_server' value in setting file to 'True' or 'False'")
        sys.exit()

def init_twitter_client(settings):
    """Initialising Twitter API Client"""
    # Getting Twitter API Keys
    consumer_key = settings["consumer_key"] if settings["consumer_key"] != "" else os.getenv("consumer_key")
    consumer_secret = settings["consumer_secret"] if settings["consumer_secret"] != "" else os.getenv("consumer_secret")
    access_token = settings["access_token"] if settings["access_token"] != "" else os.getenv("access_token")
    access_token_secret = settings["access_token_secret"] if settings["access_token_secret"] != "" else os.getenv("access_token_secret")
    print("####---> Obtained Credentials...")

    Client = tweepy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret)
    return Client

def post_to_twitter(Client,quote):
    """Posts text to twitter"""
    tweet = Client.create_tweet(text=quote)
    print(f'\n####---> Posted: ID={tweet[0]["id"]}, QUOTE={quote}')

def tracery_magic():
    """Opening json and applying tracery magic"""
    with open("bot.json", 'r', encoding="utf-8") as quotesjson_raw:
        quotesjson = json.load(quotesjson_raw)
        grammar = tracery.Grammar(quotesjson)
        grammar.add_modifiers(base_english)
        quote = grammar.flatten("#origin#")
    return quote

def parse_args(args):
    """Parse arguments given to the bot"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--quote",
                        help="Prints out a single quote by parsing the json file",
                        action="store_true")
    parser.add_argument("--tweet",
                        help="Posts a tweet to twitter regardless of time interval",
                        action="store_true")
    return parser.parse_args(args)

def main():
    """The main function of the bot."""

    # Performing a version check before running anything else
    version_check()

    # Initialising base settings
    config_file = "settings"
    config = configparser.ConfigParser()
    config.read(config_file)
    settings = config['BotSettings']

    # Parsing Arguments
    args = parse_args(sys.argv[1:])
    if args.quote:
        quote = tracery_magic()
        print(quote)
        sys.exit()
    if args.tweet:
        quote = tracery_magic()
        Client = init_twitter_client(settings)
        post_to_twitter(Client,quote)
        sys.exit()

    # Replit check & bot/API initialization
    using_replit = settings["using_replit"]
    replit_check(using_replit)
    print("####---> Starting bot...")
    time_between_tweets = int(settings["time_between_tweets"])
    print(f'####---> Time between tweets set to {time_between_tweets} seconds...')
    Client = init_twitter_client(settings)

    # The main loop of the bot
    try:
        while True:
            quote = tracery_magic()
            # Calculating time difference between tweets
            time_now = datetime.now()
            with open(config_file, 'r', encoding="utf-8") as settings_file:
                lines = settings_file.readlines()
            last_line_time_string = lines[-1].split("= ")[-1].split('\n')[0]
            last_tweet_time = datetime.strptime(last_line_time_string, "%Y-%m-%d %H:%M:%S.%f")
            time_diff = int(((time_now) - last_tweet_time).total_seconds())

            # Tweet decision based on time difference
            if time_diff >= time_between_tweets or "-" in str(time_diff):
                post_to_twitter(Client,quote)
                lines[-1] = "last_tweet_time = " + str(time_now)    
                with open(config_file, 'w', encoding="utf-8") as settings_file:
                    settings_file.writelines(lines)
                time.sleep(time_between_tweets)
            else:
                diff = time_between_tweets - time_diff
                print(f'####---> Sleeping for {diff} seconds...')
                time.sleep(diff)
    except Exception as error:
        print(f'An error has occured: {error}')
        sys.exit()

# Runs the bot, all functions & everything
if __name__ == "__main__":
    main()
