import re
from html.parser import HTMLParser

import requests

from ..provider import Provider


class PasteFS(Provider):

    PROTOCOL = "https"
    DOMAIN = "www.pastefs.com"
    WEBSITE = "{}://{}".format(PROTOCOL, DOMAIN)

    REGEX_URL = r'^{}/pid/([0-9]+)$'.format(WEBSITE)
    REGEX_URL_UPLOAD = r'<a\s+.*href=[\'"]*({}/pid/[0-9]+)[\'"]*.*>'.format(
        WEBSITE)

    @staticmethod
    def enabled():
        return True

    @staticmethod
    def nice_name():
        return PasteFS.DOMAIN.replace('www.', '')

    @staticmethod
    def is_supporting(uri):
        return re.search(PasteFS.REGEX_URL, uri) is not None

    @staticmethod
    def max_chunk_size():
        # theoretically the provider has been verified
        # as working even with 64 * 1024 (64MB) chunks.
        # let's keep it a little bit lower.
        return 8 * 1024

    @staticmethod
    def throttle():
        return 0

    @staticmethod
    def upload(content):
        request = requests.post(
            '{}/submit/submits/submit.php'.format(PasteFS.WEBSITE), data='''------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="post_text"\r\n\r\n{}\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="visibility"\r\n\r\nunlisted\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="content_rating"\r\n\r\nfamily_safe\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="filecontent[]"; filename=""\r\nContent-Type: application/octet-stream\r\n\r\n\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="recaptcha"\r\n\r\nfalse\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="paste_type"\r\n\r\ntext\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW\r\nContent-Disposition: form-data; name="submit"\r\n\r\ntrue\r\n------WebKitFormBoundaryzG9bBDqjdqxFzOZW--\r\n'''.format(content.decode()), headers={'origin': 'https', 'sec-fetch-user': '?1', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8', 'accept-encoding': 'gzip, deflate, br', 'sec-fetch-site': 'same-origin', 'authority': 'www.pastefs.com',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36', 'referer': 'https', 'sec-fetch-mode': 'navigate', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 'cache-control': 'max-age=0', 'cookie': '__cfduid=d03a89298b88af5338af0108351fecbc71566858476; PHPSESSID=95n0tj24f9mppbnimn680aof2f', 'upgrade-insecure-requests': '1', 'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryzG9bBDqjdqxFzOZW'})
        request = requests.get(request.url)
        response_match = re.search(
            PasteFS.REGEX_URL_UPLOAD, request.text)
        if response_match is None:
            print('Paste ID not found')
            return None

        return response_match.group(1)

    @staticmethod
    def download(uri):
        uri_r = re.search(PasteFS.REGEX_URL, uri)
        if uri_r is None:
            print('Paste URI unrecognized')
            return

        return requests.get('{}/components/template2/index/raw.php?pid={}'.format(
            PasteFS.WEBSITE, uri_r.group(1))).text.encode()
