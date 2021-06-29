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
        self.database_path = "postgresql://postgres:password@localhost:5432/{}".format(
            self.database_name)

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

    def test_get_paginated_questions(self):

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_get_questions_from_invalid_page(self):

        res = self.client().get('/questions?page=9999')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_non_existing_category(self):

        res = self.client().get('/categories/4324')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_categories(self):

        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))


    def test_deleting_non_existing_question(self):
        res = self.client().delete('/questions/none')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_delete_question(self):
        question = Question(question='sample question', answer='awesome answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    def test_search_questions(self):

        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'testSeachQuestion'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_add_invalid_question(self):

        res = self.client().post('/questions', json={
            'question': 'Is this question valid?',
            'answer': 'No, there is no difficulty',
            'category': 1
        })

        data = json.loads(res.data)
        self.assertEqual(data["success"], False)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["message"], "Unprocessable")

    def test_add_question(self):

        previous_number_questions = len(Question.query.all())

        res = self.client().post('/questions', json={
            'question': 'Will I pass?',
            'answer': 'Yes, your project is awesome!',
            'difficulty': 1,
            'category': 1
        })

        updated_number_question = len(Question.query.all())

        data = json.loads(res.data)
        self.assertEqual(data["success"], True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(updated_number_question,
                         previous_number_questions + 1)

    def test_search_questions(self):
        new_search = {'searchTerm': 'asd'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_invalid_search_question(self):

        res = self.client().post('/questions/search', json={'searchTerm': ''})

        data = json.loads(res.data)
        self.assertEqual(data["success"], False)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Resource not found")

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_invalid_category(self):
        res = self.client().get('/categories/invalid/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_get_random_quiz_question_invalid_category(self):
        res = self.client().post('/quizzes', json={ 'previous_questions': [] } )
        data = json.loads(res.data)

        self.assertEqual(data["success"], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["message"], "Unprocessable")

    def test_get_random_quiz_question(self):

        res = self.client().post('/quizzes',
                                 json={'previous_questions': [], 'quiz_category': {'type': "History", 'id': "4"}})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
