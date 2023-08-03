import os
import re
import time
import sys
import json
import requests
import configparser
import argparse
import logging
import tweepy
import tracery
import keep_alive
from tracery.modifiers import base_english
from datetime import datetime

version = "v4.4"

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
        keep_alive.keep_alive()
        print("####---> Running in replit mode...")
        time.sleep(2)
    elif using_replit.lower() == "false":
        print("####---> Running in local/server mode...")
    else:
        print("####---> Please set 'using_server' value in setting file to 'True' or 'False'")
        sys.exit()

def init_twitter_client():
    """Initialising Twitter API Client"""
    # Getting Twitter API Keys
    consumer_key = settings["consumer_key"] if settings["consumer_key"] != "" else os.getenv("consumer_key")
    consumer_secret = settings["consumer_secret"] if settings["consumer_secret"] != "" else os.getenv("consumer_secret")
    access_token = settings["access_token"] if settings["access_token"] != "" else os.getenv("access_token")
    access_token_secret = settings["access_token_secret"] if settings["access_token_secret"] != "" else os.getenv("access_token_secret")
    print("####---> Obtained Credentials...")

    auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    api_v1 = tweepy.API(auth)
    api_v2 = tweepy.Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret)
    return api_v1, api_v2

def get_imgs(api_v1,imgs):
    """Downloads images from url list and returns image filepaths"""
    media_ids = []
    for img in imgs:
        try:
            filepath = f"temp-imgs/{img.rsplit('/',1)[1]}"
            request = requests.get(url=img, stream=True,timeout=60)
            with open (filepath, 'wb') as image:
                for chunk in request:
                    image.write(chunk)
            media_id = upload_to_twitter(api_v1, filepath)
            media_ids.append(media_id)
        except Exception as error:
            add_to_log(f"{error} for image {img}")
            backup_file = "temp-imgs/unavailable.jpg"
            media_id = upload_to_twitter(api_v1, backup_file)
            media_ids.append(media_id)
        finally:
            if os.path.isfile(filepath):
                os.remove(filepath)
    return media_ids

def upload_to_twitter(api_v1,img):
    """Handles uploading media to twitter using API v1"""
    media = api_v1.media_upload(img)
    return media.media_id

def post_to_twitter(api_v2,quote,include_datetime,media_ids=None):
    """Handles posting to twitter (with or without media)"""
    if include_datetime.lower() == 'true':
        quote = (f"[{str(datetime.now()).rsplit(':',1)[0]}]\n\n") + quote
    tweet = api_v2.create_tweet(media_ids=media_ids,text=quote)
    print(f'\n####---> Posted: ID={tweet[0]["id"]}, QUOTE={quote}')

def tracery_magic():
    """Opening json and applying tracery magic.
        Also parses generated quotes to separate text and images."""
    with open("bot.json", 'r', encoding="utf-8") as quotesjson_raw:
        quotesjson = json.load(quotesjson_raw)
        grammar = tracery.Grammar(quotesjson)
        grammar.add_modifiers(base_english)
        quote = grammar.flatten("#origin#")
    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+',' '.join(raw_img_links))
    return parsed_quote,imgs

def add_to_log(error):
    """Adds a new entry to the logfile"""
    logging.basicConfig(filename="bot.log",format='\n%(asctime)s %(message)s',filemode='a')
    error_string = f'An error has occured: {error}'
    print(f'####---> {error_string}')
    logging.exception(error_string)

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
    """The main function for the bot.
        This runs everything in the order that it is supposed to run"""

    # Performing a version check before running anything else
    version_check()

    # Initialising base settings
    config_file = "settings"
    config = configparser.ConfigParser()
    config.read(config_file)
    global settings
    settings = config['BotSettings']
    using_replit = settings["using_replit"]
    time_between_tweets = int(settings["time_between_tweets"])
    include_datetime = settings["include_datetime"]
    api_v1, api_v2 = init_twitter_client()


    # Parsing Arguments
    args = parse_args(sys.argv[1:])
    if args.quote:
        quote,imgs = tracery_magic()
        print(quote,imgs)
        sys.exit()
    if args.tweet:
        quote,imgs = tracery_magic()
        if not imgs:
            post_to_twitter(api_v2,quote,include_datetime)
        else:
            media_ids = get_imgs(api_v1,imgs)
            post_to_twitter(api_v2,quote,include_datetime,media_ids)
        sys.exit()

    # Replit check & bot/API initialization
    replit_check(using_replit)
    print("####---> Starting bot...")
    print(f'####---> Time between tweets set to {time_between_tweets} seconds...')

    # The main loop of the bot
    while True:
        quote,imgs = tracery_magic()
        # Calculating time difference between tweets
        time_now = datetime.now()
        with open(config_file, 'r', encoding="utf-8") as settings_file:
            lines = settings_file.readlines()
        last_line_time_string = lines[-1].split("= ")[-1].split('\n')[0]
        last_tweet_time = datetime.strptime(last_line_time_string, "%Y-%m-%d %H:%M:%S.%f")
        time_diff = int(((time_now) - last_tweet_time).total_seconds())

        # Tweet decision based on time difference
        if time_diff >= time_between_tweets or "-" in str(time_diff):
            for count, num in enumerate(range(2), start=1):
                try:
                    if not imgs:
                        post_to_twitter(api_v2,quote,include_datetime)
                    else:
                        media_ids = get_imgs(api_v1,imgs)
                        post_to_twitter(api_v2,quote,include_datetime,media_ids)
                    lines[-1] = "last_tweet_time = " + str(time_now)
                    with open(config_file, 'w', encoding="utf-8") as settings_file:
                        settings_file.writelines(lines)
                    break
                except Exception as error:
                    add_to_log(error)
                    if count < 2:
                        retry_after = 2
                        print(f"####---> Retrying in {retry_after} seconds...")
                        time.sleep(retry_after)
            time.sleep(time_between_tweets)
        else:
            diff = time_between_tweets - time_diff
            print(f'####---> Sleeping for {diff} seconds...')
            time.sleep(diff)

# Runs the bot, all functions & everything
if __name__ == "__main__":
    main()
