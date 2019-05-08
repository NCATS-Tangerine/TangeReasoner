from mygene import MyGeneInfo
from ontobio.assocmodel import AssociationSet
#from .generic_similarity import GenericSimilarity
from typing import List, Union, TextIO
from pprint import pprint
from mygene import MyGeneInfo
from datetime import datetime

from ontobio.ontol_factory import OntologyFactory
from ontobio.io.gafparser import GafParser
from ontobio.assoc_factory import AssociationSetFactory
from ontobio.assocmodel import AssociationSet
from typing import List, Union, TextIO
from ontobio.analysis.semsim import jaccard_similarity
from pprint import pprint


class GenericSimilarity(object):
    def __init__(self) -> None:
        self.associations = ''
        self.ontology = ''
        self.assocs = ''
        self.afactory = AssociationSetFactory()

    def retrieve_associations(self, ont, group):
        taxon_map = {
            'human': 'NCBITaxon:9606',
            'mouse': 'NCBITaxon:10090',
        }
        ofactory = OntologyFactory()
        self.ontology = ofactory.create(ont)
        p = GafParser()
        url = ''
        if ont == 'go':
            go_roots = set(self.ontology.descendants('GO:0008150') + self.ontology.descendants('GO:0003674'))
            sub_ont = self.ontology.subontology(go_roots)
            if group == 'mouse':
                url = "http://current.geneontology.org/annotations/mgi.gaf.gz"
            if group == 'human':
                url = "http://current.geneontology.org/annotations/goa_human.gaf.gz"
            assocs = p.parse(url)
            self.assocs = assocs
            assocs = [x for x in assocs if 'header' not in x.keys()]
            assocs = [x for x in assocs if x['object']['id'] in go_roots]
            self.associations = self.afactory.create_from_assocs(assocs, ontology=sub_ont)
        else:
            self.associations = self.afactory.create(ontology=self.ontology ,
                       subject_category='gene',
                       object_category='phenotype',
                       taxon=taxon_map[group])

    def compute_jaccard(self, input_genes:List[dict], lower_bound:float=0.7) -> List[dict]:
        similarities = []
        for index, igene in enumerate(input_genes):
            for subject_curie in self.associations.subject_label_map.keys():
                input_gene = GenericSimilarity.trim_mgi_prefix(input_gene=igene['sim_input_curie'], subject_curie=subject_curie)
                if input_gene is not subject_curie:
                    score = jaccard_similarity(self.associations, input_gene, subject_curie)
                    if float(score) > float(lower_bound):
                        subject_label = self.associations.label(subject_curie)
                        similarities.append({
                            'input_id': input_gene,
                            'input_symbol': igene['input_symbol'],
                            'hit_symbol': subject_label,
                            'hit_id': subject_curie,
                            'score': score,
                        })
        return similarities

    @staticmethod
    def trim_mgi_prefix(input_gene, subject_curie):
        if 'MGI:MGI:' in subject_curie and 'MGI:MGI:' in input_gene:
            return input_gene
        elif 'MGI:MGI:' not in subject_curie and 'MGI:MGI:' in input_gene:
            return input_gene[4:]

        else:
            return input_gene
        
class FunctionalSimilarity(GenericSimilarity):
    def __init__(self, associations:AssociationSet=None):
        GenericSimilarity.__init__(self)
        self.mg = MyGeneInfo()
        self.gene_set = []
        self.input_object = ''
        self.ont = 'go'
        self.group = ''
        self.meta = {
            'input_type': {
                'complexity': 'set',
                'id_type': 'HGNC',
                'data_type': 'gene',
            },
            'output_type': {
                'complexity': 'set',
                'id_type': 'HGNC',
                'data_type': 'gene',
            },

            'source': 'Monarch Biolink',
            'predicate': ['blm:macromolecular machine to biological process association',
                          'macromolecular machine to molecular activity association']
        }

    def metadata(self):
        print("""Mod1A Functional Similarity metadata:""")
        pprint(self.meta)

    def load_input_object(self, input_object):
        self.input_object = input_object
        if self.input_object['parameters']['taxon'] == 'mouse':
            self.group = 'mouse'
        if self.input_object['parameters']['taxon'] == 'human':
            self.group = 'human'

    def load_associations(self):
        self.retrieve_associations(ont=self.ont, group=self.group)

    def load_gene_set(self, gene_set):
        for gene in gene_set: #self.input_object['input']:
            mg = MyGeneInfo()
            gene_curie = ''
            sim_input_curie = ''
            symbol = ''
            if 'MGI' in gene['hit_id']:
                gene_curie =  gene['hit_id']
                sim_input_curie = gene['hit_id'].replace('MGI', 'MGI:MGI')
                symbol = None
            if 'HGNC' in gene['hit_id']:
                gene_curie = gene['hit_id'].replace('HGNC', 'hgnc')
                scope = 'HGNC'
                mg_hit = mg.query(gene_curie,
                                  scopes=scope,
                                  species=self.input_object['parameters']['taxon'],
                                  fields='uniprot, symbol, HGNC',
                                  entrezonly=True)
                try:
                    gene_curie = gene['hit_id']
                    sim_input_curie = 'UniProtKB:{}'.format(mg_hit['hits'][0]['uniprot']['Swiss-Prot'])
                except Exception as e:
                    print(gene, e)

            self.gene_set.append({
                'input_id': gene_curie,
                'sim_input_curie': sim_input_curie,
                'input_symbol': gene['hit_symbol']
            })

    def load_gene_set(self, gene_set):
        human_taxon = 'human' #'NCBITaxon:9606'
        for gene in gene_set: #self.input_object['input']:
            mg = MyGeneInfo()
            gene_curie = ''
            sim_input_curie = ''
            symbol = ''
            if 'MGI' in gene:
                gene_curie =  gene
                sim_input_curie = gene.replace('MGI', 'MGI:MGI')
                symbol = None
            if 'HGNC' in gene:
                gene_curie = gene.replace('HGNC', 'hgnc')
                scope = 'HGNC'
                mg_hit = mg.query(gene_curie,
                                  scopes=scope,
                                  species=human_taxon, # TODO - fix hardocded taxon: # self.input_object['parameters']['taxon'],
                                  fields='uniprot, symbol, HGNC',
                                  entrezonly=True)
                try:
                    gene_curie = gene
                    sim_input_curie = 'UniProtKB:{}'.format(mg_hit['hits'][0]['uniprot']['Swiss-Prot'])
                except Exception as e:
                    print(gene, e)

            self.gene_set.append({
                'input_id': gene_curie,
                'sim_input_curie': sim_input_curie,
                'input_symbol': gene #['hit_symbol']
            })
    def compute_similarity(self):
        group = self.input_object['parameters']['taxon']
        lower_bound = float(self.input_object['parameters']['threshold'])
        results = self.compute_jaccard(self.gene_set, lower_bound)
        for result in results:
            if group == 'human':
                result['hit_id'] = self.symbol2hgnc(result['hit_symbol'])
            for gene in self.gene_set:
                if gene['sim_input_curie'] != result['input_id']:
                    result['input_id'] = self.symbol2hgnc(result['input_symbol'])
        return results

    def symbol2hgnc(self, symbol):
        mg_hit = self.mg.query('symbol:{}'.format(symbol),
                          fields='HGNC,symbol,taxon',
                          species='human',
                          entrezonly=True)
        if mg_hit['total'] == 1:
            return 'HGNC:{}'.format(mg_hit['hits'][0]['HGNC'])
