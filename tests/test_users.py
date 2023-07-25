import unittest, sys, os

sys.path.append('../../TopicTide')
from database_utility import add_user, add_topic, add_article, add_bookmark, remove_bookmark, remove_topic, get_tracked_articles, get_bookmarks, get_user_info

# Define a test class that inherits from unittest.TestCase
class TestDatabaseFunctions(unittest.TestCase):

    # Test add_user function
    def test_add_user(self):
        add_user("test_user", "test@example.com", "password123")
        user_info = get_user_info("test_user")
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info.username, "test_user")
        self.assertEqual(user_info.email, "test@example.com")
        self.assertEqual(user_info.password, "password123")

    # Test add_topic function
    def test_add_topic(self):
        add_user("test_user", "test@example.com", "password123")
        user = get_user_info("test_user")
        self.assertIsNotNone(user, "User not found.")

        add_topic("test_user", "politics", nation="USA", language="en", update_interval=1, source="nytimes")
        # Retrieve the tracked articles for the user
        tracked_articles = get_tracked_articles("test_user")
        # Check if tracked articles were added correctly
        self.assertIsNotNone(tracked_articles, "Tracked articles not found.")
        #self.assertEqual(len(tracked_articles), 1)


# Run the tests
if __name__ == '__main__':
    unittest.main()
