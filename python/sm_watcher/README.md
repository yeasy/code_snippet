# sm_watcher

A real-time smart web watcher with keyword filting.

Currently it supports the boards of newsmth.net.

## Run

First, install all required dependencies.

```sh
$ pip install -r requirements.txt
```

Then start the watcher
```sh
$ python sm_watcher.py &
```

And the web server.
```sh
$ python index.py
```

Now open `http://localhost:9000`, the result will be shown and updated in real-time, enjoy!