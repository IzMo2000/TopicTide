from database_utility import *

add_user('dummy_user', 'test@example.com','1234567')

print(get_user_info('dummy_user').email)

for i in range(5):
    add_article('dummy_user', 'student debt', f'test.com{i}', f'article{i}','testing','picture')

for i in range(5):
    add_article('dummy_user2', 'student debt', f'test.com{i}', f'article{i}','testing','picture')

result = get_tracked_articles('dummy_user')

for n in result:
    print(n.title)