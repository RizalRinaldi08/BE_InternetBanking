import bcrypt
from flask import Flask, request, make_response, jsonify, Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, create_refresh_token
from models import User
auth = Blueprint('auth', __name__)
app = Flask(__name__)


@auth.route('login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "Username tidak ada"}), 401
    match = bcrypt.checkpw(password.encode('utf-8'),user.password.encode('utf-8'))
    print(match)

    if match == True:
        access_token = create_access_token(identity=username, 
                                            additional_claims={"is_admin": user.is_admin})
            
        refresh_token = create_refresh_token(identity=username)

        return jsonify(access_token=access_token, refresh_token=refresh_token)
    else:
        return jsonify({"msg": "Password salah"}), 401



    