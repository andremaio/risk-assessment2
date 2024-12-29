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
    'dbname': os.getenv('DB_NAME', 'default_db_name'),
    'user': os.getenv('DB_USER', 'default_user'),
    'password': os.getenv('DB_PASSWORD', 'default_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))  # Porta padrão é 5432
}
SECRET_KEY = 'your-secret-key'
app = Flask(__name__)

def get_db_connection():
    """Conexão com o banco de dados PostgreSQL."""
    conn = psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        cursor_factory=RealDictCursor
    )
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        # Realiza a análise e salva no banco de dados
        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")
        nationality = data.get("nationality")
        previous_crimes = data.get("previous_crimes")
        sociological_factors = data.get("sociological_factors")
        psychological_factors = data.get("psychological_factors")
        cultural_factors = data.get("cultural_factors")
        individual_factors = data.get("individual_factors")
        criminal_factors = data.get("criminal_factors")

        # Aqui você pode realizar a análise com IA e salvar os resultados
        result = {
            "name": name,
            "risk_score": 50,  # Simulação
            "ai_analysis": "Simulação da análise de IA"
        }

        return jsonify(result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
