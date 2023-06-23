# Twitter Quotes Bot

* ### A Python bot that automatically tweets quotes/lyrics at regular intervals using the Twitter API.
* ### Can be deployed for free on [Replit](https://replit.com) or on your local machine or server.
* ### This is an alternative for those previously using CheapBotsDoneQuick to run their bot.
* ### This is a super simple version that is meant only for pure text tweets such as *posting quotes/lyrics hourly*. There is no support for *images/videos*. If you do need support for Images/Videos, please check out the repo mentioned in the *Credits* section down below.

## Setup:

1. Initial Set-up and installing the required packages:
   - If deploying on Replit:
     - Sign Up on [replit.com](https://replit.com)
     - On dashboard, click **Create Repl**
     - On the pop-up that opens, click **Import from GitHub** in top right corner
     - Paste the link to this repo in the space provided
     - Under Languages, it should now automatically select Python.
     - click **Import From GitHub** on bottom right corner of pop-up
     - Once done importing, follow steps **6 to 14** from [this guide](https://github.com/loonathedorm/Twitter-Quotes-Bot/blob/main/CBDQ-like%20Python%20Bot%20Hosting.pdf) to install required package and to obtain required twitter credentials
   - If deploying Locally or on a Server:
     - Clone this repo:
       ```
       git clone https://github.com/loonathedorm/Twitter-Quotes-Bot.git && cd Twitter-Quotes-Bot
       ```
     - Run the following command to install the required packages (Assuming you already have python installed):
       ```
       pip3 install tweepy flask
       ```
     - Follow steps **8 to 14** from [this guide](https://github.com/loonathedorm/Twitter-Quotes-Bot/blob/main/CBDQ-like%20Python%20Bot%20Hosting.pdf) to obtain required twitter credentials
2. Edit the `settings` file:
   - Enter your Twitter API credentials in the designated fields. API Key/Secret = Consumer Key/Secret
   - Set the time interval (in seconds) between each tweet. ***It is recommended to set it to 1800 or above if running the bot 24x7, as the API free tier limit is 1500 tweets per month.***
   - Set the value of `using_replit` to `False` if deploying the bot locally or on a server. If running on Replit, leave it as the default value (`True`).

3. Add your quotes/lyrics content:
   - Open the `bot.json` file.
   - Replace the sample quotes/lyrics already present in the file with your own content.
   - Each individual quote/lyric should be enclosed in double quotes "Like This" and separated by a comma as done in the sample content.
   - The bot.json file follows the format used in CheapBotsDoneQuick. So if you have an exisitng file from there, it can be used here directly.

## Usage:

- For Replit:
    - Hit **RUN** on the top to start the bot.
    - Now follow steps **19 to 23** from [this guide](https://github.com/loonathedorm/Twitter-Quotes-Bot/blob/main/CBDQ-like%20Python%20Bot%20Hosting.pdf) to setup monitoring for the bot. ***This is important as this is what stops the bot from turning off automatically***
- For Local/Server:
    - We'll use the `screen` command to run the bot in the background:
    ```shell
    # Make sure you have screen installed:
    sudo apt install screen

    # Start new session:
    screen -S TwitterBot

    # Run the bot:
    python3 main.py
    ```
    - Hit Ctrl+A+D to exit the screen session, the bot should continue to run in the background.
    - To get back to the bot you can use the command ```screen -r```
---

## Contact: 
- DM me on twitter [@loonathedorm](https://twitter.com/loonathedorm) for any assistance or create an issue here.

---

# Credits:
- This code is a super simplified and modified version of [@GuglioIsStupid](https://github.com/GuglioIsStupid/)'s **CBDQ-Python** bot that you can check out [here](https://github.com/GuglioIsStupid/CBDQ-Python).
- The PDF guide refered to in this repo is also by [@GuglioIsStupid](https://github.com/GuglioIsStupid/)
