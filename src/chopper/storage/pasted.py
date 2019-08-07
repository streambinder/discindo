import re
import requests

from html.parser import HTMLParser
from .generic import ChunkStorage


class PastedStorage(ChunkStorage):

    PROTOCOL = "http"
    DOMAIN = "pasted.co"
    WEBSITE = "{}://{}".format(PROTOCOL, DOMAIN)

    @staticmethod
    def is_supporting(uri):
        return re.search(r'^{}/[a-zA-Z0-9]+$'.format(PastedStorage.WEBSITE), uri) is not None

    @staticmethod
    def max_chunk_size():
        return 512

    @staticmethod
    def upload(content):
        timestamp = None
        r = requests.get(PastedStorage.WEBSITE)
        # with open('timestamp.html', 'w') as fname:
        #     fname.write(r.text)
        timestamp_match = re.search(
            r'<input\s+.*\s+name=[\'"]*timestamp[\'"]*.*value=[\'"]*([a-z0-9]+)[\'"]*>', r.text)
        if timestamp_match is None:
            print('Timestamp not found')
            return None
        timestamp = timestamp_match.group(1)
        # print ('timestamp is {}'.format(timestamp))
        h = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': PastedStorage.WEBSITE,
            'Accept-Encoding': 'gzip, deflate',
        }
        d = {
            'antispam': '1',
            'paste_title': 'test',
            'input_text': content,
            'timestamp': timestamp,
            # 'paste_password': 'test',
            'code': '0',
        }
        r = requests.post(
            '{}/index.php?act=submit'.format(PastedStorage.WEBSITE), data=d, headers=h)
        print('Request {} status code: {}'.format(r.url, r.status_code))
        # with open('id.html', 'w') as fname:
        #     fname.write(r.text)
        response_match = re.search(
            r'<input\s+.*value=[\'"]*({}/[a-z0-9]+)[\'"]*.*>'.format(PastedStorage.WEBSITE), r.text)
        if response_match is None:
            print('Paste ID not found')
            return None
        return response_match.group(1)

    @staticmethod
    def download(uri):
        id_match = re.search(
            r'{}/([a-z0-9]+)'.format(PastedStorage.WEBSITE), uri)
        if id_match is None:
            return
        r = requests.get(uri)
        hash_match = re.search(
            r'{}/[a-z0-9]+/fullscreen\.php\?hash=([a-z0-9]+)'.format(PastedStorage.WEBSITE), r.text)
        if hash_match is None:
            print('Paste Hash not found')
            return None
        r = requests.get('{}/{}/fullscreen.php?hash={}'.format(
            PastedStorage.WEBSITE, id_match.group(1), hash_match.group(1)))
        p = PastedChunkParser()
        p.feed(r.text)
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
