#!/usr/bin/env python
import sys
import tweepy
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import pytz
from tweepy import TweepError

from utils import *
import logging
import logging.handlers


class NewsBot(object):

    def __init__(self):
        self.config_data = get_config()

        # initialize twitter api
        auth = tweepy.OAuthHandler(self.config_data['auth']['api_key'], self.config_data['auth']['api_secret_key'])
        auth.set_access_token(self.config_data['auth']['access_token'], self.config_data['auth']['access_token_secret'])

        self.twitter_api = tweepy.API(auth)
        try:
            self.twitter_api.verify_credentials()
        except ValueError:
            logging.ERROR("Error while authenticating to twitter")
            self.twitter_api = None

        try:
            self.news_api = NewsApiClient(self.config_data['news']['api_key'])
            self.news_sources = self.config_data['news']['sources']
        except ValueError:
            logging.ERROR("Error while authenticating to news api")
            self.news_api = None


def main():
    logging.basicConfig(filename='ambul_bot.log', level=logging.INFO)
    ambul_bot = NewsBot()

    pst = pytz.timezone('America/Los_Angeles')
    curr_utc_time = datetime.utcnow()
    to_utc_time = pytz.UTC.localize(curr_utc_time)
    to_pst_time = to_utc_time.astimezone(pst)

    if ambul_bot.news_api:
        all_articles = ambul_bot.news_api.get_everything(sources=ambul_bot.news_sources,
                                                         from_param=str(to_pst_time.date()),
                                                         to=str(to_pst_time.date()),
                                                         language='en',
                                                         sort_by='popularity',
                                                         page=5)
    else:
        logging.ERROR("Error while accessing news api, will try next time.")
        sys.exit(1)

    for article in all_articles['articles']:
        if ambul_bot.twitter_api:
            try:
                ambul_bot.twitter_api.update_status(article['url'])
            except tweepy.TweepError as t:
                continue
        else:
            logging.WARN("Error accessing twitter API")


if __name__ == "__main__":
    main()
