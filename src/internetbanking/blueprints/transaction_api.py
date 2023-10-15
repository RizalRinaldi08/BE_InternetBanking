from flask import Blueprint, request, jsonify
from models import Transaction, Account, TransactionStatus
from db import session
from flask import Flask
import os 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_URL')
db = SQLAlchemy(app)

transaction_api = Blueprint('transaction_api', __name__)

@transaction_api.route('/credit_transaction', methods=['POST'])
def credit_transaction():
    data = request.get_json()
    id_account = data.get('id_account')
    amount = data.get('amount')

    if id_account is None or amount is None :
        return jsonify ({'error': 'Invalid Data'}), 400
    
    account = session.query(Account).filter_by(id_account=id_account).first()


    if not account :
        return jsonify ({'error' : 'Account Not Found'}), 400
    
    if amount < 50000:
        return jsonify ({'error' : 'Minimum amount 50000'}), 400
    
    #memperbaharui saldo(balance) akun dengan menambahkan amount
    account.balance += amount

    #membuat objek transaksi
    transaction = Transaction (
        from_account_id = data['id_account'],
        to_account_id = data['id_account'],
        type_transaction = TransactionStatus.CREDIT,
        amount = data['amount']
    )

    session.add(transaction)
    session.commit()

    return jsonify ({
        'Message' : 'CREDIT Transaction Succesfully'
    })

@transaction_api.route('/debit_transaction', methods=['POST'])
def debit_transaction():
    data = request.get_json()
    id_account = data.get('id_account')
    amount = data.get('amount')

    if id_account is None or amount is None :
        return jsonify ({'error': 'Invalid Data'}), 400
    
    account = session.query(Account).filter_by(id_account=id_account).first()


    if not account :
        return jsonify ({'error' : 'Account Not Found'}), 400
    
    if account.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    if account.balance -amount < 50000:
        return jsonify ({'error' : 'Minimum balance in account 50000'}), 400
    
    #memperbaharui saldo(balance) akun dengan menambahkan amount
    account.balance -= amount

    #membuat objek transaksi
    transaction = Transaction (
        from_account_id = data['id_account'],
        to_account_id = data['id_account'],
        type_transaction = TransactionStatus.DEBIT,
        amount = data['amount']
    )

    session.add(transaction)
    session.commit()

    return jsonify ({
        'Message' : 'DEBIT Transaction Succesfully'
    })

@transaction_api.route('/transfer_transaction', methods=['POST'])
def transfer_transaction():
    data = request.get_json()
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')

    if from_account_id is None or to_account_id is None or amount is None:
        return jsonify ({'message:' : 'Invalid Data'})
    
    from_account = Account.query.filter_by(id_account=from_account_id).first()
    to_account = Account.query.filter_by(id_account=to_account_id).first()

    if not from_account or not to_account:
        return jsonify ({'error' : 'One or both account not Found'}), 404
    
    if amount < 50000:
        return jsonify ({'error': 'Minimum Transaction 50.000'}), 400
    
    if from_account.balance < amount :
        return jsonify ({'error' : 'Insufficient Balance'}), 400
    
    if from_account.balance - amount < 50000:
        return jsonify({'error': 'Insufficient Balance Saldo'}, 400)
    
    from_account.balance -= amount

    to_account.balance += amount

    transaction_form = Transaction (
        from_account_id = from_account_id,
        to_account_id = to_account_id,
        type_transaction = TransactionStatus.TRANSFER,
        amount = amount
    ) 

    # transaction_to = Transaction(
    #     to_account_id = data.get(to_account_id),
    #     type_transaction =TransactionStatus.CREDIT,
    #     amount = amount
    # )

    session.add(transaction_form)
    session.commit()

    return jsonify ({
        'Message' : 'TRANSFER Transaction Successfully'
    })

@transaction_api.route('/history', methods=['GET'])
def get_history():
    # data = request.get_json()
    transactions = Transaction.query.all()

    transaction_list = []

    for transaction in transactions:
        transaction_data = {
            "id_transaction" : transaction.id_transaction,
            "type_transaction" : transaction.type_transaction,
            "amount" : transaction.amount,
            "created_at" : transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        transaction_list.append(transaction_data)
    return jsonify ({'transaction': transaction_list})



    # from_account = Account.query.filter_by(id_account=from_account).first()
    # to_account = Account.query.filter_by(id_account=to_account).first()