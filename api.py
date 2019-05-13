"""
Provide a standard protocol for asking graph oriented questions of Translator data sources.
"""
import copy
import argparse
import json
import os
import yaml
import jsonschema
import requests
from flask import Flask, request, abort, Response
from flask_restful import Api, Resource
from flasgger import Swagger
from flask_cors import CORS
from model import ReasonerModel

app = Flask(__name__)

api = Api(app)
CORS(app)

""" See https://github.com/NCATS-Gamma/NCATS-ReasonerStdAPI """
api_schema_name = os.path.join (os.path.dirname (__file__), 'translator_interchange_0.9.1.yaml')
api_name = "Generic Reasoner"
template = None
with open(api_schema_name, 'r') as file_obj:
    template = yaml.load(file_obj)
    template['info']['title'] = api_name
    template['info']['description'] = api_name
app.config['SWAGGER'] = {
    'title': api_name,
    'description': api_name,
    'uiversion': 3
}
swagger = Swagger(app, template=template)

class KGStandardAPIResource(Resource):
    """ A schema resource to handle validation and other core services generically. """
    def validate (self, request):
        with open(api_schema_name, 'r') as file_obj:
            specs = yaml.load(file_obj)        
        to_validate = specs["components"]["schemas"]["Message"]
        to_validate["components"] = specs["components"]
        to_validate["components"].pop("Message", None)
        to_validate['additionalProperties'] = False
        try:
            jsonschema.validate(request.json, to_validate)
        except jsonschema.exceptions.ValidationError as error:
            print (f"ERROR: {str(error)}")
            abort(Response(str(error), 400))

    def get_opt (self, request, opt):
        """ Get message options """
        return request.get('query_options', {}).get (opt)
    
    def normalize_message (self, message):
        """ Compensate for message version incompatibilities uniformly. """
        if 'answers' in message:
            message['knowledge_map'] = message['answers']
        return message

class ReasonerQuery(KGStandardAPIResource):
    """ Reasoner Query. """

    def __init__(self):
        self.model = ReasonerModel ()
        
    def post(self):
        """
        query
        ---
        tag: validation
        description: Query the reasoner.
        requestBody:
            description: Input message
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Message'
        responses:
            '200':
                description: Success
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Message'
            '400':
                description: Malformed message
                content:
                    text/plain:
                        schema:
                            type: string

        """
        self.validate (request)
        print (json.dumps(request.json, indent=2))

        ''' Execute the reasoner engine to build the output KG. '''
        response = self.model.compile (request.json['query_graph'])
        print (json.dumps(response, indent=2))

        self.validate (response)
        return self.normalize_message (response)

# Generic
api.add_resource(ReasonerQuery, '/graph/query')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=api_name)
    parser.add_argument('-port', action="store", dest="port", default=9002, type=int)
    args = parser.parse_args()

    server_host = '0.0.0.0'
    server_port = args.port

    app.run(
        host=server_host,
        port=server_port,
        debug=False,
        use_reloader=True
    )

