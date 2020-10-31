import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # load the instance config, if it exists
    app.config.from_mapping(
        {"SECRET_KEY": os.urandom(32),}
    )
    if test_config is not None:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    CORS(
        app, supports_credentials=True,
    )
    setup_db(app)

    """
        @Method: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
        @Method: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    """
        @Method: 
        Create an endpoint to handle GET requests 
        for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        categories = {c.id: c.type for c in Category.query.all()}
        return jsonify({"categories": categories})

    """
        @Method: 
        Create an endpoint to handle GET requests for questions, 
        including pagination (every 10 questions). 
        This endpoint should return a list of questions, 
        number of total questions, current category, categories. 

        TEST: At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions. 
  """

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        questions = Question.query.paginate(page, QUESTIONS_PER_PAGE, False).items
        if len(questions) == 0:
            abort(404)
        categories = {c.id: c.type for c in Category.query.all()}
        output = {
            "questions": [q.format() for q in questions],
            "total_questions": Question.query.count(),
            "categories": categories,
            "current_category": None,
        }
        return jsonify(output)

    """
        @Method: 
        Create an endpoint to DELETE question using a question ID. 

        TEST: When you click the trash icon next to a question, the question will be removed.
        This removal will persist in the database and when you refresh the page. 
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(404)
        try:
            question.delete()
        except:
            abort(422)
        return jsonify(success=True, id=question_id)

    """
        @Method: 
        Create an endpoint to POST a new question, 
        which will require the question and answer text, 
        category, and difficulty score.

        TEST: When you submit a question on the "Add" tab, 
        the form will clear and the question will appear at the end of the last page
        of the questions list in the "List" tab.  
    """

    @app.route("/questions", methods=["POST"])
    def post_questions():
        data = request.get_json()
        # If the request has a searchTerm, we search among existing questions
        if "searchTerm" in data:
            search_term = data.get("searchTerm").lower()
            questions = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()
            output = {
                "questions": [q.format() for q in questions],
                "total_questions": len(questions),
                "current_category": None,
            }
        elif not data:
            abort(400)
        # Otherwise, insert a new question into db
        else:
            try:
                question = Question(**data)
                question.insert()
                output = {"success": True}
            except:
                abort(422)
        return jsonify(output)

    """
        @Method: 
        Create a POST endpoint to get questions based on a search term. 
        It should return any questions for whom the search term 
        is a substring of the question. 

        TEST: Search by any phrase. The questions list will update to include 
        only question that include that string within their question. 
        Try using the word "title" to start. 
    """

    """
        @Method: 
        Create a GET endpoint to get questions based on category. 

        TEST: In the "List" tab / main screen, clicking on one of the 
        categories in the left column will cause only questions of that 
        category to be shown. 
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_by_category_id(category_id):
        category = Category.query.get(category_id)
        if not category:
            abort(404)
        questions = Question.query.filter_by(category=category_id).all()
        output = {
            "questions": [q.format() for q in questions],
            "total_questions": len(questions),
            "current_category": category.type,
        }
        if len(questions) == 0:
            abort(404)
        return jsonify(output)

    """
        @Method: 
        Create a POST endpoint to get questions to play the quiz. 
        This endpoint should take category and previous question parameters 
        and return a random questions within the given category, 
        if provided, and that is not one of the previous questions. 

        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not. 
    """

    @app.route("/quizzes", methods=["POST"])
    def return_new_quiz_question():
        data = request.get_json()
        previous_questions = data.get("previous_questions")
        category = data.get("quiz_category", {})
        category_id = category.get("id")
        if category_id == 0:
            questions = Question.query.filter(
                ~Question.id.in_(previous_questions)
            ).all()
        elif category_id is None:
            abort(404)
        else:
            questions = (
                Question.query.filter_by(category=category_id)
                .filter(~Question.id.in_(previous_questions))
                .all()
            )
        question = None if len(questions) == 0 else random.choice(questions).format()
        output = {
            "question": question,
        }
        return jsonify(output)

    """
        @Method: 
        Create error handlers for all expected errors 
        including 404 and 422. 
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Bad request"}),
            400,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify(
                {"success": False, "noterror": 405, "message": "Method not allowed"}
            ),
            405,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({"success": False, "noterror": 500, "message": "Server error"}),
            500,
        )

    return app
