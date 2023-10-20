from flask import request, jsonify
from models import Branch, Account, Transaction, User, TransactionStatus
from db import session
from datetime import datetime
from sqlalchemy import func, text
from sqlalchemy.orm import aliased

def get_report_filter(start_date, end_date, branch_name):
    # data = request.get_json()
    # start_date = data.get('start_date')
    # end_date = data.get('end_date')
    # branch_name = data.get('branch_name')

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

def get_history_account(nomor_rekening):
    transactions = Transaction.query.filter_by(nomor_rekening=nomor_rekening).order_by(Transaction.created_at.asc()).all()

    transaction_list = []

    last_balance = 0
    for transaction in transactions:
        transaction_data = {
            "Balance" : last_balance,
            "Tanggal Transaksi" : transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        if transaction.type_transaction == TransactionStatus.CREDIT:
            transaction_data['CREDIT'] = transaction.amount
            transaction_data['DEBIT'] = 0
            transaction_data['Balance'] += transaction.amount
        else:
            transaction_data['DEBIT'] = transaction.amount
            transaction_data['CREDIT'] = 0
            transaction_data['Balance'] -= transaction.amount
        last_balance = transaction_data['Balance']
        transaction_data['notes'] = transaction.notes
    
        transaction_list.append(transaction_data)
    
    return {'transaction': transaction_list}

def get_branch():
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
    for city,branch_name, branch_code,address, num_accounts, num_users, total_balance, in branch_report:
        report_data.append({
            'city': city,
            'address' : address,
            'branch_name': branch_name,
            'branch_code' : branch_code,
            'number_of_accounts': num_accounts,
            'number_of_users': num_users,
            'total_balance': total_balance
        })

    return {'branch_report': report_data}

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
                'is_active' : account.is_active,
                'City' : branch.city,
                'Branch_name' : branch.branch_name,
                'Address' : branch.address,
                'Dormant Period (days)' : dormant_period.days if dormant_period else None
        }
        dormant_accounts.append(dormant_account_info)
    return dormant_accounts