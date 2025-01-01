import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from psycopg2.extras import RealDictCursor
import openai
from fpdf import FPDF

# Configurações
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Conexão com o banco de dados
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        cursor_factory=RealDictCursor
    )

# Função para gerar relatório PDF
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
    prompt = f"""
    Baseado nos fatores fornecidos, analise o risco de reincidência criminal:
    - Nome: {data['name']}
    - Idade: {data['age']}
    - Gênero: {data['gender']}
    - Crimes Anteriores: {data.get('previous_crimes', 'Não informado')}
    - Fatores Sociológicos: {data.get('sociological_factors', 'Não informado')}
    - Fatores Psicológicos: {data.get('psychological_factors', 'Não informado')}
    Gere uma pontuação de risco e justifique.
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
    try:
        data = request.json
        if not data:
            return jsonify({"message": "Nenhum dado fornecido"}), 400
        analysis = analyze_with_ai(data)
        risk_score = 50  # Exemplo fixo
        pdf_file = generate_pdf(data, risk_score, analysis)
        return jsonify({
            "name": data['name'],
            "risk_score": risk_score,
            "ai_analysis": analysis,
            "pdf_report": pdf_file
        })
    except Exception as e:
        return jsonify({"message": f"Erro: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
