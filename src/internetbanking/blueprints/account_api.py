from flask import Blueprint, request, jsonify
from models import Account, User, Branch
from datetime import datetime
from db import session
from flask_jwt_extended import jwt_required, get_jwt


account_api = Blueprint('account_api', __name__)

#membuat endpoint untuk get saldo


@account_api.route('/account/<int:id_account>', methods=['GET'])
@jwt_required()
def get_balance(id_account):
    account = Account.query.get(id_account)
    j = get_jwt()
    if j["is_admin"] == False:
        return jsonify ({"msg": "You Are Not Allowed"}), 401
    # print (j["role"])
    if not account:
        return {'error': 'Account Not Found'}, 404

    return {
        'Account Name': account.account_name,
        'Balance': account.balance,
        'Account Active': account.is_active
    }, 200


@account_api.route('/account', methods=['POST'])
def create_account():
    data = request.get_json()
    user = User.query.get(data['id_user'])
    branch = Branch.query.get(data['id_branch'])
    
    if not user :
        return { 'error': 'User not found'}, 404
    
    if not branch:
        return { 'error' : 'Branch not found'}, 404    
    
    balance = data.get('balance')
    if balance is None or balance < 50000:
        return { 'error' : 'Minimum Balance 50.000'}, 400

    account = Account (    
        id_user = data['id_user'],
        account_name = data['account_name'],
        balance = balance,
        id_branch = data['id_branch']
    )
    session.add(account)
    session.commit()
    return {
        'Account Nama' : account.account_name,
        'Balance' : account.balance,
        'Acount Active' : account.is_active,
        'Nama' : user.nama,
        'Branch' : branch.city,
        'Address of Branch' : branch.address
    }, 201

@account_api.route('/account/<int:id>', methods=['PUT'])
def update_account(id):
    data = request.get_json()
    account = Account.query.filter_by(id_account=id).first()

    if not account :
        return {'error': 'Account Not Found'}, 404
    
    if 'account_name' in data:
        account.account_name = data['account_name']
    if 'balance' in data:
        balance = data['balance']
        if balance < 50000:
            return {'error' : 'Minimum balance 50.000'}, 400
        account.balance = balance
    if 'is_active' in data:
        account.is_active = data['is_active']
    if 'id_branch' in data:
        branch = Branch.query.get(data['id_branch'])
        if not branch :
            return {'error':'Branch Not Found'}, 404
        account.id_branch = data['id_branch']
    session.commit()
    return {
        'Succes' : 'Account Has Been Succesfully Updated',
        'Account Nama' : account.account_name,
        'Balance' : account.balance,
        'Acount Active' : account.is_active,
        'Nama' : account.user.nama,
        'Branch' : account.branch.city,
        'Address of Branch' : account.branch.address
    }, 201

@account_api.route('/account/:id/close',methods=['PUT'])
def close_account(id):
    account = Account.query.get(id_account=id)
    if not account:
        return{'error':'Account not found'}, 404
    account.is_active = False
    session.commit()
    return {'message':'Account Closed Succesfully'}