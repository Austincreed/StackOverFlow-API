from app import app
from model.user_model import user_model #user_model class is imported
from flask import request, send_file
from datetime import datetime
from flask import make_response
import requests
obj = user_model()

# 1. CREATE TABLES
@app.route("/user/createtable")
def user_createtable_controller():
    return obj.create_tables()


# 2. POST - LOAD data from API to Local Database
@app.route('/questions/load', methods=['POST'])
def load_questions():
    try:
        obj.load_questions_from_api()
        return make_response({'message': 'Questions loaded successfully'}, 200)

    except Exception as e:
        return make_response({'error': str(e)}, 500)


# 3. GET questions from Local-Database
@app.route("/get", methods=['GET'])
def user_getquestion_controller():
    return obj.user_getquestion_model()


# 4. GET questions from Local-Database using filters
@app.route("/get/questions/limit/<limit>/page/<page>", methods=['GET'])
def user_filterquestion_controller(limit, page):
    # filtering is done by using 'is_answered', 'tags', 'answer_count'
    filters = {
        'is_answered':request.args.get('is_answered'),
        'tags':request.args.get('tags'),
        'answer_count':request.args.get('answer_count')
    }
    
    # sort_by score
    sort_by = request.args.get('score', 'creation_date')
    
    return obj.user_filterquestion_model(filters, sort_by, limit, page)



# 5. GET questions using question_id
@app.route("/get/questions/<question_id>", methods=["GET"])
def user_getquestionsbyid_controller(question_id):
    return obj.user_getquestionbyid_model(question_id)



# 6. POST QUESTION
@app.route("/post/question", methods=["POST"])
def user_postquestion_controller():
    return obj.user_postquestion_model(request.form)



# 7. PUT QUESTION
@app.route("/put/question", methods=['PUT'])
def user_putquestion_controller():
    return obj.user_putquestion_model(request.form)


# 8. PATCH QUESTION IN THE TABLE
@app.route("/patch/question/<question_id>", methods=["PATCH"])
def user_patchquestion_controller(question_id):
    return obj.user_patchquestion_model(request.form, question_id)


# 9. DELETE questions in the TABLE
@app.route("/delete/question/<id>", methods=["DELETE"])
def user_deletequestion_controller(id):
    return obj.user_deletequestion_model(id)



