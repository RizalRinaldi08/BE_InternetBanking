import db
from flask import Flask
import blueprints
from flask_jwt_extended import JWTManager

jwt = JWTManager()
def create_app():
    app = Flask(__name__)
    db.init(app)
    jwt.init_app(app)
    blueprints.init_app(app)
    return app

def main():
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    main()