from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.category_routes import category_bp
from routes.task_routes import task_bp
from utils.cleanup import permanently_delete_users

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config.from_object(Config)

# Extensions
CORS(app)
JWTManager(app)
db.init_app(app)

# Register routes
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(category_bp, url_prefix="/api/categories")
app.register_blueprint(task_bp, url_prefix="/api")

# Create tables
with app.app_context():
    db.create_all()

    # chạy khi server start (backup)
    permanently_delete_users()

# =====================
# Scheduler chạy mỗi ngày
# =====================
scheduler = BackgroundScheduler()

def cleanup_job():
    with app.app_context():
        permanently_delete_users()

# chạy mỗi 24 giờ
scheduler.add_job(cleanup_job, "interval", hours=24)

scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)