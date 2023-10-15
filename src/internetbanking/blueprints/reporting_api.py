from flask import Blueprint,request, jsonify
from models import Branch, Account, User, Transaction, Base  
from sqlalchemy import func, case , or_
from sqlalchemy.orm import aliased, sessionmaker, joinedload
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from db import session
from db import create_engine
from flask_jwt_extended import jwt_required, get_jwt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_URL')
db = SQLAlchemy(app)

report_api = Blueprint('report_api', __name__)

@report_api.route('/branch_report', methods=['GET'])
@jwt_required()
def branch_report():
    # Aliaskan tabel Account dan User untuk menghitung jumlah akun dan jumlah pengguna
    j = get_jwt()
    if j["is_admin"] == False:
        return jsonify ({"msg":"You Are Not Allowed"}), 401
        
    AccountAlias = aliased(Account)
    UserAlias = aliased(User)

    # Query untuk mendapatkan laporan cabang
    branch_report = (
        session.query(
            Branch.city,
            Branch.address,
            func.count(AccountAlias.id_account).label('number_of_accounts'),
            func.count(UserAlias.id_user).label('number_of_users'),
            func.sum(AccountAlias.balance).label('total_balance')
        )
        .outerjoin(AccountAlias, Branch.accounts)
        .outerjoin(UserAlias, AccountAlias.id_user == UserAlias.id_user)
        .group_by(Branch.city)
        .group_by(Branch.address)
        .all()
    )

    # Mengkonversi hasil query ke format JSON
    report_data = []
    for city,address, num_accounts, num_users, total_balance in branch_report:
        report_data.append({
            'city': city,
            'address' : address,
            'number_of_accounts': num_accounts,
            'number_of_users': num_users,
            'total_balance': total_balance
        })

    return jsonify({'branch_report': report_data})

@report_api.route('/branch_report_filter', methods=['GET'])
def get_filter():
    star_date = request.args.get('star_date')
    end_date = request.args.get('end_date')

    if not star_date or not end_date:
        return jsonify ({"error" : "Please Provide star_date and end_date"}), 400
    try:
        star_date = datetime.strptime(star_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify ({'error':'Invalid data Format. Use YYYY-MM-DD'}), 400
    
    Session = sessionmaker(bind=create_engine)
    session = Session()

    account_alias = aliased(Account)

    branch_report_filter = (
        session.query(
            Branch.city,
            func.sum(
                case(
                    [
                        (Transaction.type_transaction == 'DEBIT', Transaction.amount)
                    ],
                    else_=0
                )
            ).label('total_debit'),
            func.sum(
                case(
                    [
                        (Transaction.type_transaction == 'CREDIT', Transaction.amount)
                    ],
                    else_=0
                )
            ).label('total_credit')
        )
        .join(Account, Account.id_branch == Branch.id_branch)
        .join(Transaction, Transaction.id_transaction == account_alias.id_account)
        .filter(
            Transaction.created_at.between(star_date, end_date), 
            or_(
                Transaction.type_transaction == 'DEBIT',
                Transaction.type_transaction == 'CREDIT'
            )
        )
        .group_by(Branch.city)
        .all()
    )

    report_data = []
    for city, total_debit, total_credit in branch_report :
        report_data.append({
            'city' : city,
            'total_debit' : total_debit,
            'total_credit' : total_credit
        })

    session.close()

    return jsonify ({'branch report' : report_data})

@report_api.route('/dormant_report', methods=['GET'])
def get_dormant():
    accounts = Account.query.filter_by(is_active=False).all()
    
    dormant_accounts = []
    for account in accounts :
        branch = Branch.query.get(account.id_branch)
        
        last_transaction = Transaction.query.filter_by(id_transaction= account.id_account).order_by(Transaction.created_at.desc()).first()

        if last_transaction:
            dormant_period = datetime.now() - last_transaction.created_at
        else:
            dormant_period = None  

        dormant_account_info = {
                'Account Name' : account.account_name,
                'Balance' : account.balance,
                'isActive' : account.is_active,
                'City' : branch.city,
                'Address' : branch.address,
                'Dormant Period (days)' : dormant_period.days if dormant_period else None
        }
        dormant_accounts.append(dormant_account_info)
        return jsonify (dormant_accounts), 200


if __name__ == '__main__':
    app.run()
