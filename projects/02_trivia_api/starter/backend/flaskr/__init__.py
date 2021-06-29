import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = QUESTIONS_PER_PAGE*(page - 1)
    end = QUESTIONS_PER_PAGE+start

    selection_questions = [question.format() for question in selection]
    questions_for_page = selection_questions[start:end]

    return questions_for_page


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():

        all_categories = Category.query.order_by(Category.type).all()

        if len(all_categories) == 0:
            abort(404)

        formatted_categories = {
            category.id: category.type for category in all_categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        selection_lenght = len(selection)

        paginated_questions = paginate_questions(request, selection)

        if len(paginated_questions) == 0:
            abort(404)

        all_categories = Category.query.order_by(Category.type).all()

        category_types = [category.type for category in all_categories]

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': selection_lenght,
            'categories': category_types,
            'current_category': None
        })


    @app.route("/questions", methods=['POST'])
    def add_question():
        body = request.get_json()

        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)

        added_question = body.get('question')
        added_answer = body.get('answer')
        added_difficulty = body.get('difficulty')
        added_category = body.get('category')

        try:
            question = Question(question=added_question, answer=added_answer,
                                difficulty=added_difficulty, category=added_category)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
            })

        except:
            abort(422)

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            formatted_questions = [question.format()
                                   for question in search_results]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(search_results),
                'current_category': None
            })
        abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:

            questions = Question.query.filter(
                Question.category == category_id).all()
            questions_lenght = len(questions)
            formatted_questions = [question.format() for question in questions]
            questions_lenght = len(questions)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': questions_lenght,
                'current_category': category_id
            })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():

        try:

            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['id'] == 0:
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter(Question.id.notin_(
                    (previous_questions))).filter_by(category=category['id']).all()

            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)
          
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422
  
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500


    return app
