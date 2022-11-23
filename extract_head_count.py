"""
Put data in a dictionary
when job completes, convert dictionary
to pandas datafrae

timeout
"""

import requests
import re
from bs4 import BeautifulSoup
import lxml
import logging
import datetime
import pytz


class ExtractHeadCount:

    def __init__(self, site_url):
        self.current_time = self._get_current_time()
        self.site_url = site_url

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
            #Get a response to confirm the page is working
            response = requests.get(link, timeout=5)
            response.raise_for_status()
            response_soup = BeautifulSoup(response)
        except requests.Timeout:
            logging.debug(f"ERROR: timeout limit reached for response \
                at time: {timestamp_formatted}")
        except requests.HTTPError:
            logging.debug(f"ERROR: status code {response.status_code} \
                raised error for response {timestamp_formatted}")
        except Exception as e:
            logging.debug(f"ERROR: an exception was raised of type '{e}' \
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
        
        head_count_pattern = re.compile(r'<body>(\d+)<body>')
        head_count = re.search(head_count_pattern, str(response)).group(1)

        if not head_count:
            logging.debug(f"NO COUNT: the head_count_pattern did not \
            match any number.")
            head_count = None

        return head_count

    def main(self):
        response = self.get_response(self.site_url)
        head_count = self.extract_data(response)

        return head_count


if __name__ == "__main__":
    SITE_URL = "https://display.safespace.io/value/live/a7796f34"
    ExtractHeadCount(SITE_URL).main()
            

