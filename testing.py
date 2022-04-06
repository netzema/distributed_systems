from requests import get, put, delete, post

#%% login admin
print(get('http://localhost:5000/users/api/admin').json())
print(post('http://localhost:5000/users/api/session/admin', data={'password':'admin'}))
print(get('http://localhost:5000/users/api/admin').json())

#%% create user: Welcome on board, Ted! :-)
print(post('http://localhost:5000/users/api/admin', data={'username': 'Ted', 'password':'somesupersafepassword', 'role': 'manager'}))
print(get('http://localhost:5000/users/api/Ted').json())

#%% delete user: Ted got fired again :(
print(get('http://localhost:5000/users/api/Ted').json())
print(delete('http://localhost:5000/users/api/admin', data = {'username': 'Ted'}))
print(get('http://localhost:5000/users/api/Ted').json())

#%% hire Ted again, Ted tries to hire Berta, but only admin can do that
# admin logs in
print(post('http://localhost:5000/users/api/session/admin', data={'password':'admin'}).json())
print(post('http://localhost:5000/users/api/admin', data={'username': 'Ted','password':'somesupersafepassword', 'role': 'manager'}).json())
print(get('http://localhost:5000/users/api/Ted').json())
# Ted logs in
print(post('http://localhost:5000/users/api/session/Ted', data={'password':'somesupersafepassword'}).json())
# Ted tries to hire Berta
print(post('http://localhost:5000/users/api/Ted', data={'username': 'Berta', 'password':'1234', 'role': 'secretary'}).json())
print(get('http://localhost:5000/users/api/Berta').json())
# admin hires Berta
print(post('http://localhost:5000/users/api/admin', data={'username': 'Berta', 'password':'1234', 'role': 'secretary'}).json())
print(get('http://localhost:5000/users/api/Berta').json())
# Ted got mad and wants to fire Berta again
print(delete('http://localhost:5000/users/api/Ted', data = {'username': 'Berta'}).json())
print(get('http://localhost:5000/users/api/Berta').json())
# Admin fires Berta again
print(delete('http://localhost:5000/users/api/admin', data = {'username': 'Berta'}).json())
print(get('http://localhost:5000/users/api/Berta').json())