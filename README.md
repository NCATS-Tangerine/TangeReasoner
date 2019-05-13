# TangerineReasoner

A Translator Knowledge Graph Standard API for assorted Tangerine modules.

## Configure
Requires Python 3.7+

Install:
```
pip install -r requirements.txt
```

## Run the Server
This runs a KGS API endpoint on port 9002 by default.
```
python api.py
```

## Run the Client
This posts a KGS Message object to the endpoint.
```
python client.py
```

## Status
The client posts a message that is validated against the KGS 0.9.1 spec. The validation is strict in the sense that it does not allow additional properties.

It focuses on a minimal subset of the Message object.
 
