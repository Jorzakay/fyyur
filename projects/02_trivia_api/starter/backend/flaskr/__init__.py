import json
import os
from flask import Flask, request, abort, jsonify
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import current_time
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.exc import SQLAlchemyError
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_response(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return selection[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')

        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        result = {}
        for category in categories:
            result[category.id] = category.type

        return jsonify({"categories": result, "success": True})

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def get_all_questions():
        try:
            questions = [question.format()
                         for question in Question.query.order_by(Question.id).all()]

            categories = {category.id: category.type for category in Category.query.order_by(
                Category.id).all()}

            total_questions = len(questions)

            current_category = None

            paginated_questions = paginate_response(request, questions)
            if len(paginated_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "questions": paginated_questions,
                    "total_questions": total_questions,
                    "current_category": current_category,
                    "categories": categories
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            abort(422)

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if not question:
            abort(404)
        try:
            question.delete()
            return jsonify(None), 204
        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions', methods=['post'])
    def create_question():
        data = request.get_json()
        if 'searchTerm' in data:
            search_term = data['searchTerm']
            questions_query = Question.query.filter(Question.question.ilike(
                f"%{search_term}%")).order_by(Question.id).all()

            questions = [question.format() for question in questions_query]
            paginated_questions = paginate_response(request, questions)

            response = {
                "questions": paginated_questions,
                "total_questions": len(questions),
                "current_category": None,
                "success": True
            }
            return jsonify(response)
        try:
            question = Question(**data)
            question.insert()
            return jsonify(), 201
        except (TypeError, SQLAlchemyError):
            abort(400)
        except:
            abort(422)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_for_category(category_id):
        current_category = Category.query.filter(
            Category.id == category_id).one_or_none()
        if not current_category:
            abort(404)
        try:
            questions_query = Question.query.filter(
                Question.category == category_id)
            questions = [question.format() for question in questions_query]
            paginated_questions = paginate_response(request, questions)

            response = {
                "questions": paginated_questions,
                "total_questions": len(questions),
                "current_category": current_category.type,
                "success": True
            }
            return jsonify(response)
        except:
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def play():
        try:
            data = request.get_json()
            category = data.get('quiz_category')
            category_id = category.get('id')
            previous_questions = data.get('previous_questions')
            if category_id:
                question = Question.query.filter(
                    Question.category == category_id, Question.id.notin_(previous_questions)).first()
            else:
                question = Question.query.filter(
                    Question.id.notin_(previous_questions)).first()
            if not question:
                response = {"question": False}
            else:
                response = {"question": question.format()}
            return jsonify(response)
        except Exception as e:
            print("E: ", str(e))
            abort(422)

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "error": 404,
                "success": False,
                "message": "resource not found"
            }
        ), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify(
            {
                "error": 422,
                "success": False,
                "message": "unprocessable"
            }
        ), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                "error": 400,
                "success": False,
                "message": "bad request"
            }
        ), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(
            {
                "error": 405,
                "success": False,
                "message": "method not allowed"
            }
        ), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify(
            {
                "error": 500,
                "success": False,
                "message": "internal server error"
            }
        ), 500

    return app
