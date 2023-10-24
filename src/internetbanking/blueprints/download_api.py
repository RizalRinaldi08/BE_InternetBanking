# from flask import Blueprint, request, jsonify, send_file
# from models import Branch, Account
# from db import session
# from flask_jwt_extended import jwt_required, get_jwt
# from .utils import get_history_account, get_report_filter, get_branch, get_dormant
# import pandas as pd
# import io
# import json

# download_api = Blueprint('download_api', __name__)

# @download_api.route('/download', methods=['GET'])
# def get_download():
#     q = request.args.get("q")
#     if q == "get_history_account":
#         account_number = request.args.get('account_number')
#         results = get_history_account(account_number)
#         df = pd.DataFrame(results)
#         response_stream = io.BytesIO(df.to_csv().encode())
#         return send_file(
#             response_stream,
#             mimetype="text/csv",
#             download_name="history_account.csv"
#         )
    
#     elif q == "get_branch":
#         results = get_branch()
#         df = pd.DataFrame(results)
#         response_stream = io.BytesIO(df.to_csv().encode())
#         return send_file(
#             response_stream,
#             mimetype="text/csv",
#             download_name="branch_report.csv"
#         )
#     elif q == "get_dormant":
#         results = get_dormant()
#         df = pd.DataFrame(results)
#         response_stream = io.BytesIO(df.to_csv().encode())
#         return send_file(
#             response_stream,
#             mimetype="text/csv",
#             download_name="dormant_account.csv"
#         )



































#     # elif q == "get_report_filter":
#     #     start_date = request.args.get('start_date')
#     #     end_date = request.args.get('end_date')
#     #     branch_name = request.args.get('branch_name')
#     #     data = {'start_date': [start_date],'end_date': [end_date],'branch_name': [branch_name]}
#     #     # my_dict = {start_date:'start_date', end_date:'end_date', branch_name:'branch_name'}
#     #     df = pd.DataFrame([data])
#     #     response_stream = io.BytesIO(df.to_csv(index=False).encode())
#     #     return send_file(
#     #         response_stream,
#     #         mimetype="text/csv",
#     #         download_name="report_branch_filter.csv"
#     #     )

from flask import Blueprint, request, jsonify, send_file
from models import Branch, Account
from db import session
from flask_jwt_extended import jwt_required, get_jwt
from .utils import get_history_account, get_report_filter, get_branch, get_dormant
import pandas as pd
import io
import xlsxwriter

download_api = Blueprint('download_api', __name__)

@download_api.route('/download', methods=['GET'])
def get_download():
    q = request.args.get("q")
    if q == "get_history_account":
        account_number = request.args.get('account_number')
        results = get_history_account(account_number)
        # print(results)
        # final_result = []
        # for r in results['transaction']:
        #     items = []
        #     for key,value in r.items():
        #         # if key == "transaction_date":
        #         #     items
        #         items.append(value)
        #     final_result.append(items)
        # df = pd.DataFrame(columns=["Balance","Transaction Date", "Credit", "Debit", "Notes"])
        df = pd.DataFrame.from_dict(results['transaction'], orient="columns")
        df.columns = ["Balance","Transaction Date", "Credit", "Debit", "Notes"]

        # Buat Excel Writer menggunakan Pandas
        excel_stream = io.BytesIO()
        with pd.ExcelWriter(excel_stream, engine='xlsxwriter') as excel_writer:
            df.to_excel(excel_writer, sheet_name='History Account', index=False)

        excel_stream.seek(0)

        return send_file(
            excel_stream,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="history_account.xlsx"
        )
    elif q == "get_branch":
        results = get_branch()
        # final_result =[]
        # for r in results['branch_report']:
        #     items =[]

        #     for key,value in r.items():
        #         items.append(value)
        #     final_result.append(items)
        
        # # Membuat DataFrame dari hasil query
        # df = pd.DataFrame(final_result, columns=["Branch Name", "Branch Code", "City", "Address", "Number of Accounts", "Number of Users", "Total Balance"])
        
        df = pd.DataFrame.from_dict(results["branch_report"], orient="columns")
        df.columns = ["Branch Name", "Branch Code", "City", "Address", "Number of Accounts", "Number of Users", "Total Balance"]
        
        excel_stream = io.BytesIO()
        with pd.ExcelWriter(excel_stream, engine='xlsxwriter') as excel_writer:
            df.to_excel(excel_writer, sheet_name='Branch Report', index=False)

        excel_stream.seek(0)

        return send_file(
            excel_stream,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="branch_report.xlsx"
    )

    
    elif q == "get_dormant":
        results = get_dormant()
        final_result = []
        for r in results:
            items=[]
            for key,value in r.items():
                items.append(value)
            final_result.append(items)
        df = pd.DataFrame(final_result, columns=["Account Name", "Balance", "Branch Name", "Dormant Period(Days)", "Account Active"])

        excel_stream = io.BytesIO()
        with pd.ExcelWriter(excel_stream, engine='xlsxwriter') as excel_writer:
            df.to_excel(excel_writer, sheet_name='Dormant Account', index=False)

        excel_stream.seek(0)

        return send_file(
            excel_stream,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="dormant_account.xlsx"
        )
    # q = request.args.get("q")
    # if q == "get_history_account":
    #     account_number = request.args.get('account_number')
    #     results = get_history_account(account_number)
    #     df = pd.DataFrame(results)

    #     # Buat Excel Writer menggunakan Pandas
    #     excel_writer = pd.ExcelWriter('history_account.xlsx', engine='xlsxwriter')
    #     df.to_excel(excel_writer, sheet_name='History Account', index=False)

    #     excel_writer.save()
    #     excel_stream = io.BytesIO()
    #     excel_writer.save(excel_stream)
    #     excel_stream.seek(0)

    #     return send_file(
    #         excel_stream,
    #         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #         as_attachment=True,
    #         download_name="history_account.xlsx"
    #     )
    
    # elif q == "get_branch":
    #     results = get_branch()
    #     df = pd.DataFrame(results)

    #     # Buat Excel Writer menggunakan Pandas
    #     excel_writer = pd.ExcelWriter('branch_report.xlsx', engine='xlsxwriter')
    #     df.to_excel(excel_writer, sheet_name='Branch Report', index=False)

    #     excel_writer.save()
    #     excel_stream = io.BytesIO()
    #     excel_writer.save(excel_stream)
    #     excel_stream.seek(0)

    #     return send_file(
    #         excel_stream,
    #         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #         as_attachment=True,
    #         download_name="branch_report.xlsx"
    #     )
    
    # elif q == "get_dormant":
    #     results = get_dormant()
    #     df = pd.DataFrame(results)

    #     # Buat Excel Writer menggunakan Pandas
    #     excel_writer = pd.ExcelWriter('dormant_account.xlsx', engine='xlsxwriter')
    #     df.to_excel(excel_writer, sheet_name='Dormant Account', index=False)

    #     excel_writer.save()
    #     excel_stream = io.BytesIO()
    #     excel_writer.save(excel_stream)
    #     excel_stream.seek(0)

    #     return send_file(
    #         excel_stream,
    #         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #         as_attachment=True,
    #         download_name="dormant_account.xlsx"
    #     )
