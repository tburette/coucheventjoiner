coucheventjoiner
================

_coucheventjoiner_ is a command line tool to join couchsurfing event. If the event is full it will retry periodically until a spot is free and the event is joined.

Setup
=====

Use
===
```
coucheventjoiner.py [-h] [-d DELAY] event username [password]

positional arguments:
  event                 Event URL
  username              Couchsurfing username
  password              Couchsurfing password. Optional. If password missing the application will ask for it.

optional arguments:
  -h, --help            show this help message and exit
  -d DELAY, --delay DELAY
                        Delay before retrying if event is full(in seconds)
```

Tests
=====

```
python tests.py
```

