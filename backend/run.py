"""
AgriNova AI — Application Entry Point
Run: python run.py
Gunicorn: gunicorn --bind 0.0.0.0:5000 run:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
