import os
from flask import Flask 
from flask_jwt_extended import JWTManager
from dbms.db import db
from datetime import timedelta
from models.expense import Expense
from models.income import Income
from models.category import Category
from models.loan import Loan
from models.borrow import Borrow
from models.subscribe import Subscription
from routes.auth import auth_bp
from routes.otp import otp_bp
from routes.income import income_bp
from routes.category import category_bp
from models.user import User
from routes.forgot import forgot_bp
from routes.expense import expense_bp
from routes.loan import loan_bp
from flask_migrate import Migrate
from routes.dashboard import dashboard_bp
from routes.ai import ai_bp
from routes.borrow import borrow_bp
from routes.subscription import subscribe_bp
from block import BLOCKLIST
from dotenv import load_dotenv

load_dotenv()
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =os.getenv("DATABASE_URL") 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"]=os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
db.init_app(app)
migrate=Migrate(app,db)
jwt=JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header,jwt_payload):
    return jwt_payload.get('jti') in BLOCKLIST

@jwt.revoked_token_loader
def revoked_token_loader(jwt_header,jwt_payload):
      return ({
        "description":"user has been logged out",
        "error":"token-revoked"
      },401)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(otp_bp,url_prefix="/otp")
app.register_blueprint(forgot_bp,url_prefix='/')
app.register_blueprint(expense_bp)
app.register_blueprint(income_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(category_bp)
app.register_blueprint(loan_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(borrow_bp)
app.register_blueprint(subscribe_bp)
@app.route("/")
def home():
    return {"message":"Api Running Successful"}

# with app.app_context(): #with automatically handles and it uses 2 special method start and cleanup
#     db.create_all() 
    print("Tables created successfully")
if __name__=="__main__":
    app.run(debug=True)








