from requests import get, put, delete, post, login

print(get('http://localhost:5000/users/api/admin').json())
print(post('http://localhost:5000/users/api/session/admin', ).json())

print()

