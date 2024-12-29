import os
import psycopg2
from flask import Flask, request, jsonify, render_template
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

# Função para gerar o relatório PDF
def generate_pdf(data, risk_score, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, "Relatório de Risco de Reincidência Criminal", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Nome: {data['name']}", ln=True)
    pdf.cell(200, 10, f"Idade: {data['age']}", ln=True)
    pdf.cell(200, 10, f"Género: {data['gender']}", ln=True)
    pdf.cell(200, 10, f"Risco Calculado: {risk_score}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Análise detalhada:\n{analysis}")
    pdf_file = f"relatorio_{data['name']}.pdf"
    pdf.output(pdf_file)
    return pdf_file

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

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
@token_required
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "Dados não fornecidos.", "status": "error"})
        
        analysis = analyze_with_ai(data)
        risk_score = 50  # Simula um cálculo mais complexo (ajustável)
        
        # Gerar PDF
        pdf_file = generate_pdf(data, risk_score, analysis)
        
        return jsonify({
            "name": data['name'],
            "risk_score": risk_score,
            "ai_analysis": analysis,
            "pdf_report": pdf_file,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}", "status": "error"})

if __name__ == "__main__":
    app.run(debug=True)
