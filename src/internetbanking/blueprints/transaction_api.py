from flask import Blueprint, request, jsonify
from models import Transaction, Account, TransactionStatus
from db import session
from flask import Flask
from sqlalchemy import or_
import os 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_URL')
db = SQLAlchemy(app)

transaction_api = Blueprint('transaction_api', __name__)

@transaction_api.route('/credit_transaction', methods=['POST'])
def credit_transaction():
    data = request.get_json()
    account_number = data.get('account_number')
    amount = data.get('amount')
    notes = data.get('notes')

    if account_number is None or amount is None :
        return jsonify ({'error': 'invalid data'}), 400
    
    account = session.query(Account).filter_by(account_number=account_number).filter_by(is_active=True).first()

    if not account :
        return jsonify ({'error' : 'account not found'}), 400
    
    if amount < 50000:
        return jsonify ({'error' : 'minimum amount 50000'}), 400
    
    #memperbaharui saldo(Balance) akun dengan menambahkan amount
    account.balance += amount

    #membuat objek transaksi
    transaction = Transaction (
        account_number = data['account_number'],
        type_transaction = TransactionStatus.credit,
        amount = data['amount'],
        notes = data['notes']
    )

    session.add(transaction)
    session.commit()

    return jsonify ({
        'Message' : 'credit transaction succesfully'
    })

@transaction_api.route('/debit_transaction', methods=['POST'])
def debit_transaction():
    data = request.get_json()
    account_number = data.get('account_number')
    amount = data.get('amount')
    notes = data.get('notes')

    if account_number is None or amount is None :
        return jsonify ({'error': 'invalid data'}), 400
    
    account = session.query(Account).filter_by(account_number=account_number).filter_by(is_active=True).first()


    if not account :
        return jsonify ({'error' : 'account not found'}), 400
    
    if account.balance < amount:
        return jsonify({'error': 'insufficient balance'}), 400
    
    if account.balance -amount < 50000:
        return jsonify ({'error' : 'minimum balance in account 50000'}), 400
    
    #memperbaharui saldo(balance) akun dengan menambahkan amount
    account.balance -= amount

    #membuat objek transaksi
    transaction = Transaction (
        account_number = data['account_number'],
        type_transaction = TransactionStatus.debit,
        amount = data['amount'],
        notes = data['notes']

    )

    session.add(transaction)
    session.commit()

    return jsonify ({
        'message' : 'debit transaction succesfully'
    })

@transaction_api.route('/transfer_transaction', methods=['POST'])
def transfer_transaction():
    data = request.get_json()
    from_account_number = data.get('from_account_number')
    to_account_number = data.get('to_account_number')
    amount = data.get('amount')
    notes = data.get('notes')
    print(from_account_number, to_account_number, amount, notes)

    if from_account_number is None or to_account_number is None or amount is None:
        return jsonify ({'message:' : 'invalid data'})
    
    from_account = session.query(Account).filter_by(account_number=from_account_number).filter_by(is_active=True).first()
    to_account = session.query(Account).filter_by(account_number=to_account_number).filter_by(is_active=True).first()
    # to_account = Account.query.filter_by(account_number=to_account_number).filter_by(is_active=True).first()


    if not from_account or not to_account:
        return jsonify ({'error' : 'one or both account not found'}), 404
    
    if amount < 50000:
        return jsonify ({'error': 'minimum transaction 50.000'}), 400
    
    if from_account.balance < amount :
        return jsonify ({'error' : 'insufficient balance'}), 400
    
    if from_account.balance - amount < 50000:
        return jsonify({'error': 'insufficient balance saldo'}, 400)
    
    from_account.balance -= amount

    to_account.balance += amount

    transaction_form_debit= Transaction (
        account_number = from_account_number,
        type_transaction = TransactionStatus.debit,
        amount = amount,
        notes = notes
    ) 
    session.add(transaction_form_debit)

    transaction_form_credit = Transaction(
        account_number = to_account_number,
        type_transaction =TransactionStatus.credit,
        amount = amount,
        notes = notes
    )

    session.add( transaction_form_credit)
    session.commit()

    return jsonify ({
        'message' : 'transfer transaction successfully'
    })

@transaction_api.route('/history', methods=['GET'])
def get_history():
    data = request.get_json()
    account_number = data.get('account_number')
    transactions = Transaction.query.filter_by(account_number=account_number).order_by(Transaction.created_at.asc()).all()
    # print(transactions)

    transaction_list = []

    last_balance = 0
    for transaction in transactions:
        transaction_data = {
            "balance" : last_balance,
            "transaction_date" : transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        if transaction.type_transaction == TransactionStatus.credit:
            transaction_data['credit'] = transaction.amount
            transaction_data['debit'] = 0
            transaction_data['balance'] += transaction.amount
        else:
            transaction_data['debit'] = transaction.amount
            transaction_data['credit'] = 0
            transaction_data['balance'] -= transaction.amount
        last_balance = transaction_data['balance']
        transaction_data['notes'] = transaction.notes
    #     if transaction.from_account_number != transaction.to_account_number:
    #         if transaction.from_account_number == account_number:
    #             transaction_data['debit'] = -1*transaction.amount
    #             transaction_data['credit'] = 000
    #         else:
    #             transaction_data['credit'] = transaction.amount
    #             transaction_data['debit'] = 000
    #     else :
    #         if transaction.amount > 0 :
    #             transaction_data['credit'] = transaction.amount
    #             transaction_data['debit'] = 000
    #         else :
    #             transaction_data['debit'] = -1*transaction.amount
    #             transaction_data['credit'] = 000

        transaction_list.append(transaction_data)
    # for e in transaction_list:
    #     print(e)
    return jsonify ({'transaction': transaction_list})




    # from_account = Account.query.filter_by(id_account=from_account).first()
    # to_account = Account.query.filter_by(id_account=to_account).first()