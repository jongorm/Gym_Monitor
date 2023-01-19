
import requests
import re
from bs4 import BeautifulSoup
import lxml
import logging
import datetime
import pytz
import mysql
from requests.adapters import HTTPAdapter


class ExtractHeadCount:

    MAX_RETRIES_PER_REQUEST = 3
    REQUEST_TIMEOUT = 10

    def __init__(self, URL : str, upload_location : str):
        self.current_time = self._get_current_time()
        self.URL = URL
        self.upload_location = upload_location
        self.session = requests.Session()
        self.session.mount("https://display.safespace.io/", 
                        adapter=HTTPAdapter(max_retries=self.MAX_RETRIES_PER_REQUEST))

    def _get_current_time(self):
        """
        :return: the current timestamp objects that is utc timezone aware.
        """
        return datetime.datetime.now(tz=pytz.utc)

    def get_response(self, URL : str, parser='lxml'):
        """
        :param link: link for website being queried
        :param parser:  html parser, default lxml
        :return: BeautifulSoup object with HTML lines
        """
        timestamp_formatted = self.current_time.iso_format()

        try:
            response = self.session.get(URL, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.Timeout:
            logging.error(f"ERROR: timeout limit reached for response \
                at time: {timestamp_formatted}")
        except requests.HTTPError:
            logging.error(f"ERROR: status code {response.status_code} \
                resulted in error for response {timestamp_formatted}")
        except Exception as e:
            logging.error(f"ERROR: an exception resulted of type '{e}' \
                for response: {timestamp_formatted}")
        else:
            return BeautifulSoup(response, parser)
        
        return None


    def extract_data(self, response : str):
        """
        :param response: html string
        :return: the desired data from the webpage
        """
        head_count_pattern = re.compile(r'<body>(\d+)<body>')
        head_count = re.search(head_count_pattern, str(response)).group(1)

        if not head_count:
            logging.warn(f"NO COUNT: the head_count_pattern regex did not \
                match any number.")
        else:
            head_count = int(head_count)

        return head_count

    def upload_data(self, location : str, head_count : str):
        """
        :param location: SQL database upload location
        :param head_count: head_count int
        """
        database = ExtractHeadCount.mysql_connect()
        sql = """INSERT INTO vital_head_count (head_count, time) VALUES (%s, %s)"""
        vals = (head_count, self.current_time)
        logging.debug(f"Entering the following into vital_head_count table: \
            {head_count}, {self.current_time}")
        database.cursor.execute(sql, vals)
        database.commit()

    def extract_upload(self):
        """
        :return:
        """
        response = self.get_response(self.URL)
        head_count = self.extract_data(response)
        self.upload_data(self.upload_location, head_count)

        return head_count
    
    @staticmethod
    def mysql_connect(host : str, user : str, passwd : str, database : str, retry=0):
        try:
            db_connection = mysql.connector.connet(
                host=host,
                user=user,
                passwd=passwd,
                database=database
            )
        except Exception as e:
            logging.error(f"ERROR: An exception of type {e} resulted while \
                uploading to database")
            if retry == 3:
                raise
            ExtractHeadCount.mysql_connect(host, user, passwd, database, retry=retry+1)
        else:
            logging.debug(f"CONNECTION TO: {host} ESTABLISHED")
            return db_connection


if __name__ == "__main__":
    SITE_URL = "https://display.safespace.io/value/live/a7796f34"
    UPLOAD_LOCATION = ""
    ExtractHeadCount(SITE_URL, UPLOAD_LOCATION).extract_upload()
            

