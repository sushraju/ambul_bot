import unittest
from ambul_bot import NewsBot


class TestBot(unittest.TestCase):

    def test_twitter_api(self):
        nb = NewsBot()
        self.assertFalse(nb is None)
        self.assertFalse(nb.twitter_api is None)

    def test_news_api(self):
        nb = NewsBot()
        self.assertFalse(nb is None)
        self.assertFalse(nb.news_api is None)


if __name__ == "__main__":
    unittest.main()
