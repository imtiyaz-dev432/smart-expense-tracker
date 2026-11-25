import os

from dotenv import load_dotenv
from flask import Flask, abort, current_app, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from redis.exceptions import RedisError

from config import Config, TestingConfig
from dbms.db import db
from routes.ai import ai_bp
from routes.auth import auth_bp
from routes.borrow import borrow_bp
from routes.dashboard import dashboard_bp
from routes.expense import expense_bp
from routes.forgot import forgot_bp
from routes.income import income_bp
from routes.loan import loan_bp
from routes.otp import otp_bp
from routes.subscription import subscribe_bp
from utils.ce_lery import make_celery
from utils.extensions import redis_client
from utils.rate import limiter

load_dotenv()
def create_app(config_name=None):
      app=Flask(__name__)
      APP_ENV=os.getenv("APP_ENV","development")
      @app.after_request
      def add_security_headers(response):
          response.headers["X-Content-Type-Options"] = "nosniff"
          response.headers["X-Frame-Options"] = "DENY"
          response.headers["Referrer-Policy"] = ("strict-origin-when-cross-origin")
          if APP_ENV=="production" and request.is_secure:
            response.headers["Strict-Transport-Security"] = (
            "max-age=31536000")
          return response

      if config_name=="testing":
        app.config.from_object(TestingConfig)
      else:
        app.config.from_object(Config)
      allowed_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
      ]
      # cors is browser only protection
      CORS(app,
        origins=allowed_origins,  #Benefit: * ka matlab tha —
        # duniya ki koi bhi website tera API call kar sakti hai. Ab sirf tera
        #  frontend (localhost:3000, 5173) call kar sakta hai.
        allow_headers=["Content-Type", "Authorization"], #Unknown custom headers
        supports_credentials=False,  #Browser ko bolta hai "cookies automatically
        #mat bhej"[reduce csrf attacks]
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
      db.init_app(app)
      Migrate(app,db)
      limiter.init_app(app)
      jwt=JWTManager(app)

      @jwt.token_in_blocklist_loader
      def check_if_token_in_blocklist(jwt_header,jwt_payload):
          jti=jwt_payload['jti']
          try:
            return redis_client.exists(f"blacklist:{jti}") #without try there is a avalablity risk
          except RedisError:
                      current_app.logger.exception("Redis unavailable during JWT blocklist check")
                      abort(503,
            description="Authentication service temporarily unavailable")

      @jwt.revoked_token_loader
      def revoked_token_loader(jwt_header,jwt_payload):
            return ({
        "description":"user has been logged out",
        "error":"token-revoked"
      },401)
      app.register_blueprint(auth_bp)
      app.register_blueprint(otp_bp)
      app.register_blueprint(forgot_bp)
      app.register_blueprint(expense_bp)
      app.register_blueprint(income_bp)
      app.register_blueprint(dashboard_bp)
      app.register_blueprint(loan_bp)
      app.register_blueprint(ai_bp)
      app.register_blueprint(borrow_bp)
      app.register_blueprint(subscribe_bp)
      @app.route("/")
      def home():
         return {"message":"Api Running Successful"}

      return app
app=create_app()

celery=make_celery(app)
if __name__=="__main__":
    app.run(debug=False)
