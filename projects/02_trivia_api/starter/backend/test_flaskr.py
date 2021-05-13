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
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question':  'Heres a new question string',
            'answer':  'Heres a new answer string',
            'difficulty': 1,
            'category': 3
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get("/categories")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertTrue(data["success"])

    def test_get_questions(self):
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertEqual(data['current_category'], None)

    def test_get_questions_beyond_bounds(self):
        response = self.client().get('/questions?page=1000')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertTrue(data["error"])
        self.assertEqual(data["message"], 'resource not found')
        self.assertEqual(data['error'], 404)

    # def test_delete_question(self):
    #     response = self.client().delete('/questions/5')
    #     self.assertEqual(response.status_code, 204)
    #     question = Question.query.filter(Question.id == 5).one_or_none()
    #     self.assertEqual(question, None)

    def test_delete_unknown_question_fails(self):
        response = self.client().delete('/questions/1')
        self.assertEqual(response.status_code, 404)

    def test_create_new_question(self):
        response = self.client().post('/questions', json=self.new_question)
        self.assertEqual(response.status_code, 201)
        newest_question = Question.query.order_by(Question.id.desc()).first()
        self.assertEqual(newest_question.question,
                         self.new_question['question'])
        self.assertEqual(newest_question.answer, self.new_question['answer'])
        self.assertEqual(newest_question.difficulty,
                         self.new_question['difficulty'])
        self.assertEqual(newest_question.category,
                         self.new_question['category'])

    def test_create_question_with_nonsense(self):
        new_question = {
            "noitsueq": "This is a backwards question",
            "ategory": 2,
        }
        response = self.client().post('/questions', json=new_question)
        self.assertEqual(response.status_code, 400)

    def test_search_questions(self):
        response = self.client().post(
            '/questions', json={"searchTerm": "What"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["total_questions"], 8)
        self.assertEqual(data['current_category'], None)

    def test_search_questions_no_results(self):
        response = self.client().post(
            '/questions', json={"searchTerm": "WhatWhatWhat"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertFalse(len(data["questions"]))
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data['current_category'], None)

    def test_get_questions_for_category(self):
        response = self.client().get('/categories/1/questions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data.get('total_questions'), 3)
        for question in data.get('questions'):
            self.assertEqual(question.get('category'), 1)
        self.assertEqual(data.get('current_category'), 'Science')

    def test_get_questions_for_unknown_category(self):
        response = self.client().get('/categories/7/questions')
        self.assertEqual(response.status_code, 404)

    def test_get_quiz_question(self):
        previous_quesions = [20, 21]
        quiz_data = {
            "previous_questions": previous_quesions,
            "quiz_category": {
                "type": "click",
                "id": 0
            }
        }
        response = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(data['question']['id'], previous_quesions)
        self.assertTrue(data['question'])

    def test_get_quiz_question_false_for_no_questions_left(self):
        previous_quesions = [20, 21, 22]
        quiz_data = {
            "previous_questions": previous_quesions,
            "quiz_category": {
                "type": "Science",
                "id": 1
            }
        }
        response = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['question'])

    def test_404_handled(self):
        response = self.client().get('/categories/1/questions/4')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertFalse(data['success'])

    def test_400_handled(self):
        new_question = {
            "noitsueq": "This is a backwards question",
            "ategory": 2,
        }
        response = self.client().post('/questions', json=new_question)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')
        self.assertFalse(data['success'])

    def test_405_handled(self):
        response = self.client().post('/categories/1/questions', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], 'method not allowed')
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
