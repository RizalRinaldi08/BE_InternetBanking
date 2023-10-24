from flask import Blueprint, request, jsonify, abort
from models import Account, User, Branch, Transaction,TransactionStatus
from datetime import datetime
from db import session
from flask_jwt_extended import jwt_required, get_jwt

account_api = Blueprint('account_api', __name__)

#membuat endpoint untuk get saldo


@account_api.route('/account/<uuid:id_account>', methods=['GET'])
@jwt_required()
def get_balance(id_account):
    account = Account.query.filter_by(id_account=id_account).first()
    if account == None:
        abort(404)
    j = get_jwt()
    if j["is_admin"] == False:
        return jsonify ({"msg": "you are not allowed"}), 401
    if not account:
        return {'error': 'account not found'}, 404

    return {
        'account_name': account.account_name,
        'balance': account.balance,
        'account_active': account.is_active
    }, 200


@account_api.route('/account', methods=['POST'])
@jwt_required()
def create_account():
    j = get_jwt()
    if j["is_admin"] == False:
        return jsonify ({"msg" : "you are not allowed"}), 401
    data = request.get_json()
    user = User.query.filter_by(id_user=data.get('id_user')).first()
    # branch = Branch.query.filter_by(branch_name=data.get('branch_name')).first()
    branch = Branch.query.filter_by(id_branch=data.get('id_branch')).first()
    print(user,branch)
    
    if not user :
        return { 'error': 'user not found'}, 404
    
    if not branch:
        return { 'error' : 'branch not found'}, 404    
    
    balance = data.get('balance')
    if balance is None or balance < 50000:
        return { 'error' : 'minimum balance 50.000'}, 400

    account = Account (    
        id_user = user.id_user,
        id_branch = branch.id_branch,
        account_name = data['account_name'],
        account_number = data['account_number'],
        balance = 0
    )
    session.add(account)

    transaction = Transaction (
        amount = balance,
        type_transaction = TransactionStatus.credit,
        account_number = account.account_number,
        notes = "first top up"
    )
    account.balance += balance

    session.add(transaction)
    session.commit()
    return {
        'account_name' : account.account_name,
        'balance' : account.balance,
        'account_active' : account.is_active,
        'account_number' : account.account_number,
        'name' : user.name,
        'branch' : branch.city,
        'branch_name' : branch.branch_name,
        'branch_code' : branch.branch_code,
        'address_of_branch' : branch.address, 
        'notes' : transaction.notes
    }, 201

@account_api.route('/account/<uuid:id_account>', methods=['PUT'])
@jwt_required()
def update_account(id_account):
    j = get_jwt()
    if j["is_admin"]==False:
        return jsonify ({"msg":"you are not allowed"}), 401
    data = request.get_json()
    account = Account.query.filter_by(id_account=id_account).first()
    # user = User.query.filter_by(username=data.get('username')).first()
    # branch = Branch.query.filter_by(branch_name=data.get('branch_name')).first()
    branch = Branch.query.filter_by(id_branch=data.get('id_branch')).first()
    # print(user,branch)

    account.account_name = data['account_name']
    # account.account_number = data['account_number']
    account.id_branch = data['id_branch']
    account.is_active = data['is_active']

    # if not account :
    #     return {'error': 'Account Not Found'}, 404
    
    # if 'account_name' in data:
    #     account.account_name = data['account_name']
    # if 'balance' in data:
    #     balance = data['balance']
    #     if balance < 50000:
    #         return {'error' : 'minimum balance 50.000'}, 400
    #     account.balance = balance
    # if 'is_active' in data:
    #     account.is_active = data['is_active']
    # if 'city' in data:
    #     branch = Branch.query.get(data['city'])
    #     if not branch :
    #         return {'error':'City Not Found'}, 404
    #     account.city = data['city']
    # if 'branch_name' in data:
    #     branch = Branch.query.get(data['branch_name'])
    #     if not branch :
    #         return {'error':'Branch Name Not Found'}, 404
    # if 'branch_code' in data:
    #     branch = Branch.query.get(data['branch_code'])
    #     if not branch:
    #         return{'error': 'Branch Code Not Found'}, 404
    session.commit()
    return {
        'succes' : 'account has been succesfully updated',
        'account_name' : account.account_name,
        'balance' : account.balance,
        'account_active' : account.is_active,
        'name' : account.user.name,
        'branch' : branch.city,
        'branch_name' : branch.branch_name,
        'branch_code' : branch.branch_code,
        'address_of_branch' : branch.address
    }, 201

@account_api.route('/account/close/<uuid:id_account>',methods=['PUT'])
@jwt_required()
def close_account(id_account):
    j = get_jwt()
    if j["is_admin"]==False:
        return jsonify ({"msg":"you are not allowed"})
    account = Account.query.filter_by(id_account=id_account).first()
    if not account:
        return{'error':'account not found'}, 404
    account.is_active = False
    session.commit()
    return {'message':'account closed succesfully'}