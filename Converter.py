import os
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans
import Preprocess
import re
import sys

# paths of your data
all_data = ""
training_data = ""
test_data = ""
evaluation_data = ""
nlp = spacy.blank("de")
count_documents = 0

def span_not_valid(doc_number, text, entity_name, start, end, label):
    print("Character indice couldn't be map to valid span!")
    print("Document: " + str(doc_number))
    print("Text: " + text)
    print("Entity: " + entity_name)
    print("Start: " + str(start))
    print("End: " + str(end))
    print("Label: " + label + "\n") 


def get_ents(doc, annot_path):
    global count_documents
    ents = []
    # labels need to be changed for your specific data
    labels = ["Procedures", "Physiology", "Anatomical_Structure", "Disorders"]

    with open(annot_path) as ent_file:
        lines = ent_file.readlines()

    for line in lines:
        tokens = line.split()
        label = tokens[1]
        start = int(tokens[2])
        end = int(tokens[3])
        entity_name = line.split("\t")[2]

        if(label in labels):
            span = doc.char_span(start_idx=start, end_idx=end,
                                 label=label, alignment_mode="contract")
            if (span is None):
                span_not_valid(count_documents, doc.text, entity_name, start, end, label)  
            else:
                ents.append(span)
    count_documents += 1
    return ents


def ann_to_spacy(path):
    false_annot = []
    all_files = sorted(os.listdir(path))
    db = DocBin()
    for annot, text in zip(all_files[0::2], all_files[1::2]):
        text_path = path + "/" + text
        annot_path = path + "/" + annot

        with open(text_path) as text_file:
            text = text_file.read()
            text = Preprocess.replace_special_chars_with_space(text)
            doc = nlp.make_doc(text)
        ents = get_ents(doc, annot_path)
        
        try:
            doc.ents = ents
        except ValueError:
            false_annot.append(text_path)
            filtered_ents = filter_spans(ents)
            doc.ents = filtered_ents
        db.add(doc)
    print("Paths with duplicated or overlapping spans:\n " + str(false_annot) + "\n")
    return db


def find_positions(text, entity, label):
    pattern = "\\b" + entity + "\\b"
    pos = [(ele.start(), ele.end())
           for ele in re.finditer(pattern, text)]
    res = {'entity': entity, 'pos': pos, 'label': label}
    return res


def preproce_spacy_data(doc_bin):
    global count_documents
    docs = list(doc_bin.get_docs(nlp.vocab))
    db = DocBin()
    count_documents = 0
    for doc in docs:
        indx = None
        entity_with_positions = None
        ents = []
        # preprocess text
        text = Preprocess.replace_umlauts(doc.text)
        doc_new = nlp.make_doc(text)
        # preprocess entities
        entities = get_entities_with_positions(text, doc)
        while len(entities)> 0:
            start = sys.maxsize
            for cnt, e in enumerate(entities):
                if e['pos'][0][0] < start:
                    start = int(e['pos'][0][0])
                    entity_with_positions = e
                    indx = cnt

            entity_name = entity_with_positions['entity']
            label = entity_with_positions['label']
            end = int(entity_with_positions['pos'][0][1])

            if len(entities[indx]['pos']) == 1:
                entities.pop(indx)
            else:
                entities[indx]['pos'].pop(0)
            
            span = doc_new.char_span(start_idx=start, end_idx=end,
                                     label=label, alignment_mode="contract")
            
            if (span is None):
                span_not_valid(count_documents, text, entity_name, start, end, label)
            else:
                ents.append(span)
        try:
            doc_new.ents = ents
        except ValueError:
            filtered_ents = filter_spans(ents)
            doc_new.ents = filtered_ents
            print("Check! Duplicated or overlapping spans.")
            print("Document: " + str(count_documents))
            print("Text: " + text)

        count_documents += 1
        db.add(doc_new)
    return db


def remove_overlapping_positions(substring_entity, entity):
    for p_ in substring_entity['pos'][:]:
        for p in entity['pos']:
            if p[0] == p_[0]:
                substring_entity['pos'].remove(p_)
            if p[1] == p_[1]:
                substring_entity['pos'].remove(p_)


def get_entities_with_positions(text, doc):
    entities = []
    different_entity = True
    for e in doc.ents:
        different_entity = True

        # preprocess entity
        entity_name = Preprocess.replace_umlauts(e.text)
        entity_with_positions = find_positions(text, entity_name, e.label_)

        for ents in entities:
            if ents['entity'] == entity_with_positions['entity']:
                different_entity = False
                break
        if different_entity:
            pattern_entity = "\\b" + entity_with_positions["entity"] + "\\b"
            for ent in entities[:]:
                pattern_ent = "\\b" + ent['entity'] + "\\b"
                if re.search(pattern_entity, ent['entity']):
                    remove_overlapping_positions(
                        entity_with_positions, ent)
                    
                elif re.search(pattern_ent, entity_with_positions["entity"]): 
                    remove_overlapping_positions(ent,
                        entity_with_positions)
                    if len(ent["pos"]) == 0:
                        entities.remove(ent)

            if len(entity_with_positions["pos"]) > 0:
                entities.append(entity_with_positions)
    return entities


db = ann_to_spacy(all_data)
db = preproce_spacy_data(db)
# .to_disk("./train.spacy")


"""
with these two functions, the data can be split into training, testing, 
and evaluation datasets based on the number of entities
"""

def count_ents(doc_bin):
    docs = list(doc_bin.get_docs(nlp.vocab))
    count_docs = 0
    res = []
    for doc in docs:
        count_entities = 0
        for e in doc.ents:
            count_entities += 1
        itm = {'Document': count_docs, 'Number of entities': count_entities}
        res.append(itm)
        count_docs += 1
    return res


def get_document(entities, number_of_entities=None):
    sum_entities = 0
    for e in entities:
        sum_entities += e['Number of entities']
        if number_of_entities is not None:
            if sum_entities >= number_of_entities:
                print(str(e) + "\n")
                break
    print("Sum of entities: " + str(sum_entities))
# get_document(count_ents(db))

