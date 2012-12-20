#!/usr/bin/env python

"""Interact with a Chrome Developer Tools Runtime instance."""

from pprint import pprint as pp

import argparse
import code
import json
import sys
import threading
import time
import websocket

import remotes


def get_request(method, params=None):
    """Get a string representing a request."""
    request = {"id": 0, "method": method}
    if params:
        request["params"] = params
    return json.dumps(request)


def get_eval_request(expression, return_by_value=False):
    """Get a string representing a Runtime.evaluate request."""
    return get_request("Runtime.evaluate",
                       {
                           "expression": expression,
                           "objectGroup": "runtime.py",
                           "returnByValue": return_by_value
                       })


def get_properties_request(object_id):
    """Get a string representing a Runtime.getProperties request."""
    return get_request("Runtime.getProperties",
                       {
                           "objectId": object_id,
                           "ownProperties": False
                       })


def get_call_func_request(object_id, function_declaration):
    """Get a string representing a Runtime.callFunctionOn request."""
    return get_request("Runtime.callFunctionOn",
                       {
                           "objectId": object_id,
                           "functionDeclaration": function_declaration,
                           "arguments": [],
                           "returnByValue": True
                       })


def get_clear_console_request():
    return get_request("Console.clearMessages")


def get_enable_console_request():
    return get_request("Console.enable")


def get_enumerable_results(response):
    """Get a list of enumerable results from the given response."""
    return [r for r in response["result"]["result"] if r["enumerable"]]


def receive(*args):
    ws = args[0]
    while True:
        message = json.loads(ws.recv())
        method = message.get("method")
        if method:
            if method == "Inspector.detached":
                if message["params"]["reason"] == "replaced_with_devtools":
                    print "Chrome Developer Tools has assumed this connection."
                else:
                    print "The connection to Chrome Developer Tools has been lost."
                sys.exit("No Inspector connection is currently available.")
            pp(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--url",
                        help="A URL to query for Chrome Developer Tools remote debugger information.  " +
                        "Defaults to http://localhost:1337",
                        default="http://localhost:1337")
    parser.add_argument("--expression", help="A JavaScript expression to evaluate in a Chrome runtime.")
    parser.add_argument("--timeout",
                        help="An amount of time, in seconds, to wait for the expression to evaluate.  Defaults to 2.0",
                        type=float, default="2.0")
    parser.add_argument("--trace", action="store_true", help="Enable WebSocket trace output.")
    parser.add_argument("--domain", help="A domain to filter WebSocket URLs by.")
    args = parser.parse_args()

    ws_urls = remotes.get_web_socket_urls(args.url, args.domain)

    if not ws_urls:
        sys.exit("No Chrome Developer Tools remote debugger WebSocket URLs are available.\n" +
                 "Is Developer Tools open within the browser?")

    # Just pick the first match for now.
    ws_url = ws_urls[0]
    ws = websocket.create_connection(ws_url)
    websocket.enableTrace(args.trace)

    thread = threading.Thread(target=receive, args=(ws,))
    thread.daemon = True
    thread.start()

    ws.send(get_clear_console_request())
    ws.send(get_enable_console_request())

    lines = None
    if args.expression:
        lines = args.expression.splitlines()
    else:
        lines = sys.stdin
    expression = " ".join([l.strip() for l in lines]).strip()
    ws.send(get_eval_request(expression))
    thread.join(args.timeout)
