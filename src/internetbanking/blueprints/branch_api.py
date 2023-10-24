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
        return {"msg":"you are not allowedd"}, 401
    data = request.get_json()

    branch = Branch (
        city = data['city'],
        address = data['address'],
        branch_name = data['branch_name'],
        branch_code = data['branch_code']
    )
    session.add(branch)
    session.commit()
    return {
        'city' : branch.city,
        'address' : branch.address,
        'branch_code' : branch.branch_code,
        'branch_name' : branch.branch_name
    }, 201

@branch_api.route('/branch/<uuid:id_branch>', methods= ['PUT'])
@jwt_required()
def update_branch(id_branch):
    j = get_jwt()
    if j["is_admin"] == False :
        return {"msg":"you are not allowed"}, 401
    data = request.get_json()
    branch = Branch.query.filter_by(id_branch=id_branch).first()
    branch.city = data['city']
    branch.branch_name = data['branch_name']
    branch.address = data['address']
    branch.branch_code = data['branch_code']
    session.commit()
    return {
        'message' : 'branch data has been succesfully updated',
        'city' : branch.city,
        'address' : branch.address,
        'branch_name' : branch.branch_name,
        'branch_code' : branch.branch_code
    }, 201