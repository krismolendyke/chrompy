#!/usr/bin/env python

"""Interact with a Chrome Developer Tools Runtime instance."""

from pprint import pprint as pp

import argparse
import json
import sys
import threading
import time
import websocket

import remotes


def get_request(method, params=None):
    """Get a string representing a request."""
    request = { "id": 0, "method": method }
    if params:
        request["params"] = params
    return json.dumps(request)


def get_eval_request(expression, return_by_value=False):
    """Get a dict representing a Runtime.evaluate request."""
    return get_request("Runtime.evaluate",
                       {
                           "expression": expression,
                           "objectGroup": "runtime.py",
                           "returnByValue": return_by_value
                       })


def get_properties_request(object_id):
    """Get a dict representing a Runtime.getProperties request."""
    return get_request("Runtime.getProperties",
                       {
                           "objectId": object_id,
                           "ownProperties": False
                       })


def get_call_func_request(object_id, function_declaration):
    """Get a dict representing a Runtime.callFunctionOn request."""
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


def send_request(ws, request, trace=False):
    """Send the given request and return the response.  Optionally print the response."""
    if trace:
        pp(json.loads(request))
        print "_" * 80
    ws.send(request)
    response = json.loads(ws.recv())
    if trace:
        pp(response)
        print "_" * 80
    return response


def get_enumerable_results(response):
    """Get a list of enumerable results from the given response."""
    return [r for r in response["result"]["result"] if r["enumerable"]]


def receive(*args):
    ws = args[0]
    while True:
        message = json.loads(ws.recv())
        print pp(message)
        method = message.get("method")
        if method:
            if method == "Inspector.detached":
                if message["params"]["reason"] == "replaced_with_devtools":
                    print "Chrome Developer Tools stole the WebSocket!"
                else:
                    print "This connection has been closed."
                return
            print pp(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--url",
                        help="A URL to query for Chrome Developer Tools remote debugger information.  Defaults to http://localhost:1337",
                        default="http://localhost:1337")
    parser.add_argument("domain", help="A domain to filter WebSocket URLs by.")
    parser.add_argument("--trace", action="store_true", help="Enable WebSocket trace output.")
    args = parser.parse_args()

    ws_urls = remotes.get_web_socket_urls(args.url, args.domain)

    if not ws_urls:
        sys.exit("No Chrome Developer Tools remote debugger WebSocket URLs are available.")

    ws_url = ws_urls[0]
    ws = websocket.create_connection(ws_url)
    websocket.enableTrace(args.trace)

    thread = threading.Thread(target=receive, args=(ws,))
    thread.daemon = True
    thread.start()

    ws.send(get_clear_console_request())
    ws.send(get_enable_console_request())
    time.sleep(1)
    expression = """
var d = {};
var f = function() {};
mps.newegg.common.collectProductPage(d, f);
console.log(d);
"""
    ws.send(get_eval_request(expression));

    thread.join()


#     print "yo!"
#     time.sleep(2)
#     expression = """
# mps.newegg.common.getPidFromSearchTerm()
# """
#     # Send a function...
#     request = get_eval_request(expression)
#     response = ws.send(request)

    # ws = websocket.create_connection(ws_url)

    # request = get_enable_console_request()
    # response = send_request(ws, request, trace=args.trace)


#     # Execute a function...
#     request = get_eval_request("mps.bestbuy.collect.getThumbnails()")
#     response = send_request(ws, request, trace=args.trace)

    # Get information about that execution... this shitty hack should really
    # be handled with some recursion.
    # object_id = response["result"]["result"]["objectId"]
    # request = get_properties_request(object_id)
    # response = send_request(ws, request)
    # results = get_enumerable_results(response)
    # pp(results)
    # for r in results:
    #     pp(r)
    #     request = get_properties_request(r["value"]["objectId"])
    #     response = send_request(ws, request)
    #     results2 = get_enumerable_results(response)
    #     pp(results2)
