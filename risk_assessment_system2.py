import os
from flask import Flask, request, jsonify, render_template, send_file
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from fpdf import FPDF

app = Flask(__name__)

# Configurações
openai.api_key = os.getenv('OPENAI_API_KEY', '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')
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'default_db_name'),
    'user': os.getenv('DB_USER', 'default_user'),
    'password': os.getenv('DB_PASSWORD', 'default_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Função para conexão com o banco de dados
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        cursor_factory=RealDictCursor
    )

# Função para gerar relatório em PDF
def generate_pdf(data, risk_score, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, "Relatório de Risco de Reincidência Criminal", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Nome: {data['name']}", ln=True)
    pdf.cell(200, 10, f"Idade: {data['age']}", ln=True)
    pdf.cell(200, 10, f"Gênero: {data['gender']}", ln=True)
    pdf.cell(200, 10, f"Pontuação de Risco: {risk_score}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Análise detalhada:\n{analysis}")
    pdf_file = f"relatorio_{data['name']}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Função para análise com OpenAI
def analyze_with_ai(data):
    prompt = f"""
    Baseado nos fatores fornecidos, analise:
    - Nome: {data['name']}
    - Idade: {data['age']}
    - Gênero: {data['gender']}
    - Crimes anteriores: {data['previous_crimes']}
    - Outros fatores: {data.get('other_factors', 'Não fornecidos')}
    Gere uma pontuação de risco entre 0 e 100 e justifique.
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
def analyze():
    data = request.form
    if not data:
        return jsonify({"message": "Dados não fornecidos."})
    analysis = analyze_with_ai(data)
    risk_score = 50  # Exemplo estático
    pdf_file = generate_pdf(data, risk_score, analysis)
    return send_file(pdf_file, as_attachment=True)

@app.route("/report", methods=["GET"])
def report():
    return render_template("report.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))