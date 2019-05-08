import requests
import json
import os

url="http://localhost:9002/graph/query"
request = {
    "query_options": {
    },
    "query_graph": {
        "nodes": [
            {
                "node_id": "n00",
                "type": "gene"
            },
            {
                "node_id": "n01",
                "type": "gene"
            }   
        ], 
        "edges": [
            {
                "edge_id": "e00",
                "type": "association",
                "source_id": "n00",
                "target_id": "n01"
            } 
        ]
    },
    "results" : [
        {
            "edge_bindings" : {
            },
            "node_bindings" : {
            },
            "result_graph" : {
                "nodes" : [
                ],
                "edges" : [
                ]
            }
        }
    ]
}

response = requests.post (url, json=request)
print (response.text)
json.dumps (response.json (), indent=2)

