import json
import collections
from collections import deque
from abc import abstractmethod, ABC
from collections import OrderedDict, Counter
from logging import Logger
from typing import Iterable, List

import numpy as np
from tqdm import tqdm
from transformers import AutoTokenizer

from src import util
from src.entities import Dataset, EntityLabel, RelationLabel, EntityType, RelationType, Entity, Relation, Document


E_PREFIX = ['B-', 'U-', 'I-', 'L-']
R_PREFIX = ['R-', 'L-'] # relation Pointing to left/right

class BaseInputReader(ABC):
    def __init__(self, types_path: str, tokenizer: AutoTokenizer, logger: Logger = None):
        # entity + relation types in general, i.e., without prefix
        types = json.load(open(types_path), object_pairs_hook=OrderedDict)

        self._entity_labels = OrderedDict()
        self._idx2entity_label = OrderedDict()
        self._relation_labels = OrderedDict()
        self._idx2relation_label = OrderedDict()


        self._entity_types = OrderedDict()
        self._idx2entity_type = OrderedDict()
        self._relation_types = OrderedDict()
        self._idx2relation_type = OrderedDict()


        # entities
        # add 'None' entity label
        none_entity_label = EntityLabel('O', 0, 'O', 'O')
        self._entity_labels['O'] = none_entity_label
        self._idx2entity_label[0] = none_entity_label

        none_entity_type = EntityType([none_entity_label], 0, 'O', 'O')
        self._entity_types['O'] = none_entity_type
        self._idx2entity_type[0] = none_entity_type

        # specified entity labels
        for i, (key, v) in enumerate(types['entities'].items()):
            entity_labels = []
            for j, pre in enumerate(E_PREFIX):
                entity_label = EntityLabel(key, 4 * i + j + 1, pre + v['short'], pre + v['verbose'])
                self._entity_labels[pre + key] = entity_label
                self._idx2entity_label[4 * i + j + 1] = entity_label
                entity_labels.append(entity_label)
            entity_type = EntityType(entity_labels, i + 1, v['short'], v['verbose'])
            self._entity_types[key] = entity_type
            self._idx2entity_type[i + 1] = entity_type

        # relations
        # add 'None' relation label
        none_relation_label = RelationLabel('None', 0, 'None', 'No Relation')
        self._relation_labels['None'] = none_relation_label
        self._idx2relation_label[0] = none_relation_label

        none_relation_type = RelationType([none_relation_label], 0, 'None', 'No Relation')
        self._relation_types['None'] = none_relation_type
        self._idx2relation_type[0] = none_relation_type

        # specified relation labels
        for i, (key, v) in enumerate(types['relations'].items()):
            relation_labels = []
            relation_tags = []
            for j, pre in enumerate(R_PREFIX):
                relation_label = RelationLabel(key, 2 * i + j + 1, pre + v['short'], pre + v['verbose'], v['symmetric'])
                # print(relation_label)
                self._relation_labels[pre + key] = relation_label
                self._idx2relation_label[2 * i + j + 1] = relation_label
                relation_labels.append(relation_label)
                # print("Revealling")
                # relation_tags.append(pre+v['short'])
            relation_type = RelationType(relation_labels, i + 1, v['short'], v['verbose'])
            self._relation_types[key] = relation_type
            self._idx2relation_type[i + 1] = relation_type

        '''
        for i in range(len(relation_tags)):
            print("RelationTags")
            print(relation_tags[i])
        '''

        self._datasets = dict()

        self._tokenizer = tokenizer
        self._logger = logger

        self._vocabulary_size = tokenizer.vocab_size
        self._context_size = 0
        # print("Relation Labels:")
        # for i in range(len(relation_labels)):
        # print(relation_labels[i]._verbose_name)

    @abstractmethod
    def read(self, datasets):
        pass

    def get_dataset(self, label) -> Dataset:
        return self._datasets[label]

    def get_entity_label(self, idx) -> EntityLabel:
        entity = self._idx2entity_label[idx]
        return entity

    def get_relation_label(self, idx) -> RelationLabel:
        relation = self._idx2relation_label[idx]
        return relation

    def get_entity_type(self, idx) -> EntityType:
        entity = self._idx2entity_type[idx]
        return entity

    def get_relation_type(self, idx) -> RelationType:
        relation = self._idx2relation_type[idx]
        return relation
    def _log(self, text):
        if self._logger is not None:
            self._logger.info(text)

    @property
    def datasets(self):
        return self._datasets

    @property
    def entity_labels(self):
        return self._entity_labels

    @property
    def list_entity_labels(self):
        return list(self._entity_labels.keys())

    @property
    def relation_labels(self):
        return self._relation_labels

    @property
    def relation_label_count(self):
        return len(self._relation_labels)

    @property
    def entity_label_count(self):
        return len(self._entity_labels)

    @property
    def entity_types(self):
        return self._entity_types

    @property
    def relation_types(self):
        return self._relation_types

    @property
    def relation_type_count(self):
        return len(self._relation_types)

    @property
    def entity_type_count(self):
        return len(self._entity_types)

    @property
    def max_entity_len(self):
        return max([d.max_entity_len for d in self._datasets.values()])

    @property
    def vocabulary_size(self):
        return self._vocabulary_size

    @property
    def context_size(self):
        return self._context_size

    def __str__(self):
        string = ""
        for dataset in self._datasets.values():
            string += "Dataset: %s\n" % dataset
            string += str(dataset)

        return string

    def __repr__(self):
        return self.__str__()


