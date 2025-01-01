import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from psycopg2.extras import RealDictCursor
import openai
from fpdf import FPDF

# Configurações
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
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
    pdf.cell(200, 10, f"Gênero: {data['gender']}", ln=True)
    pdf.cell(200, 10, f"Risco Calculado: {risk_score}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Análise detalhada:\n{analysis}")
    pdf_file = f"relatorio_{data['name']}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Função para análise de IA
def analyze_with_ai(data):
    previous_crimes = data.get('previous_crimes', 'Não informado')
    sociological_factors = data.get('sociological_factors', 'Não fornecido')
    psychological_factors = data.get('psychological_factors', 'Não fornecido')
    cultural_factors = data.get('cultural_factors', 'Não fornecido')
    individual_factors = data.get('individual_factors', 'Não fornecido')

    messages = [
        {"role": "system", "content": "Você é um especialista em análise de risco criminal."},
        {"role": "user", "content": f"""
        Baseado nos fatores fornecidos, analise o risco de reincidência criminal:
        - Nome: {data['name']}
        - Idade: {data['age']}
        - Gênero: {data['gender']}
        - Crimes Anteriores: {previous_crimes}
        - Fatores Sociológicos: {sociological_factors}
        - Fatores Psicológicos: {psychological_factors}
        - Fatores Culturais: {cultural_factors}
        - Fatores Individuais: {individual_factors}

        Gere uma pontuação de risco entre 0 e 100 e justifique os fatores que contribuíram para essa pontuação.
        """}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

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

        # Análise com IA
        analysis = analyze_with_ai(data)
        risk_score = 50  # Exemplo de pontuação fixa (ajustável conforme necessário)

        # Gerar PDF
        pdf_file = generate_pdf(data, risk_score, analysis)

        return jsonify({
            "name": data['name'],
            "risk_score": risk_score,
            "ai_analysis": analysis,
            "pdf_report": pdf_file
        })
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
