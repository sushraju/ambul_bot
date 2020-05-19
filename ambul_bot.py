"""
NewsBot uses twitter and newsapi
"""

# !/usr/bin/env python
import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime
import random
import pytz
import tweepy
from newsapi import NewsApiClient
from utils import get_config


class NewsBot():
    """
    NewsBot uses twitter and newsapi
    """

    def __init__(self):
        """
        Initialize the twitter and news api using config data in json
        """
        self.config_data = get_config()

        # initialize twitter api
        auth = tweepy.OAuthHandler(self.config_data['auth']['api_key'],
                                   self.config_data['auth']['api_secret_key'])
        auth.set_access_token(self.config_data['auth']['access_token'],
                              self.config_data['auth']['access_token_secret'])

        self.twitter_api = tweepy.API(auth)
        try:
            self.twitter_api.verify_credentials()
        except ValueError:
            LOGGER.error("Error while authenticating to twitter")
            self.twitter_api = None

        try:
            self.news_api = NewsApiClient(self.config_data['news']['api_key'])
            self.news_sources = self.config_data['news']['sources'].split(',')
        except ValueError:
            LOGGER.error("Error while authenticating to news api")
            self.news_api = None

    def get_twitter_api(self):
        """ getter for twitter api """
        return self.twitter_api

    def get_news_api(self):
        """ getter for news api """
        return self.news_api

    def get_news_sources(self):
        """ getter for news sources """
        return self.news_sources


global LOGGER
# initialize logging
LOGGER = logging.getLogger("Rotating Log")


def main():
    """ Starts here """

    LOGGER.setLevel(logging.DEBUG)

    # add a rotating handler
    handler = RotatingFileHandler('ambul_bot.log', maxBytes=536870912, backupCount=5)
    LOGGER.addHandler(handler)

    ambul_bot = NewsBot()

    pst = pytz.timezone('America/Los_Angeles')
    curr_utc_time = datetime.utcnow()
    to_utc_time = pytz.UTC.localize(curr_utc_time)
    to_pst_time = to_utc_time.astimezone(pst)

    # fetch news
    if ambul_bot.news_api:
        sources = ambul_bot.news_sources[random.randint(0, len(ambul_bot.news_sources) - 1)] + ',' + \
                  ambul_bot.news_sources[random.randint(0, len(ambul_bot.news_sources) - 1)] + ',' + \
                  ambul_bot.news_sources[random.randint(0, len(ambul_bot.news_sources) - 1)]

        all_articles = ambul_bot.news_api.get_everything(sources=sources,
                                                         from_param=str(to_pst_time.date()),
                                                         to=str(to_pst_time.date()),
                                                         language='en',
                                                         sort_by='relevancy',
                                                         page=1)
    else:
        LOGGER.error("Error while accessing news api, will try next time.")
        sys.exit(1)

    # update status by using article_url in the articles list
    for article in all_articles['articles']:
        if ambul_bot.twitter_api:
            try:
                LOGGER.debug(article['url'])
                ambul_bot.twitter_api.update_status(article['url'])
            except tweepy.TweepError:
                # not the ideal way to deal with it, ignoring and moving forward for now.
                continue
        else:
            LOGGER.warning("Error accessing twitter API")


if __name__ == "__main__":
    main()
