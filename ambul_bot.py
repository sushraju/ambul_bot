#!/usr/bin/env python
import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime
import pytz
import tweepy
import random
from newsapi import NewsApiClient
from utils import get_config

"""
NewsBot uses twitter and newsapi
"""

global logger
# initialize logging
logger = logging.getLogger("Rotating Log")


class NewsBot(object):

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
            logger.error("Error while authenticating to twitter")
            self.twitter_api = None

        try:
            self.news_api = NewsApiClient(self.config_data['news']['api_key'])
            self.news_sources = self.config_data['news']['sources'].split(',')
        except ValueError:
            logger.error("Error while authenticating to news api")
            self.news_api = None


def main():
    logger.setLevel(logging.DEBUG)

    # add a rotating handler
    handler = RotatingFileHandler('ambul_bot.log', maxBytes=536870912, backupCount=5)
    logger.addHandler(handler)

    ambul_bot = NewsBot()

    pst = pytz.timezone('America/Los_Angeles')
    curr_utc_time = datetime.utcnow()
    to_utc_time = pytz.UTC.localize(curr_utc_time)
    to_pst_time = to_utc_time.astimezone(pst)

    # fetch news
    if ambul_bot.news_api:
        sources = ambul_bot.news_sources[random.randint(0, len(ambul_bot.news_sources)-1)] + ',' + \
                  ambul_bot.news_sources[random.randint(0, len(ambul_bot.news_sources)-1)] + ',' + \
                  ambul_bot.news_sources[random.randint(0, len(ambul_bot.news_sources)-1)]
        
        all_articles = ambul_bot.news_api.get_everything(sources=sources,
                                                         from_param=str(to_pst_time.date()),
                                                         to=str(to_pst_time.date()),
                                                         language='en',
                                                         sort_by='relevancy',
                                                         page=1)
    else:
        logger.error("Error while accessing news api, will try next time.")
        sys.exit(1)

    # update status by using article_url in the articles list
    for article in all_articles['articles']:
        if ambul_bot.twitter_api:
            try:
                logger.debug(article['url'])
                ambul_bot.twitter_api.update_status(article['url'])
            except tweepy.TweepError:
                # debug
                # print(article['url'])
                continue
        else:
            logger.warning("Error accessing twitter API")


if __name__ == "__main__":
    main()
