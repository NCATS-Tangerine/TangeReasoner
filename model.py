import networkx as nx
import json
from collections import defaultdict
from similarity import FunctionalSimilarity

class ReasonerModel:
    """ Encapsulates
    * Modeling a knowledge map among biolink model types
    * Parsing a machine question and mapping to the knowledge map
    * Building a knowledge graph response
    """
    def __init__(self):
        self.next_id = 0
        k_map = self.get_knowledge_map ()
        ''' Build the knowledge map. '''
        self.type_graph = nx.MultiDiGraph ()
        for start_type, start_k_map in k_map.items ():
            for end_type, predicate_map in start_k_map.items ():
                for predicate, operators in predicate_map.items ():
                    if not start_type in self.type_graph:
                        self.type_graph.add_node (start_type)
                    if not end_type in self.type_graph:
                        self.type_graph.add_node (end_type)
                    for operator in operators:
                        self.type_graph.add_edge (
                            start_type,
                            end_type,
                            attr_dict={
                                'predicate' : predicate,
                                'operator'  : operator['operator']
                            })
                        
    def get_knowledge_map (self):
        """ Override this to define the knowledge map. """
        return {
            'gene' : {
                'gene' : {
                    'functional_similarity' : [
                        { 'operator' : self.gene__functional_similarity__gene }
                    ]
                }
            }
        }
        #return {}
    
    def compile (self, question):
        """ Given a machine question, iterate over its edges, invoking
        operators to build an output knowledge graph. 
        For this prototype, we do something trivial.
        In particular, we need a more sophisticated graph traversal
        and a memory mechanism for results, preventing duplicates, etc."""
        nodes = []
        edges = []
        answers = []
        node_ids = { i['node_id'] : i for i in question['nodes'] }
        for edge in question['edges']:
            print (f"processing edge: {edge}")
            source = node_ids[edge['source_id']]
            target = node_ids[edge['target_id']]
            source_type = source['type']
            target_type = target['type']
            predicate = edge.get('type', None)
            print (f"{source_type}-{predicate}->{target_type}")
            print (f"   src curie: {source.get('curie','')}")
            print (f"   trg curie: {target.get('curie','')}")
            if self.type_graph.has_edge(source_type, target_type):
                map_edge = self.type_graph.edges(
                    [source_type, target_type],
                    data=True)
                seen = {}
                for p in map_edge:
                    key = f"{source_type}-{target_type}"
                    if key in seen:
                        continue
                    seen[key] = key
                    answer = {
                        'edge_bindings' : defaultdict(list), #{},
                        'node_bindings' : defaultdict(list), #{},
                        'score_name' : 'weight',
                        'score' : 0.0
                    }
                    node_bind = answer['node_bindings']
                    edge_bind = answer['edge_bindings']
                    attributes = p[2]['attr_dict']
                    path_predicate = attributes['predicate']
                    operator = attributes['operator']
                    if predicate:
                        if not predicate == path_predicate:
                            continue
                    if 'curie' in source:
                        response = operator (source['curie'])
                        with open ('save.json', 'w') as stream:
                            json.dump (response, stream, indent=2) 
                        for n in response['nodes']:
                            nodes.append (n)
                        score = 0
                        for e in response['edges']:
                            edges.append (e)
                            answer['score'] = answer['score'] + e['weight']
                            node_bind[source['node_id']].append (e['source_id'])
                            node_bind[target['node_id']].append (e['target_id'])
                            edge_bind[e['id']].append (e['id'])
                        answers.append (answer)
                        print (attributes)
        return {
            'query_graph' : question,
            'knowledge_graph' : {
                'nodes' : nodes,
                'edges' : edges
            },
            'results' : answers
        }
    
    def stub_gene__functional_similarity__gene0 (self, input_gene):
        """ """
        return {
            "nodes": [
                {
                    "type": "gene",
                    "id": "HGNC:20922"
                },
                {
                    "type": "gene",
                    "id": "HGNC:23845"
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source_id": "HGNC:23845",
                    "target_id": "HGNC:20922",
                    "weight": 0.782312925170068
                }
            ]
        }
    def gene__functional_similarity__gene (self, input_gene):
        input_curie_set = [ {
            'hit_id' : input_gene,
            'hit_symbol' : ''
        }]
        mod1a_input_object_human = {
            'input': input_curie_set,
            'parameters': {
                'taxon': 'human',
                'threshold': 0.75,  # jaccard index threshold
            },
        }
        func_sim_human = FunctionalSimilarity()
        func_sim_human.load_input_object(mod1a_input_object_human)
        func_sim_human.load_gene_set()
        func_sim_human.load_associations()
        similarities = func_sim_human.compute_similarity()

        ''' Package all new nodes and associations discovered here
        into a graph for the caller to merge into a result kg. '''
        nodes = []
        edges = []
        for sim in similarities:
            nodes.append ({
                'type'  : 'gene',
                'id'    : sim['hit_id']
            })
            if sim['score'] == 1.0:
                continue
            self.next_id = self.next_id + 1
            edges.append ({
                'id'        : f"e{self.next_id}",
                'source_id' : input_gene,
                'target_id' : sim['hit_id'],
                'weight'    : sim['score']
            })
        return {
            'nodes' : nodes,
            'edges' : edges
        }


    
        '''
        [
            {
                "input_id": "UniProtKB:Q8IY92",
                "input_symbol": "SLX4",
                "hit_symbol": "SLX4",
                "hit_id": "HGNC:23845",
                "score": 1.0
            },
            {
                "input_id": "UniProtKB:Q8IY92",
                "input_symbol": "SLX4",
                "hit_symbol": "SLX1A",
                "hit_id": "HGNC:20922",
                "score": 0.782312925170068
            }
        ]
        '''
