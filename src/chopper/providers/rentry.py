import re
import time
from html.parser import HTMLParser

import requests

from ..provider import Provider


class Rentry(Provider):

    PROTOCOL = "https"
    DOMAIN = "rentry.co"
    WEBSITE = "{}://{}".format(PROTOCOL, DOMAIN)
    TROTTLING = 30  # in seconds
    REGEX_URL = r'^{}/([a-zA-Z0-9]+)$'.format(WEBSITE)
    REGEX_CSRF = r'<input\s+.*\s+name=[\'"]*csrfmiddlewaretoken[\'"]*.*value=[\'"]*([a-zA-Z0-9]+)[\'"]*.*>'
    REGEX_HITLIMIT = r'<.*-error.*You have hit the limit, please wait a bit.*>'

    @staticmethod
    def nice_name():
        return Rentry.DOMAIN

    @staticmethod
    def is_supporting(uri):
        return re.search(Rentry.REGEX_URL, uri) is not None

    @staticmethod
    def max_chunk_size():
        return 128

    @staticmethod
    def upload(content):
        request = requests.get(Rentry.WEBSITE)
        request_csrf_r = re.search(
            Rentry.REGEX_CSRF, request.text)
        if request_csrf_r is None:
            print('CSRF middleware token not found')
            return None
        request_csrftoken_h = request.headers['Set-Cookie']
        if request_csrftoken_h is None:
            print('CSRF header token not found')
            return None

        request = requests.post(
            '{}/'.format(Rentry.WEBSITE), data={
                'csrfmiddlewaretoken': request_csrf_r.group(1),
                'text': content,
                'edit_code': '',
                'url': '',
            }, headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': Rentry.WEBSITE,
                'Accept-Encoding': 'gzip, deflate, br',
                'Cookie': request_csrftoken_h
            }
        )

        if request.status_code != 200:
            return None
        elif re.search(Rentry.REGEX_HITLIMIT, request.text) is not None:
            print('Rate limit hit')
            time.sleep(Rentry.TROTTLING)
            return Rentry.upload(content)

        return request.url

    @staticmethod
    def download(uri):
        return requests.get('{}/raw'.format(uri)).text
