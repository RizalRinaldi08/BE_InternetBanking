from flask import Blueprint,request, jsonify
from models import Branch, Account, User, Transaction, Base  
from sqlalchemy import func, text
from sqlalchemy.orm import aliased, sessionmaker, joinedload
from flask import Flask
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from db import session
from db import create_engine
from flask_jwt_extended import jwt_required, get_jwt
# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_URL')
# db = SQLAlchemy(app)

report_api = Blueprint('report_api', __name__)

@report_api.route('/branch_report', methods=['GET'])
@jwt_required()
def branch_report():
    j = get_jwt()
    if j["is_admin"] == False:
        return jsonify ({"msg":"You Are Not Allowed"}), 401

    # Aliasing tabel Account dan User untuk menghitung jumlah akun dan jumlah pengguna 
    AccountAlias = aliased(Account)
    UserAlias = aliased(User)

    # Query untuk mendapatkan laporan cabang
    branch_report = (
        session.query(
            Branch.city,
            Branch.address,
            Branch.branch_name,
            Branch.branch_code,
            func.count(AccountAlias.id_account).label('number_of_accounts'),
            func.count(UserAlias.id_user).label('number_of_users'),
            func.sum(AccountAlias.balance).label('total_balance')
        )
        .outerjoin(AccountAlias, Branch.accounts)
        .outerjoin(UserAlias, AccountAlias.id_user == UserAlias.id_user)
        .group_by(Branch.city)
        .group_by(Branch.address)
        .group_by(Branch.branch_name)
        .group_by(Branch.branch_code)

        .all()
    )

    # Mengkonversi hasil query ke format JSON
    report_data = []
    for city,address ,branch_name, branch_code, num_accounts, num_users, total_balance, in branch_report:
        report_data.append({
            'city': city,
            'address' : address,
            'branch_name': branch_name,
            'branch_code' : branch_code,
            'number_of_accounts': num_accounts,
            'number_of_users': num_users,
            'total_balance': total_balance
        })

    return jsonify({'branch_report': report_data})

@report_api.route('/dormant_report', methods=['GET'])
def get_dormant():
    # session.query
    accounts = session.query(
        Account.account_name, 
        Account.balance, 
        Account.is_active, 
        Branch.branch_name,
        Transaction.created_at
    ).outerjoin(
        Branch, 
        Branch.id_branch == Account.id_branch
    ).outerjoin(
        Transaction, 
        Transaction.nomor_rekening == Account.nomor_rekening
    ).filter(
        Account.is_active.is_(False)
    ).order_by(
        Transaction.created_at.desc()
    ).all()
    # print(accounts)
    dormant_accounts = [{
        'account_name': account.account_name,
        'balance': account.balance,
        'is_active': account.is_active,
        'branch_name': account.branch_name,
        'dormant_period(days)': f'{(datetime.now() - account.created_at).days} days'
    } for account in accounts]

    
    return jsonify (dormant_accounts), 200


@report_api.route('/branch_report_filter', methods=['GET'])
@jwt_required()
def get_filter():
    j = get_jwt()
    if j["is_admin"]==False:
        return jsonify ({"msg":"You Are Not Allowed"})
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    branch_name = data.get('branch_name')

    query = text(
        f"select t.type_transaction,sum(t.amount)\
            from tb_transaction as t\
            join tb_account as a on a.nomor_rekening = t.nomor_rekening\
            where t.created_at >= '{start_date}' and t.created_at <= '{end_date}' and a.id_branch =\
            (SELECT id_branch from tb_branch\
                where tb_branch.branch_name='{branch_name}')\
                group by t.type_transaction;"
        )
    result= session.execute(query).mappings().all()
    
    result = [dict(c) for c in result]
    print(result)
    result2 = {
        "branch_name": branch_name,
        "start_date": start_date,
        "end_date": end_date
    }
    for r in result:
        if 'type_transaction' in r and r['type_transaction']=='DEBIT' :
            result2['DEBIT'] = r['sum']
    if 'DEBIT' not in result2:
        result2['DEBIT'] = 0

    for r in result:
        if 'type_transaction' in r and r['type_transaction']=='CREDIT' :
            result2['CREDIT'] = r['sum']
    if 'CREDIT' not in result2:
        result2['CREDIT'] = 0
 
    if 'CREDIT' not in result2:
        print("tidak ada")
    print(result2)
    return result2
   