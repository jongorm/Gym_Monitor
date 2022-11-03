"""
Put data in a dictionary
when job completes, convert dictionary
to pandas datafrae

timeout
"""

import requests
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
import lxml
import logging
import datetime
import pytz
import selenium.webdriver.chrome.options import Options

SITE_URL = "https://www.vitalclimbinggym.com/brooklyn"

class ExtractHeadCount:

    def __init__(self):
        self.current_time = self._get_current_time()

    def _get_current_time(self):
        """
        :returns: the current timestamp objects
        that is utc timezone aware.
        """
        return datetime.datetime.now(tz=pytz.utc)

    def get_response(self, link : str, parser='lxml'):
        """
        :param link: link for website being queried
        :param parser:  html parser, default lxml
        :returns: BeautifulSoup object with HTML lines
        """
        timestamp_formatted = self.current_time.iso_format()

        try:
            response_soup = None
            response = requests.get(link, timeout=5)
            response.raise_for_status()
            response_soup = BeautifulSoup(response.content, parser)
        except requests.Timeout:
            logging.debug(f"ERROR: timeout limit reached for response \
                at time: {timestamp_formatted}")
        except requests.HTTPError:
            logging.debug(f"ERROR: status code {response.status_code} \
                raised error for response {timestamp_formatted}")
        except Exception as e:
            logging.debug(f"ERROR: an exception was raised of type {e} \
                for response: {timestamp_formatted}")

        if not response_soup:
            return None

        return response_soup

    def extract_data(self, response : str):
        """
        :param response: html string
        :returns: the desired data from the webpage
        """
        if not response:
            return None
        
        head_count_pattern = re.compile(r'<span\sid="currocc">(\d{3})')
        head_count = re.search(head_count_pattern, str(response)).group(1)

        return head_count

    def create_table(self):

    def enhance_table(self):

    def main(self):


if __name__ == "__main__":
    ExtractHeadCount.main()
            

