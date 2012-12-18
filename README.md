# chrompy

A simple Python interface to Chrome Developer Tools Remote Debugging
[over the wire](https://developers.google.com/chrome-developer-tools/docs/remote-debugging#remote).
Currently it is only tested on OS X.

## Quick Usage

Launch a dedicated instance of Chrome with the `--remote-debugging-port` and
`--user-data-dir` flags set.

```sh
./chrome.py duckduckgo.com
```

Send an expression to the JavaScript runtime environment within that Chrome
instance:

```sh
echo "console.log('quack, quack!');" | ./runtime.py duckduckgo.com
```