class JsonInputReader(BaseInputReader):
    def __init__(self, labels_path: str, tokenizer: AutoTokenizer, logger: Logger = None):
        super().__init__(labels_path, tokenizer, logger)

    def read(self, dataset_path, dataset_label):
        dataset = Dataset(dataset_label, self._relation_types, self._entity_types)
        types_count,types_countr = self._parse_dataset(dataset_path, dataset)
        self._datasets[dataset_label] = dataset
        print("read entities")
        print(types_count)
        return dataset, types_count,types_countr

    def _parse_dataset(self, dataset_path, dataset):
        documents = json.load(open(dataset_path))
        types_count = Counter([])
        types_countr = Counter([])
        types_r = []
        for document in tqdm(documents, desc="Parse dataset '%s'" % dataset.label):
            doc,we,wc= self._parse_document(document, dataset)
            types_count+=we
            types_countr+=wc
            print("Parse document")
            print("Parse relations")
            print(types_countr)
            print("Parse entities")
            print(types_count)
        return types_count,types_countr

    def _parse_document(self, doc, dataset) -> Document:
        jtokens = doc['tokens']
        jrelations = doc['relations']
        jtags = doc['tags']
        doc_id = doc['orig_id']
        # parse tokens
        doc_tokens, doc_encoding = self._parse_tokens(doc_id, jtokens, dataset)

        # parse entity mentions
        entities = self._parse_entities(jtags, doc_tokens, dataset)
        (unique, counts) = np.unique(jtags, return_counts=True)
        entitycounter={x:y for x,y in zip(unique, counts)}
        # parse relations
        relations, wordscounter = self._parse_relations(jrelations, entities, dataset)
        print("Doc:")
        print(wordscounter)
        # create document
        document = dataset.create_document(doc_tokens, entities, relations, doc_encoding)
        if len(doc_encoding) > self._context_size:
            self._context_size = len(doc_encoding)

        return document, entitycounter, wordscounter

    def _parse_tokens(self, doc_id, jtokens, dataset):
        doc_tokens = []

        #         if doc_id in dataset._documents:
        #             return dataset._documents[doc_id]._tokens, dataset._documents[doc_id].encoding
        # full document encoding including special tokens ([CLS] and [SEP]) and byte-pair encodings of original tokens
        doc_encoding = [self._tokenizer.convert_tokens_to_ids('[CLS]')]
        # parse tokens
        for i, token_phrase in enumerate(jtokens):
            token_encoding = self._tokenizer.encode(token_phrase, add_special_tokens=False)
            span_start, span_end = (len(doc_encoding), len(doc_encoding) + len(token_encoding))
            token = dataset.create_token(i, span_start, span_end, token_phrase)
            #             print(self._tokenizer.convert_ids_to_tokens(token_encoding))
            doc_tokens.append(token)
            doc_encoding += token_encoding
        doc_encoding += [self._tokenizer.convert_tokens_to_ids('[SEP]')]
        return doc_tokens, doc_encoding

    def _parse_entities(self, jtags, doc_tokens, dataset) -> List[Entity]:
        #words_ent=Counter([])
        entities=[]
        entity_labels = []
        for idx, jtag in enumerate(jtags):
            print("TAGS")
            print (jtag)
            if not jtag.startswith('O'):  # skip non-entities
                entity_labels.append(self._entity_labels[jtag])
                if jtag.startswith('B') or jtag.startswith('U'):
                    start = idx
                if jtag.startswith('U') or jtag.startswith('L'):
                    entity_type = self._entity_types[jtag[2:]]
                    end = idx + 1
                    tokens = doc_tokens[start:end]
                    phrase = " ".join([t.phrase for t in tokens])
                    entity = dataset.create_entity(entity_type, entity_labels, tokens, phrase)
                    #words_ent.update(collections.Counter(jtag))
                    entities.append(entity)
                    #print(entity.entity_labels)
                    entity_labels = []
                    #words_ent.update(collections.Counter(jtag))

        return entities

    def _parse_relations(self, jrelations, entities, dataset):
        relations = []
        rl = []
        words = Counter([])
        for jrelation in jrelations:
            relation_type = self._relation_types[jrelation['type']]
            # rl_types.append('R-'+relation_type)
            # rl_types.append('L-'+relation_type)
            head_idx = jrelation['head']
            tail_idx = jrelation['tail']

            # create relation
            head = entities[head_idx]
            tail = entities[tail_idx]
            print("What is inside relations?")
            print(relations)
            print("relation_type")
            print(relation_type)
            print("relation_type : type")
            print(type(relation_type))
            relation = dataset.create_relation(relation_type, head_entity=head, tail_entity=tail)
            relations.append(relation)
            rl.append("R-" + str(relation_type))
            rl.append("L-" + str(relation_type))
            words.update(collections.Counter(rl))
            print("What is inside rl?")
            print(rl)
            print("1.relations list")
            print(relations)

        print("Relations types list")
        print(relations)
        print(type(relations))
        print("Counter status")
        print(words)
        return relations, words

