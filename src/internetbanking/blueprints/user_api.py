from flask_bcrypt import Bcrypt
from flask import Blueprint, request, jsonify, Flask
from models import User
from datetime import datetime
from db import session
from flask_jwt_extended import jwt_required, get_jwt

user_api = Blueprint('user_api', __name__)
app = Flask(__name__)
bcrypt = Bcrypt(app)


@user_api.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    j = get_jwt()
    if j["is_admin"]==False:
        return {"msg":"You Are Not Allowed"}, 401
    users = User.query.all()
    user_list = []

    for user in users:
        user_data = {
        "name": user.name,
        "Username": user.username,
        "address": user.address,
        "phone_number" :user.phone_number,
        "is_admin": user.is_admin
        }
        user_list.append(user_data)

    return jsonify (user_list), 200
    
    

@user_api.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    password = data.get("password", None)
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    # print(data)
    user = User (
        name = data['name'],
        address = data['address'],
        phone_number = data['phone_number'],
        # created_at=datetime.now(),
        username = data['username'],
        password = hashed_password,
        is_admin = data['is_admin']
    )
    # print
    # (user)
    session.add(user)
    session.commit()
    return {
        'name' : user.name,
        'address' : user.address,
        'phone_number' : user.phone_number,
        'created_at' : user.created_at,
        'is_admin' : user.is_admin
    }, 201

@user_api.route('/user/<uuid:id_user>', methods=['PUT'])
def update_user(id_user):
    data = request.get_json()
    print(id_user)
    password = data.get("password")
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User.query.filter_by(id_user=id_user).first()
    user.name = data['name']
    user.address = data['address']
    user.phone_number = data['phone_number']
    user.username = data['username']
    user.password = hashed_password
    session.commit()
    return {
        'message' : 'your data has been succesfully updated',
        'name' : user.name,
        'username' : user.username,
        'address' : user.address,
        'phone_number' : user.phone_number
    }, 201
        