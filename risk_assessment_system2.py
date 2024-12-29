import os
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
import openai
import jwt
import datetime
from functools import wraps
from fpdf import FPDF

# Configurações
app = Flask(__name__)
openai.api_key = os.getenv('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') 
SECRET_KEY = os.getenv('SECRET_KEY', 'minha_chave_secreta')
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'default_db_name'),
    'user': os.getenv('DB_USER', 'default_user'),
    'password': os.getenv('DB_PASSWORD', 'default_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Autenticação de Token
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

# Função para análise de IA
def analyze_with_ai(data):
    prompt = f"""
    Baseado nos estudos de Montreal sobre fatores que influenciam o risco de reincidência criminal, analise:
    - Nome: {data['name']}
    - Idade: {data['age']}
    - Género: {data['gender']}
    - Crimes Anteriores: {data['previous_crimes']}
    - Fatores Sociológicos: {data.get('sociological_factors', 'Não fornecido')}
    - Fatores Psicológicos: {data.get('psychological_factors', 'Não fornecido')}
    - Fatores Culturais: {data.get('cultural_factors', 'Não fornecido')}
    - Fatores Individuais: {data.get('individual_factors', 'Não fornecido')}
    - Fatores Criminais: {data.get('criminal_factors', 'Não fornecido')}

    Gere uma pontuação de risco entre 0 e 100 e explique os fatores que contribuíram para essa pontuação.
    """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()

# Rotas
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/input", methods=["GET", "POST"])
def input():
    if request.method == "POST":
        data = {
            'name': request.form['name'],
            'age': request.form['age'],
            'gender': request.form['gender'],
            'previous_crimes': request.form['previous_crimes'],
            'sociological_factors': request.form.get('sociological_factors', ''),
            'psychological_factors': request.form.get('psychological_factors', ''),
            'cultural_factors': request.form.get('cultural_factors', ''),
            'individual_factors': request.form.get('individual_factors', ''),
            'criminal_factors': request.form.get('criminal_factors', '')
        }
        return redirect(url_for('analyze', **data))
    return render_template("input.html")

@app.route("/analyze", methods=["GET"])
def analyze():
    try:
        data = request.args.to_dict()
        analysis = analyze_with_ai(data)
        risk_score = 50  # Simula um cálculo mais complexo (ajustável)
        return render_template("result.html", name=data['name'], risk_score=risk_score, ai_analysis=analysis)
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}", "status": "error"})

@app.route("/generate_report", methods=["GET"])
def generate_report():
    return render_template("report.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
