import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from psycopg2.extras import RealDictCursor
from transformers import pipeline

# Configurações
app = Flask(__name__)
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'default_db_name'),
    'user': os.getenv('DB_USER', 'default_user'),
    'password': os.getenv('DB_PASSWORD', 'default_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Conexão com o banco de dados
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        cursor_factory=RealDictCursor
    )

# Função para análise de IA usando Hugging Face
def analyze_with_hugging_face(data):
    model = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
    input_text = f"""
    Nome: {data['name']}
    Idade: {data['age']}
    Gênero: {data['gender']}
    Crimes Anteriores: {data.get('previous_crimes', 'Não informado')}
    """
    result = model(input_text[:512])  # Limitar a 512 caracteres
    return result

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Carregar dados da requisição JSON
        data = request.get_json()
        if not data:
            return jsonify({"message": "Nenhum dado fornecido."}), 400

        # Análise com Hugging Face
        analysis = analyze_with_hugging_face(data)

        # Gerar uma resposta fictícia de risco (por enquanto)
        risk_score = 50  # Ajuste conforme necessário

        return jsonify({
            "name": data['name'],
            "risk_score": risk_score,
            "ai_analysis": analysis,
        })
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)