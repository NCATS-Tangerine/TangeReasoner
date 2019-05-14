# TangerineReasoner

A Translator Knowledge Graph Standard API for assorted Tangerine modules.

The near term aim of this repo is to 
* Provide a KGS 0.9.1 API
* Able to answer a growing set of questions

The longer term hope is to
* Modularize some of the common boilerplate of building a reasoner
* Produce a repo folks can fork to get started with less startup cost

A recent Tangerine mini-hackathon identified capabilities we want to expose via multiple automation environemnts (Jupyter, CWL, TranQL). We discussed the idea that it would help to expose these capabilities first via the KGS API and have the automation layer call KGS. The TangeReasoner is the first step towards that goal state.

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
 
