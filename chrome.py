#!/usr/bin/env python

"""Launch a Google Chrome instance for remote debugging."""

import argparse
import envoy
import os
import sys


def launch(url, port=1337, profile_dir=os.path.expanduser(os.path.join("~", "chrome-remote-profile")), canary=False):
    """Launch an instance of Google Chrome for remote debugging."""
    app = "Google Chrome"
    if canary:
        app += " Canary"

    chrome = os.path.join(os.sep, "Applications", app + os.path.extsep + "app", "Contents", "MacOS", app)
    assert os.path.exists(chrome), "'%s' does not exist." % chrome
    chrome = chrome.replace(" ", "\ ")
    cmd = "'%s' --remote-debugging-port=%d --user-data-dir=%s %s" % (chrome, port, profile_dir, url or "")
    envoy.run(cmd)


if __name__ == "__main__":
    assert sys.platform.startswith("darwin"), "Only OS X is supported at the moment."

    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("url", help="The URL to navigate to.")
    parser.add_argument("--port",
                        help="The remote debugging port.  Defaults to 1337.",
                        default=1337)
    parser.add_argument("--profile-dir",
                        help="A directory to store an alternate user profile within.  " +
                        "Defaults to ~/chrome-remote-profile.",
                        default=os.path.expanduser(os.path.join("~", "chrome-remote-profile")))
    parser.add_argument("--canary",
                        help="Launch a Google Chrome Canary instance.",
                        action="store_true")
    args = parser.parse_args()
    launch(args.url, port=args.port, profile_dir=args.profile_dir, canary=args.canary)
