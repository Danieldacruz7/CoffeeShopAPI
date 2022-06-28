import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drinks_array = [drink.short() for drink in drinks]

    return jsonify(
        {
            'status code': 200,
            'success': True,
            "drinks": drinks_array
        }
    )

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_long(jwt):
    try:
        if jwt is None:
            abort(401)
        drinks = Drink.query.all()
        detailed_drinks_array = [drink.long() for drink in drinks]
                
        return jsonify(
                            {
                                'status code': 200,
                                'success': True,
                                "drinks": detailed_drinks_array
                            }
                            )
    except:
        abort(404)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def insert_drink(jwt):
    try: 
        body = request.get_json()
        new_recipe = body.get('recipe')
        new_title = body.get('title')

        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()  # Add data to Database.

        return jsonify(
                {
                    'status code': 200,
                    'success': True,
                    "drinks": [drink.long()]
                }
                )

    except:
        abort(403)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    try:
        if id is None:
            abort(404)

        else:
            body = request.get_json()
            new_title = body.get('title')
            new_recipe = body.get('recipe')

            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = new_title
            drink.recipe = json.dumps(new_recipe)
            drink.update()

            return jsonify(
                {
                    'status code': 200,
                    'success': True,
                    "drinks": [drink.long()]
                }
                )
    except:
        abort(404)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.delete()

        return jsonify(
            {
                'status code': 200,
                'success': True,
                "delete": drink.id
            }
            )
    except:
        abort(404)



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

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "authorization error."
    }), 401

@app.errorhandler(AuthError)
def invalid_claims(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "authorization error."
    }), 403

