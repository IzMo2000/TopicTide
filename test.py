from database_utility import *

add_user('user_name', 'test@example.com', '123456')

print(get_user_info('user_name').id)