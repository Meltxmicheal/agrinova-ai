from flask import Flask, render_template
from config.config import Config
from app.extensions import db, bcrypt, jwt, migrate
from app.models.user import User
from app.models.farm import Farm
from app.models.weather import WeatherHistory
from app.models.prediction import Prediction
from app.farm.routes import farm_bp

def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static"
    )

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS for dev (restrict origins in production)
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ----------------------------
    # Translation Support (i18n)
    # ----------------------------
    import json
    import os
    from flask import request

    # Load translations
    translations_path = os.path.join(os.path.dirname(__file__), 'translations.json')
    try:
        with open(translations_path, 'r', encoding='utf-8') as f:
            app.translations = json.load(f)
    except FileNotFoundError:
        app.translations = {}

    def translate_filter(text):
        """Custom Jinja2 filter for translating text based on cookie."""
        lang = request.cookies.get('lang', 'en')
        if lang == 'ta':
            # Handle nested objects like Soil Types if needed, but for simple strings:
            if text in app.translations:
                return app.translations[text]
            # Check if it's inside a nested category like "Soil Types"
            for category, items in app.translations.items():
                if isinstance(items, dict) and text in items:
                    return items[text]
        return text

    app.jinja_env.filters['t'] = translate_filter

    @app.context_processor
    def inject_lang():
        return dict(current_lang=request.cookies.get('lang', 'en'))

    # ----------------------------
    # Register Blueprints
    # ----------------------------
    from app.auth.routes import auth_bp
    from app.weather.routes import weather_bp
    from app.ai.routes import ai_bp
    from app.crop.routes import crop_bp
    from app.disease.routes import disease_bp
    from app.prediction.routes import prediction_bp
    from app.dashboard.routes import dashboard_bp
    from app.reports.routes import reports_bp
    from app.assistant.routes import assistant_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(farm_bp, url_prefix="/api/farms")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(crop_bp, url_prefix="/api/crop")
    app.register_blueprint(disease_bp, url_prefix="/api/disease")
    app.register_blueprint(prediction_bp, url_prefix="/api/prediction")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(assistant_bp, url_prefix="/api/assistant")

    # ----------------------------
    # Frontend Routes
    # ----------------------------

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.route("/farms")
    def farms_page():
        return render_template("farms.html")

    @app.route("/weather")
    def weather_page():
        return render_template("weather.html")

    @app.route("/prediction")
    def prediction_page():
        return render_template("prediction.html")

    @app.route("/reports")
    def reports_page():
        return render_template("reports.html")

    @app.route("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.route("/settings")
    def settings_page():
        return render_template("settings.html")

    @app.route("/forgot-password")
    def forgot_password_page():
        return render_template("forgot_password.html")

    @app.route("/reset-password")
    def reset_password_page():
        return render_template("reset_password.html")

    return app