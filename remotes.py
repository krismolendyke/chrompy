#!/usr/bin/env python

"""Discover information regarding available Chrome Developer Tools remote
debuggers.
"""

from pprint import pprint as pp
import argparse
import requests
import sys
import urlparse


def get_web_socket_urls(url, domain=None):
    """Get a list of WebSocket URLs available at the given URL.  Optionally
    only yield those from a given domain.
    """
    parsed_url = urlparse.urlparse(url)
    url = urlparse.urlunparse((parsed_url[0], parsed_url[1], "json", "", "", ""))
    web_socket_urls = []
    try:
        r = requests.get(url)
        if r.status_code == requests.codes.OK:
            for i in [u for u in r.json if "webSocketDebuggerUrl" in u and
                    u["url"].startswith("http")]:
                url = urlparse.urlparse(i["url"])
                if domain:
                    if url.netloc.find(domain) != -1:
                        web_socket_urls.append(i["webSocketDebuggerUrl"])
                else:
                    web_socket_urls.append(i["webSocketDebuggerUrl"])
        return web_socket_urls
    except requests.exceptions.ConnectionError, e:
        sys.exit("Could not connect to '%s'." % url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--url",
                        help="A URL to query for Chrome Developer Tools remote debugger information.  Defaults to http://localhost:1337",
                        default="http://localhost:1337")
    parser.add_argument("--domain", help="A domain used to limit the search.")
    args = parser.parse_args()
    for ws in get_web_socket_urls(args.url, args.domain):
        print ws
