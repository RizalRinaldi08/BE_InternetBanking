from flask import Blueprint, request
from models import Branch
from db import session
from flask_jwt_extended import jwt_required, get_jwt

branch_api = Blueprint('branch_api', __name__)

@branch_api.route('/branch', methods=['GET'])
def get_branch():
    return "Berhasil"

@branch_api.route('/branch', methods=['POST'])
@jwt_required()
def create_branch():
    j = get_jwt()
    if j["is_admin"] == False:
        return {"msg":"You Are Not Allowed"}, 401
    data = request.get_json()

    branch = Branch (
        city = data['city'],
        address = data['address']
    )
    session.add(branch)
    session.commit()
    return {
        'City' : branch.city,
        'Address' : branch.address
    }, 201

@branch_api.route('/branch/<int:id>', methods= ['PUT'])
@jwt_required()
def update_branch(id):
    j = get_jwt()
    if j["is_admin"] == False :
        return {"msg":"You Are Not Allowe"}, 401
    data = request.get_json()
    branch = Branch.query.filter_by(id_branch=id).first()
    branch.city = data['city']
    branch.address = data['address']
    session.commit()
    return {
        'Message' : 'Branch Data Has Been Succesfully Updated',
        'City' : branch.city,
        'Address' : branch.address
    }, 201