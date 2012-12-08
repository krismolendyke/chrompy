#!/usr/bin/env python

"""Interact with a Chrome Developer Tools Runtime instance."""

from pprint import pprint as pp

import argparse
import json
import websocket

import remotes


def get_request(method, params):
    """Get a dict representing a request."""
    return {
        "id": 0,
        "method": "Runtime.%s" % method,
        "params": params
    }


def get_eval_request(expression, return_by_value=False):
    """Get a dict representing a Runtime.evaluate request."""
    return get_request("evaluate",
                       {
                           "expression": expression,
                           "objectGroup": "runtime.py",
                           "returnByValue": return_by_value
                       })


def get_properties_request(object_id):
    """Get a dict representing a Runtime.getProperties request."""
    return get_request("getProperties",
                       {
                           "objectId": object_id,
                           "ownProperties": False
                       })


def get_call_func_request(object_id, function_declaration):
    """Get a dict representing a Runtime.callFunctionOn request."""
    return get_request("callFunctionOn",
                       {
                           "objectId": object_id,
                           "functionDeclaration": function_declaration,
                           "arguments": [],
                           "returnByValue": True
                       })


def send_request(ws, request, trace=False):
    """Send the given request and return the response.  Optionally print the
    response.
    """
    request_json = json.dumps(request)
    if trace:
        pp(request_json)
        print "_" * 80
    ws.send(json.dumps(request))
    response = json.loads(ws.recv())
    if trace:
        pp(response)
        print "_" * 80
    return response


def get_enumerable_results(response):
    """Get a list of enumerable results from the given response."""
    return [r for r in response["result"]["result"] if r["enumerable"]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--url",
                        help="A URL to query for Chrome Developer Tools remote debugger information.  Defaults to http://localhost:1337",
                        default="http://localhost:1337")
    parser.add_argument("domain", help="A domain to filter WebSocket URLs by.")
    parser.add_argument("--trace", action="store_true", help="Enable WebSocket trace output.")
    args = parser.parse_args()
    websocket.enableTrace(args.trace)
    ws_url = remotes.get_web_socket_urls(args.url, args.domain)[0]
    ws = websocket.create_connection(ws_url)

    expression = """
mps.bestbuy.collect.getThumbnails = function() {
    console.group('getThumbnails');
    var thumbs = {}, badgeObj = {}, i, anchor, sku;
    if (window.sku && window.sku.length) {
        console.log('window.sku: ', window.sku);
        for (i = 0; i < window.sku.length; ++i) {
            sku = window.sku[i];
            badgeObj = {loc: mc.dom.getElementById(sku)};
            anchor = badgeObj.loc && badgeObj.loc.getElementsByTagName('a')[0];
            if (anchor && anchor.href) {
                badgeObj.href = anchor.href;
            }
            thumbs[sku] = badgeObj;
        }
    }
    console.groupEnd();
    return thumbs;
};"""

    # Send a function...
    request = get_eval_request(expression)
    response = send_request(ws, request, trace=args.trace)

    # Execute a function...
    request = get_eval_request("mps.bestbuy.collect.getThumbnails()")
    response = send_request(ws, request, trace=args.trace)

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
