import os
from flask import Flask, request, jsonify, render_template
import openai
import jwt
import datetime
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurações
openai.api_key = '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'
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432))
}
SECRET_KEY = 'Amaio261@'
app = Flask(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({"message": "Token é necessário!", "status": "error"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return jsonify({"message": "Token inválido!", "status": "error"}), 403
        return f(*args, **kwargs)
    return decorated

# Banco de Dados
def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        cursor_factory=RealDictCursor
    )
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS individuals (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            nationality TEXT NOT NULL,
            previous_crimes INTEGER NOT NULL,
            sociological_factors TEXT,
            psychological_factors TEXT,
            cultural_factors TEXT,
            individual_factors TEXT,
            criminal_factors TEXT,
            risk_score REAL,
            ai_analysis TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    initialize_db()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
