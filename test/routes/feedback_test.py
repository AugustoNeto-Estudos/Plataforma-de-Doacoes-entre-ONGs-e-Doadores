import unittest
from flask import Flask
from routes.feedback import feedback_bp

class FeedbackRoutesTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.secret_key = "test_secret"
        app.register_blueprint(feedback_bp)
        self.client = app.test_client()
        self.app = app

if __name__ == "__main__":
    unittest.main()
