from flask import Blueprint, request, jsonify, send_file
from models import Branch, Account
from db import session
from flask_jwt_extended import jwt_required, get_jwt
from .utils import get_history_account, get_report_filter, get_branch, get_dormant
import pandas as pd
import io
import json

download_api = Blueprint('download_api', __name__)

@download_api.route('/download', methods=['GET'])
def get_download():
    q = request.args.get("q")
    if q == "get_history_account":
        nomor_rekening = request.args.get('nomor_rekening')
        results = get_history_account(nomor_rekening)
        df = pd.DataFrame(results)
        response_stream = io.BytesIO(df.to_csv().encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name="history_account.csv"
        )
    
    elif q == "get_branch":
        results = get_branch()
        df = pd.DataFrame(results)
        response_stream = io.BytesIO(df.to_csv().encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name="branch_report.csv"
        )
    elif q == "get_dormant":
        results = get_dormant()
        df = pd.DataFrame(results)
        response_stream = io.BytesIO(df.to_csv().encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name="dormant_account.csv"
        )



































    # elif q == "get_report_filter":
    #     start_date = request.args.get('start_date')
    #     end_date = request.args.get('end_date')
    #     branch_name = request.args.get('branch_name')
    #     data = {'start_date': [start_date],'end_date': [end_date],'branch_name': [branch_name]}
    #     # my_dict = {start_date:'start_date', end_date:'end_date', branch_name:'branch_name'}
    #     df = pd.DataFrame([data])
    #     response_stream = io.BytesIO(df.to_csv(index=False).encode())
    #     return send_file(
    #         response_stream,
    #         mimetype="text/csv",
    #         download_name="report_branch_filter.csv"
    #     )