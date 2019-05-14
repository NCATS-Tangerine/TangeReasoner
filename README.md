# TangerineReasoner

A Translator [Knowledge Graph Standard (KGS)](https://github.com/NCATS-Tangerine/NCATS-ReasonerStdAPI) API for assorted Tangerine modules.

The near term aim of this repo is to 
* Provide a KGS 0.9.1 API
* Able to answer a growing set of questions

The longer term hope is to
* Modularize some of the common boilerplate of building a reasoner
* Produce a repo folks can fork to get started with less startup cost

A recent Tangerine mini-hackathon identified [capabilities](https://github.com/ncats/translator-workflows/tree/296d7e412cf7fb3875ffc3bc30b02bb0761f56cb/Workflow2/Modules) we want to expose via multiple automation environemnts (Jupyter, CWL, TranQL). We discussed the idea that it would help to expose these capabilities first via the KGS API and have the automation layer call KGS. The TangeReasoner is the first step towards that goal state.

## Configure
Requires Python 3.7+

Install:
```
pip install -r requirements.txt
```

## Configure the server

The API requires a file to be downloaded to the directory it's run from. This is for the functional similarity module. 
```
wget http://current.geneontology.org/annotations/goa_human.gaf.gz
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
 
