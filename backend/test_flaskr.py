import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            "localhost:5432", self.database_name
        )
        self.new_question = {
            "question": "How far is the mooon away from the earth?",
            "answer": "238,900 mi",
            "category": 3,
            "difficulty": 4,
        }
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["categories"]))

    def test_get_questions_success(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))

    def test_get_questions_404(self):
        res = self.client().get("/questions?page=30")
        self.assertEqual(res.status_code, 404)

    def test_delete_question_success(self):
        res = self.client().delete("/questions/9")
        self.assertEqual(res.status_code, 200)

    def test_delete_question_404(self):
        res = self.client().delete("/questions/100")
        self.assertEqual(res.status_code, 404)

    def test_post_question_search(self):
        res = self.client().post("/questions", json={"searchTerm": "box"})
        self.assertEqual(res.status_code, 200)

    def test_post_question_insert(self):
        res = self.client().post("/questions", json=self.new_question)
        self.assertEqual(res.status_code, 200)

    def test_post_question_422(self):
        res = self.client().post("/questions", json={"test": True})
        self.assertEqual(res.status_code, 422)

    def test_post_question_400(self):
        res = self.client().post("/questions", json={})
        self.assertEqual(res.status_code, 400)

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        self.assertEqual(res.status_code, 200)

    def test_get_questions_by_category_404(self):
        res = self.client().get("/categories/tt/questions")
        self.assertEqual(res.status_code, 404)

    def test_get_quiz_question(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [],
                "quiz_category": {"type": "History", "id": "4"},
            },
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue("question" in data.keys())


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
