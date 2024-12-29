import os
import psycopg2
from flask import Flask, request, jsonify, render_template, send_file
from psycopg2.extras import RealDictCursor
import openai
from fpdf import FPDF

# Configurações
app = Flask(__name__)
openai.api_key = os.getenv('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')
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        cursor_factory=RealDictCursor
    )

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

def analyze_with_ai(data):
    prompt = f"""
    Avalie o risco de reincidência criminal para:
    - Nome: {data['name']}
    - Idade: {data['age']}
    - Gênero: {data['gender']}
    - Crimes Anteriores: {data['previous_crimes']}
    Outros fatores: {data.get('sociological_factors', 'Não fornecido')}
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Erro com a API OpenAI: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        analysis = analyze_with_ai(data)
        risk_score = 50  # Simula um cálculo mais complexo
        pdf_file = generate_pdf(data, risk_score, analysis)
        return jsonify({
            "name": data['name'],
            "risk_score": risk_score,
            "ai_analysis": analysis,
            "pdf_report": pdf_file
        })
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)