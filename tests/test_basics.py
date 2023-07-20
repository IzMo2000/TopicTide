import unittest, sys

sys.path.append('../') # imports python file from parent directory
from app import app #imports flask app object

class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        self.app = app.test_client()

    ###############
    #### tests ####
    ###############
    
    def test_main_page(self):
        response = self.app.get('/start', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_todo(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_destination(self):
        response = self.app.get('/signup', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_about_us(self):
        response = self.app.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_todo(self):
        response = self.app.get('/tracking', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_destination(self):
        response = self.app.get('/topic_expand', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    """
    def test_about_us(self):
        response = self.app.get('/boomark', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    
    def test_about_us(self):
        response = self.app.get('/update_server', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    """

if __name__ == "__main__":
    unittest.main()