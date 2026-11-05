import os
from flask import Flask ,current_app
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
from dotenv import load_dotenv
from flask_cors import CORS
from utils.otp import send_otp_mail
from utils.rate import limiter
from utils.extensions import redis_client
from utils.ce_lery import make_celery
from config import Config
load_dotenv()
app=Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
migrate=Migrate(app,db)
limiter.init_app(app)      
jwt=JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header,jwt_payload):
    jti=jwt_payload['jti']
    try:
      return redis_client.exists(f"blacklist:{jti}") #without try there is a avalablity risk
    except Exception:
         current_app.logger.exception("Blocklist check failed jti=%s", jti)
         return False
         
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
with app.app_context():
    db.create_all()
@app.route("/")
def home():
    return {"message":"Api Running Successful"}

celery=make_celery(app)    
if __name__=="__main__":
    app.run(debug=False)








