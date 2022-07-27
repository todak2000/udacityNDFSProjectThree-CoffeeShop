import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# '''
# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# !! Running this funciton will add one
# '''
db_drop_and_create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')

    return response
# ROUTES
# '''
# @TODO implement endpoint
#     GET /drinks
#         it should be a public endpoint
#         it should contain only the drink.short() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
def format_long_drinks(drinks):
    formated_drinks = [drink.long() for drink in drinks]
    return formated_drinks

def format_short_drinks(drinks):
    formated_drinks = [drink.short() for drink in drinks]
    return formated_drinks

@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    formated_drinks = format_short_drinks(all_drinks)

    result = {
        'success': True,
        'drinks': formated_drinks
    }
    return jsonify(result)

# '''
# @TODO implement endpoint
#     GET /drinks-detail
#         it should require the 'get:drinks-detail' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    all_drinks = Drink.query.all()
    formatted_drinks = format_long_drinks(all_drinks)

    result = {
        'success': True,
        'drinks': formatted_drinks
    }
    return jsonify(result)

# '''
# @TODO implement endpoint
#     POST /drinks
#         it should create a new row in the drinks table
#         it should require the 'post:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
#         or appropriate status code indicating reason for failure
# '''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    body = request.get_json()
    if 'title' and 'recipe' not in body:
        abort(422)
    try:
        drink_title = body['title']
        drink_recipe = body['recipe']
        recipe = json.dumps(drink_recipe)
        newDrink = Drink(title=drink_title, recipe=recipe)
        newDrink.insert()
        
        formatted_drink = newDrink.long()

        result = {
            'success': True,
            'drink': formatted_drink
        }
        
        return jsonify(result)
    except Exception:
        abort(422)
        # print(sys.exc_info())

# '''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    
    try:
        updatedDrink = Drink.query.get(id)
        if updatedDrink is None:
            abort(404)
        if body['title'] is None:
            abort(404)

        updatedDrink.title = body['title']
        updatedDrink.update()
        formatted_drink = [updatedDrink.long()]
        result = {
            'success': True,
            'drink': formatted_drink
        }
    
        return jsonify(result)
    except Exception:
        abort(422)
        
        

    
# '''
# @TODO implement endpoint
#     DELETE /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should delete the corresponding row for <id>
#         it should require the 'delete:drinks' permission
#     returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        deletedDrink = Drink.query.get(id)
        print(id)
        if deletedDrink is None:
            abort(404)

        deletedDrink.delete()
        result = {
            'success': True,
            'delete': deletedDrink.id
        }
    
        return jsonify(result)
    except Exception:
        abort(422)

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# '''
# @TODO implement error handler for 404
#     error handler should conform to general task above
# '''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# '''
# @TODO implement error handler for AuthError
#     error handler should conform to general task above
# '''
@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), 401


