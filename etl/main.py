from pymongo import MongoClient, DESCENDING
from datetime import datetime
from os import listdir, path
from typing import Tuple
from hashlib import md5
import json

FILENAME = "source_file"
NOMCOMPLET = "nomComplet"
MATRICULE = "matricule"
STATUS = "file_status"
HASH = "hash"
MESSAGE = "message"

DATAPATH = "/data/"
mongo_client = MongoClient(host="database")
log_collection_pointer = mongo_client['glo4035']['log']
midterm_questions_collection_pointer = mongo_client['glo4035']['midtermQuestions']


def get_source_file(data_source_path: str) -> Tuple[str, list]:
    for file in listdir(data_source_path):
        file_handle = open(path.join(data_source_path, file))
        yield file, file_handle


def get_log_document_template():
    return {
        "date": datetime.now()
    }


def get_file_last_hash(filename: str) -> str:
    file_hash_pointer = log_collection_pointer.find({FILENAME: filename}, {HASH: 1}).sort("_id", DESCENDING)
    if file_hash_pointer.count() == 0:
        file_hash = ""
    else:
        file_hash = file_hash_pointer.next()[HASH]

    return file_hash


def file_to_update(filename : str, file_hash : str) -> bool:
    last_hash = get_file_last_hash(filename)
    return file_hash != last_hash


def insert_log(log_document: dict):
    log_collection_pointer.insert_one(log_document)


def anonimize_question(question_document: dict):
    del question_document[NOMCOMPLET]


def insert_question(source_file: str, question_document : dict):
    question_document[FILENAME] = source_file
    anonimize_question(question_document)
    midterm_questions_collection_pointer.insert_one(question_document)


def delete_question(source_file: str):
    midterm_questions_collection_pointer.delete_many({FILENAME:source_file})


if __name__ == "__main__":

    for filename, file_handle in get_source_file(DATAPATH):

        log_document = get_log_document_template()
        log_document[FILENAME] = filename
        try:
            question_document = json.load(file_handle)
            current_document_hash = md5(str(question_document).encode()).hexdigest()
            log_document[HASH] = current_document_hash
            if file_to_update(filename, current_document_hash):
                delete_question(filename)
                for question in question_document:
                    insert_question(filename, question)
                log_document[STATUS] = "EXTRACTED"
                print("Lecture complétée du fichier {}".format(filename))
            else:
                log_document[STATUS] = "IGNORED"
                print("Aucun changement détecté dans le fichier {}".format(filename))
        except Exception as e:
            print("Erreur avec le document {}: {}".format(filename, e.args[0]))
            log_document[MESSAGE] = e.args[0]
            log_document[STATUS] = "ERROR"

        if log_document[STATUS] in ["EXTRACTED", "ERROR"]:
            insert_log(log_document)
