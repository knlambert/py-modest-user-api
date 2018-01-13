
# Introduction

This repository is a python lib designed to handle the authentication on my personal projects. 
The projects uses :
 - Python2.
 - SQLAlchemy.
 - Flask.
 - PBKDF2 algorithm.
 - A JWT token.

# Setting up

## Installation

To install the lib :

```bash
pip2 install https://github.com/knlambert/py-modest-user-api.git
```

## The database

Execute the database/schema.sql file given in the repository.

```sql
source database/schema.sql
```
## Flask adapter

### Base setup
```python
# coding: utf-8

from flask import Flask
from user_api import create_user_api

# create flask server
app = Flask(__name__)
app.debug = True

# Create user api object
user_api = create_user_api(
    db_url=u"mysql://root:localroot1234@127.0.0.1/user_api",
    jwt_secret=u"DUMMY"
)

# Register the blueprint
app.register_blueprint(
    user_api.get_flask_adapter().construct_blueprint(),
    url_prefix=u"/api/users"
)

# Run flask server
app.run(port=5000, debug=True)
```

### Enable auth on an endpoint

Just use the built-in "is_connected" decorator for flask.

```python
app = Flask(__name__)

@app.route(u'/dummy', methods=[u'GET'])
@user_api.is_connected 
def dummy_route():
    return jsonify({
        "message": "Let's rock !"
    })
```


# API

## How does the session work ?

Some services will send you a 401 if your are not authenticated.
To evoid that, do not forget to set the authentication header.
```bash
Authentication: Bearer eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0
```
The API also works with a auth cookie which is set server side at connection.

## Authentify

Use this service to connect your user.
Send email & password to get a token.

```bash
POST http://localhost:5000/api/users/login
{
  "email": "dummy@dummy.net",
  "password": "JustMyPassword"
}
```
```bash
{
  "token": "eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0"
}
```

## Reset password [Authenticated]

Use this service to reset the password of a user.
Send email & password, get an updated Token.

You must be connected to use this service.

Payload :

```bash
POST http://localhost:5000/api/users/reset-password
{
    "email": "dummy@dummy.net",
    "password": "JustMyPassword"
}
```
```bash
{
  "token": "eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0"
}
```

## Register a new user [Authenticated]

Use this web service to create a user.

You must be connected to use this service.

Payload 
```bash
POST http://localhost:5000/api/user/register
{
    "email": "dummy@dummy.net",
    "password": "JustMyPassword",
    "name": "Dummy Doe"
}
```
```bash
{
    "email": "dummy@dummy.net",
    "password": "JustMyPassword",
    "name": "Dummy Doe"
    "id": 42,
    "active": true 
}
```

## Get connected user information [Authenticated]

When your user is authenticated, the password should never be sent again.
Then, use this service to check the token, and extract the information stored inside.
Please pay attention to the "exp" field. This is an UTC timestamp giving you the expiration date of the token.

Past this time, the token is not going to work anymore.

You must be connected to use this service.

```bash
GET http://localhost:5000/api/users/me
```
```bash
{
  "email": "dummy@dummy.net", 
  "exp": 1497989335, 
  "id": 2, 
  "name": "Dummy Doe"
}
```
