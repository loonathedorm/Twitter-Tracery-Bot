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
from colorama import Fore, Back, Style
from tracery.modifiers import base_english
from datetime import datetime

version = "v4.7.8"

def version_check():
    """Check for latest version"""
    latest_version = requests.get("https://raw.githubusercontent.com/loonathedorm/Twitter-Tracery-Bot/main/version", timeout=10)
    if latest_version.text != version:
        print(Fore.GREEN + f"\n\n####---> Current Version = {version}, Latest Version = {latest_version.text}")
        print("\n####---> Please wait while the bot updates itself...\n" + Style.RESET_ALL)
        time.sleep(1)
        os.system('git stash && git pull && git stash pop')
        print(Fore.GREEN + "\n####---> UPDATE PROCESS COMPLETE! Please Re-Run the bot to continue...\n" + Style.RESET_ALL)
        sys.exit()
    else:
        print(Fore.GREEN + f"####---> Current Version = {version}" + Style.RESET_ALL)

def replit_check(using_replit):
    """Checking for server or replit mode"""
    if using_replit.lower() == "true":
    # Running flask web server to indicate bot status
        keep_alive.keep_alive()
        print(Fore.GREEN + "####---> Running in replit mode..." + Style.RESET_ALL)
        time.sleep(2)
    elif using_replit.lower() == "false":
        print(Fore.GREEN + "####---> Running in local/server mode..." + Style.RESET_ALL)
    else:
        print(Back.RED + Fore.BLACK + "####---> Please set 'using_server' value in setting file to 'True' or 'False'" + Style.RESET_ALL)
        sys.exit()

def init_twitter_client():
    """Initialising Twitter API Client"""
    # Getting Twitter API Keys
    consumer_key = settings["consumer_key"] if settings["consumer_key"] != "" else os.getenv("consumer_key")
    consumer_secret = settings["consumer_secret"] if settings["consumer_secret"] != "" else os.getenv("consumer_secret")
    access_token = settings["access_token"] if settings["access_token"] != "" else os.getenv("access_token")
    access_token_secret = settings["access_token_secret"] if settings["access_token_secret"] != "" else os.getenv("access_token_secret")
    print(Fore.GREEN + "####---> Obtained Credentials..." + Style.RESET_ALL)

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
            media = api_v1.media_upload(filepath)
            media_ids.append(media.media_id)
        except Exception as error:
            log_string = f"{error} for image {img}"
            add_to_log(log_string)
            backup_file = "temp-imgs/unavailable.jpg"
            media = api_v1.media_upload(backup_file)
            media_ids.append(media.media_id)
        finally:
            if os.path.isfile(filepath):
                os.remove(filepath)
    return media_ids

def post_to_twitter(api_v2,quote,include_datetime,media_ids=None):
    """Handles posting to twitter (with or without media)"""
    if include_datetime.lower() == 'true':
        quote = (f"[{str(datetime.now()).rsplit(':',1)[0]}]\n\n") + quote
    tweet = api_v2.create_tweet(media_ids=media_ids,text=quote)
    print(Fore.GREEN + f'\n####---> Posted: ID={tweet[0]["id"]}, QUOTE={quote}' + Style.RESET_ALL)

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

def init_logger():
    """Initializes the logger"""
    logger = logging.getLogger("Twitter-Bot")
    log_format = logging.Formatter('\n%(asctime)s %(message)s')
    log_file = logging.FileHandler('bot.log')
    log_file.setFormatter(log_format)
    logger.addHandler(log_file)
    return logger

def add_to_log(log_string):
    """Adds a new entry to the logfile"""
    print(Fore.YELLOW + f'####---> {log_string}' + Style.RESET_ALL)
    logger.exception(log_string)

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
    global logger
    logger = init_logger()
    api_v1, api_v2 = init_twitter_client()

    # Parsing Arguments
    args = parse_args(sys.argv[1:])
    if args.quote:
        quote,imgs = tracery_magic()
        print(Fore.BLUE + f'\n{quote},{imgs}\n' + Style.RESET_ALL)
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
    print(Fore.GREEN + "####---> Starting bot..." + Style.RESET_ALL)
    print(Fore.GREEN + f'####---> Time between tweets set to {time_between_tweets} seconds...' + Style.RESET_ALL)

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
                    log_string = f'An error has occured: {error}'
                    add_to_log(log_string)
                    if count < 2:
                        quote,imgs = tracery_magic()
                        retry_after = 30
                        print(Back.RED + Fore.BLACK + f"####---> Retrying in {retry_after} seconds..." + Style.RESET_ALL)
                        time.sleep(retry_after)
            time.sleep(time_between_tweets)
        else:
            diff = time_between_tweets - time_diff
            print(Fore.GREEN + f'####---> Sleeping for {diff} seconds...' + Style.RESET_ALL)
            time.sleep(diff)

# Runs the bot, all functions & everything
if __name__ == "__main__":
    main()
