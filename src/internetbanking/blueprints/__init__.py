from .user_api import user_api
from .account_api import account_api
from .branch_api import branch_api
from .transaction_api import transaction_api
from .reporting_api import report_api
from .download_api import download_api
# from .auth import login_api
from flask import Flask
from .auth import auth


def init_app(app: Flask):
    app.register_blueprint(user_api, url_prefix='/api')
    app.register_blueprint(account_api, url_prefix='/api')
    app.register_blueprint(branch_api, url_prefix='/api')
    app.register_blueprint(transaction_api, url_prefix='/api')
    app.register_blueprint(report_api, url_prefix='/api')
    # app.register_blueprint(login_api, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/api')
    app.register_blueprint(download_api, url_prefix='/api')