
import json
from flask import request
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from initialise import Initialise
from flask import Flask
# Creates the Flask app
app = Flask(__name__)
init = Initialise()
app = init.db(app)
# Creates the db connection
db = SQLAlchemy(app)


def hateoas(id):
    return [
                {
                    "rel": "self",
                    "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
                    "method": "GET"
                },
                {
                    "rel": "update",
                    "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
                    "method": "PATCH"
                },
                {
                    "rel": "update",
                    "resource": "http://127.0.0.1:8000/v1/users/" + str(id),
                    "method": "DELETE"
                }
            ]
@app.route('/v1/users', methods=['POST'])
def post_user_details():
    try:
        data = request.get_json()
        sql = text('INSERT INTO users (name, surname, identity_number) values (:name, :surname, :id_num)')
        result = db.engine.execute(
            sql,
            name=data['name'],
            surname=data['surname'],
            id_num = data['identity_number']
        )
        return json.dumps({"id": result.lastrowid,"links": hateoas(result.lastrowid)})
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v1/users/<user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        sql = text('SELECT * FROM users WHERE id=:id_num')
        result = db.engine.execute(sql, id_num=user_id).fetchone()
        return json.dumps({"name": result.name, "surname": result.surname, "identity_number": result.identity_number, "links": hateoas(user_id)}), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND        


@app.route('/v1/users/<user_id>', methods=['PATCH'])
def patch_user_details(user_id):
    data = request.get_json()
    """
    An update query has a portion where you specify which values to  update. Because we are  sending through a variable amount of columns to change, we need to build the clause in the  SQL that states what must change, programmatically
    """
    for key in data:
        update_string = key + '=:' + key + ','
        # Remove the last comma in the update portion
        update_string = update_string[:-1]
    try:
        data['id'] = user_id
        sql = text('UPDATE users SET ' + update_string + ' WHERE id = :id')
        result = db.engine.execute(sql, data)
        return json.dumps(
        {
            "id": user_id,
            "links": hateoas(user_id)
        })
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND        


@app.route('/v1/users/<user_id>', methods=['DELETE'])
def delete_user_details(user_id):
    try:
        sql = text('DELETE FROM users WHERE id=:id_num')
        result = db.engine.execute(sql, id_num=user_id)
        return json.dumps('Deleted'), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND        


# ORM (bject Relational Model) version ->

@app.route('/v2/users/<user_id>', methods=['GET'])
def get_user_details_orm(user_id):
    try:
        result = db.session.query(Users).filter_by(id=user_id).first()
        return json.dumps(
            {
                "name":result.name,
                "surname":result.surname,
                "identity_number":result.identity_number,
                "links": hateoas(user_id)
            }
        ), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed to retrieve record. ' + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v2/users', methods=['POST'])
def post_user_details_orm():
    try:
        data = request.get_json()
        user = Users(name=data['name'], surname=data['surname'], identity_number=data['identity_number'])
        db.session.add(user)
        db.session.commit()
        return json.dumps(
            {
                "id": user.id,
                "links": hateoas(user.id)
            }
        ), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed to add record. ' + str(e)), HTTPStatus.NOT_FOUND


@app.route('/v2/users/<user_id>', methods=['PATCH'])
def patch_user_details_orm(user_id):
    try:
        data = request.get_json()
        user = db.session.query(Users).filter_by(id=user_id).update(data)
        db.session.commit()
        return json.dumps(
            {
                "id": user_id,
                "links": hateoas(user_id)
            }
    )
    except Exception as e:
        return json.dumps('Failed to update record. ' + str(e)), HTTPStatus.NOT_FOUND

        
@app.route('/v2/users /<user_id>', methods=['DELETE'])
def delete_user_details_orm(user_id):
    try:
        user = db.session.query(Users).filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return json.dumps('Deleted'), HTTPStatus.OK
    except Exception as e:
        return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND        



def create(post_data):
    sql = text(
         'INSERT INTO users (name, surname, identity_number) values (:name, :surname,      :identity_number)'
      )
    return execute(sql, post_data)
"""
The return data here is handy to retrieve meta data from the sql operation, for instance, the id of the last inserted row.
"""
def execute(sql, data):
     return db.engine.execute(sql, data)

"""
Returns data in a json format
"""
def return_message(message):
    return json.dumps(message), HTTPStatus.OK        


def post_user_details():
   try:
       # Get the details from the request object as usual
       data = request.get_json()
       # Call the create function, passing it the data from the request object
       # This object return an object, but we don't need to use it here
       create(data)
       # Return the message 'Added'
       return return_message('Added')
   except Exception as e:
       return json.dumps('Failed. ' + str(e)), HTTPStatus.NOT_FOUND

