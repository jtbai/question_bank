from flask import Flask, render_template
from random import randint
from pymongo import MongoClient
from bson import ObjectId, Code
import os

flask_env = os.getenv('flask_env')
application = Flask('test_app')

if flask_env == "prod":
    debug = False
    port = 80
elif flask_env == "dev":
    debug = True
    port = 8080
else :
    raise ValueError("Aucun comportement attendu pour l'environnement {}".format(flask_env))
mongo_client = MongoClient(host="database")

midterm_questions_collection_pointer = mongo_client['glo4035']['midtermQuestions']

def obtain_random_question():
    question_pointer = midterm_questions_collection_pointer.find({})
    nb_question = question_pointer.count()
    random_question = randint(0, nb_question-1)
    return question_pointer.skip(random_question).next()

def get_stats_by_matricule():
    mon_map = Code("function(){"
                   "emit({'matricule':this.matricule, 'type':this.typeQuestion}, 1)"
                   "}")
    mon_reduce = Code("function(key, values){"
                      "return Array.sum(values)"
                      "}")
    result = midterm_questions_collection_pointer.map_reduce(mon_map, mon_reduce, "stats")
    cursor = result.find()
    return({value['_id']['matricule']:value['value'] for value in cursor})

@application.route('/')
def index_or_load_data():
    return("<a href=/random-question>Obtenir une question</a>")

@application.route('/random-question')
def show_random_question():
    question_from_db = obtain_random_question()
    question_id = question_from_db.get("_id", "")
    matricule = question_from_db.get("matricule", "")
    question = question_from_db.get("question", "")
    reponse = question_from_db.get("reponse", "")
    type_question = question_from_db.get("typeQuestion", "")

    return render_template("question.html", question_id = question_id,
                           matricule=matricule, question=question, answer=reponse, type_question=type_question)


@application.route('/monitoring')
def get_monitoring_stats():
    return get_stats_by_matricule()


@application.route('/question/<question_id>')
def get_question(question_id):
    question_from_db = midterm_questions_collection_pointer.find_one({"_id":ObjectId(question_id)})

    question_id = question_from_db.get("_id", "")
    matricule = question_from_db.get("matricule", "")
    question = question_from_db.get("question", "")
    reponse = question_from_db.get("reponse", "")
    type_question = question_from_db.get("typeQuestion", "")

    return render_template("question.html", question_id = question_id,
                           matricule=matricule, question=question, answer=reponse, type_question=type_question)

application.run('0.0.0.0',port, debug=debug)
