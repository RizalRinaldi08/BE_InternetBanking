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
    nomor_rekening = data.get('nomor_rekening')
    amount = data.get('amount')
    notes = data.get('notes')

    if nomor_rekening is None or amount is None :
        return jsonify ({'error': 'Invalid Data'}), 400
    
    account = session.query(Account).filter_by(nomor_rekening=nomor_rekening).first()

    if not account :
        return jsonify ({'error' : 'Account Not Found'}), 400
    
    if amount < 50000:
        return jsonify ({'error' : 'Minimum amount 50000'}), 400
    
    #memperbaharui saldo(Balance) akun dengan menambahkan amount
    account.balance += amount

    #membuat objek transaksi
    transaction = Transaction (
        nomor_rekening = data['nomor_rekening'],
        type_transaction = TransactionStatus.CREDIT,
        amount = data['amount'],
        notes = data['notes']
    )

    session.add(transaction)
    session.commit()

    return jsonify ({
        'Message' : 'CREDIT Transaction Succesfully'
    })

@transaction_api.route('/debit_transaction', methods=['POST'])
def debit_transaction():
    data = request.get_json()
    nomor_rekening = data.get('nomor_rekening')
    amount = data.get('amount')
    notes = data.get('notes')

    if nomor_rekening is None or amount is None :
        return jsonify ({'error': 'Invalid Data'}), 400
    
    account = session.query(Account).filter_by(nomor_rekening=nomor_rekening).first()


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
        nomor_rekening = data['nomor_rekening'],
        type_transaction = TransactionStatus.DEBIT,
        amount = data['amount'],
        notes = data['notes']

    )

    session.add(transaction)
    session.commit()

    return jsonify ({
        'Message' : 'DEBIT Transaction Succesfully'
    })

@transaction_api.route('/transfer_transaction', methods=['POST'])
def transfer_transaction():
    data = request.get_json()
    from_nomor_rekening = data.get('from_nomor_rekening')
    to_nomor_rekening = data.get('to_nomor_rekening')
    amount = data.get('amount')
    notes = data.get('notes')
    print(from_nomor_rekening, to_nomor_rekening, amount, notes)

    if from_nomor_rekening is None or to_nomor_rekening is None or amount is None:
        return jsonify ({'message:' : 'Invalid Data'})
    
    from_account = Account.query.filter_by(nomor_rekening=from_nomor_rekening).first()
    to_account = Account.query.filter_by(nomor_rekening=to_nomor_rekening).first()

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

    transaction_form_debit= Transaction (
        nomor_rekening = from_nomor_rekening,
        type_transaction = TransactionStatus.DEBIT,
        amount = amount,
        notes = notes
    ) 
    session.add(transaction_form_debit)

    transaction_form_credit = Transaction(
        nomor_rekening = to_nomor_rekening,
        type_transaction =TransactionStatus.CREDIT,
        amount = amount,
        notes = notes
    )

    session.add( transaction_form_credit)
    session.commit()

    return jsonify ({
        'Message' : 'TRANSFER Transaction Successfully'
    })

@transaction_api.route('/history', methods=['GET'])
def get_history():
    data = request.get_json()
    nomor_rekening = data.get('nomor_rekening')
    transactions = Transaction.query.filter_by(nomor_rekening=nomor_rekening).order_by(Transaction.created_at.asc()).all()

    print(transactions)


    # transactions = Transaction.query.filter(or_(Transaction.from_nomor_rekening == nomor_rekening, Transaction.to_nomor_rekening == nomor_rekening)).order_by(Transaction.created_at.asc()).all()
    # User.query.order_by(User.popularity.desc(), User.date_created.desc()).limit(10).all()
    # print(transactions)
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
    #     if transaction.from_nomor_rekening != transaction.to_nomor_rekening:
    #         if transaction.from_nomor_rekening == nomor_rekening:
    #             transaction_data['DEBIT'] = -1*transaction.amount
    #             transaction_data['CREDIT'] = 000
    #         else:
    #             transaction_data['CREDIT'] = transaction.amount
    #             transaction_data['DEBIT'] = 000
    #     else :
    #         if transaction.amount > 0 :
    #             transaction_data['CREDIT'] = transaction.amount
    #             transaction_data['DEBIT'] = 000
    #         else :
    #             transaction_data['DEBIT'] = -1*transaction.amount
    #             transaction_data['CREDIT'] = 000

        transaction_list.append(transaction_data)
    # for e in transaction_list:
    #     print(e)
    return jsonify ({'transaction': transaction_list})




    # from_account = Account.query.filter_by(id_account=from_account).first()
    # to_account = Account.query.filter_by(id_account=to_account).first()