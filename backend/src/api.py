import os
from unicodedata import name
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import ssl

# Avoid certificate error
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # Try to get all drinks avalaible on DB, if nothing returned rise an Exception
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]

    except BaseException:
        abort(422)
        
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    # Try to get all drinks avalaible on DB with some details, if nothing returned rise an Exception
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        print(drinks)
        
    except BaseException:
        abort(422)
        
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):

    body = request.get_json()
    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    
    # Try to add new drink on DB based on user input on frontend.
    try:
        drink = Drink(title = new_title, recipe = json.dumps(new_recipe))

        if new_title and new_recipe:
            drink.insert()
        else:
            abort(400)
        
    except BaseException:
        abort(400)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    # Try to update one drink by his ID. If an error occur, rise an Exception
    try:
        drink_to_update = Drink.query.get_or_404(drink_id)
        body = request.get_json()
        updated_title = body.get("title", None)
        updated_recipe = body.get("recipe", None)

        if updated_title :
            drink_to_update.title = updated_title
        
        if updated_recipe :
            drink_to_update.recipe = json.dumps(updated_recipe)
        
        drink_to_update.update()

    except BaseException:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink_to_update.long()]
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_one_drink(payload, drink_id):
    # Try to delete one drink by his ID. If an error occur, rise an Exception
    try:
        drink_to_delete = Drink.query.get_or_404(drink_id)
        drink_to_delete.delete()
        
    except BaseException:
        abort(422)

    return jsonify({
        "success": True,
        "delete": drink_id
    }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def AuthError(error):
  response = jsonify(error)
  response.status_code = error.status_code
  
  return response

if __name__ == "__main__":
    app.debug = True
    app.run(ssl_context='adhoc')
