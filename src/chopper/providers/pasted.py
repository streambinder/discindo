import re
import requests

from html.parser import HTMLParser
from ..provider import Provider


class Pasted(Provider):

    PROTOCOL = "http"
    DOMAIN = "pasted.co"
    WEBSITE = "{}://{}".format(PROTOCOL, DOMAIN)

    REGEX_URL = r'^{}/([a-zA-Z0-9]+)$'.format(WEBSITE)
    REGEX_URL_UPLOAD = r'<input\s+.*value=[\'"]*({}/[a-z0-9]+)[\'"]*.*>'.format(
        WEBSITE)
    REGEX_TIMESTAMP = r'<input\s+.*\s+name=[\'"]*timestamp[\'"]*.*value=[\'"]*([a-z0-9]+)[\'"]*>'
    REGEX_PASTE_HASH = r'{}/[a-z0-9]+/fullscreen\.php\?hash=([a-z0-9]+)'.format(
        WEBSITE)

    @staticmethod
    def nice_name():
        return Pasted.DOMAIN

    @staticmethod
    def is_supporting(uri):
        return re.search(Pasted.REGEX_URL, uri) is not None

    @staticmethod
    def max_chunk_size():
        return 512

    @staticmethod
    def upload(content):
        request = requests.get(Pasted.WEBSITE)
        request_timestamp_r = re.search(
            Pasted.REGEX_TIMESTAMP, request.text)
        if request_timestamp_r is None:
            print('Timestamp not found')
            return None

        request = requests.post(
            '{}/index.php?act=submit'.format(Pasted.WEBSITE), data={
                'antispam': '1',
                'paste_title': 'test',
                'input_text': content,
                'timestamp': request_timestamp_r.group(1),
                'code': '0',
                # 'paste_password': '',
            }, headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': Pasted.WEBSITE,
                'Accept-Encoding': 'gzip, deflate',
            }
        )
        response_match = re.search(
            Pasted.REGEX_URL_UPLOAD, request.text)
        if response_match is None:
            print('Paste ID not found')
            return None

        return response_match.group(1)

    @staticmethod
    def download(uri):
        uri_r = re.search(Pasted.REGEX_URL, uri)
        if uri_r is None:
            print('Paste URI unrecognized')
            return

        request = requests.get(uri)
        request_hash_r = re.search(
            Pasted.REGEX_PASTE_HASH, request.text)
        if request_hash_r is None:
            print('Paste hash not found')
            return None

        request = requests.get('{}/{}/fullscreen.php?hash={}'.format(
            Pasted.WEBSITE, uri_r.group(1), request_hash_r.group(1)))
        p = PastedChunkParser()
        p.feed(request.text)
        p.close()

        return p.paste_value.encode()


class PastedChunkParser(HTMLParser):
    def __init__(self):
        super(PastedChunkParser, self).__init__()
        self.paste_started = False
        self.paste_value = ''

    def handle_starttag(self, tag, attrs):
        self.paste_started = tag == 'pre' and 'thepaste' in [
            attr[1] for attr in attrs]

    def handle_endtag(self, tag):
        self.paste_started = self.paste_started and tag == 'pre'

    def handle_data(self, data):
        self.paste_value += data.strip() if self.paste_started else ''
