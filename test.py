from database_utility import *

topics = get_tracked_topics('test_demo')

for topic in topics:
    remove_topic('test_demo', topic.topic)
