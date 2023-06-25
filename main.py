import os, json, tweepy, time, random
import configparser

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
  print("Running in replit mode...")
elif using_replit.lower() == "false":
  print("Running in local/server mode...")
else:
  print("Please set 'using_server' value in setting file to 'True' or 'False'")
  exit()

# Getting Twitter API Keys
consumer_key = settings["consumer_key"] if settings["consumer_key"] != "" else os.getenv("consumer_key")
consumer_secret = settings["consumer_secret"] if settings["consumer_secret"] != "" else os.getenv("consumer_secret")
access_token = settings["access_token"] if settings["access_token"] != "" else os.getenv("access_token")
access_token_secret = settings["access_token_secret"] if settings["access_token_secret"] != "" else os.getenv("access_token_secret")
print("Obtained Credentials...")

# Initialising Twitter API Client
Client = tweepy.Client(consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token=access_token,
                       access_token_secret=access_token_secret)

# Fetching raw quotes file
raw_quotes = "bot.json"
print("Starting loop...")

# Main Loop that selects random quote and posts it on Twitter
print(f'Time between tweets set to {time_between_tweets} seconds...')
while True:
  with open(raw_quotes, 'r') as quotesjson:
    quotesjson = json.load(quotesjson)
    quotes = []
    for quote in quotesjson["origin"]:
      quotes.append(quote)
    random.shuffle(quotes)
    for quote in quotes:
      tweet = Client.create_tweet(text=quote)
      print(f'\nPosted: ID={tweet[0]["id"]} QUOTE={quote}')
      time.sleep(time_between_tweets)
