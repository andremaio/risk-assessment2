import os
import sqlite3
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
    'port': os.getenv('DB_PORT', 5432)  # Porta padrão é 5432
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

def initialize_db():
    """Cria a tabela se ela não existir."""
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

# Análise com IA
def analyze_with_ai(data):
    """Realiza análise com OpenAI."""
    try:
        prompt = f"""
        Analise o risco de reincidência criminal com base nos seguintes dados:
        - Nome: {data['name']}
        - Idade: {data['age']}
        - Género: {data['gender']}
        - Nacionalidade: {data['nationality']}
        - Crimes Anteriores: {data['previous_crimes']}
        - Fatores Sociológicos: {data.get('sociological_factors', 'Não fornecido')}
        - Fatores Psicológicos: {data.get('psychological_factors', 'Não fornecido')}
        - Fatores Culturais: {data.get('cultural_factors', 'Não fornecido')}
        - Fatores Individuais: {data.get('individual_factors', 'Não fornecido')}
        - Fatores Criminais: {data.get('criminal_factors', 'Não fornecido')}

        Use uma abordagem interdisciplinar para fornecer uma análise detalhada e uma pontuação de risco entre 0 e 100.
        """

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        analysis = response.choices[0].text.strip()
        return analysis
    except Exception as e:
        return f"Erro ao utilizar a IA: {str(e)}"

# Rotas
@app.route("/login", methods=["POST"])
def login():
    auth = request.json
    if auth and auth['username'] == 'admin' and auth['password'] == 'admin':
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Credenciais inválidas!", "status": "error"}), 401

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

        name = data.get("name", "Não informado")
        age = data.get("age", 0)
        gender = data.get("gender", "Não informado")
        nationality = data.get("nationality", "Não informado")
        previous_crimes = data.get("previous_crimes", 0)
        sociological_factors = data.get("sociological_factors", "Não fornecido")
        psychological_factors = data.get("psychological_factors", "Não fornecido")
        cultural_factors = data.get("cultural_factors", "Não fornecido")
        individual_factors = data.get("individual_factors", "Não fornecido")
        criminal_factors = data.get("criminal_factors", "Não fornecido")

        formatted_data = {
            "name": name,
            "age": int(age),
            "gender": gender,
            "nationality": nationality,
            "previous_crimes": int(previous_crimes),
            "sociological_factors": sociological_factors,
            "psychological_factors": psychological_factors,
            "cultural_factors": cultural_factors,
            "individual_factors": individual_factors,
            "criminal_factors": criminal_factors
        }

        # Análise com IA
        ai_analysis = analyze_with_ai(formatted_data)
        risk_score = 0  # Exemplo: Este pode ser substituído por uma integração mais complexa.

        # Salvar no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO individuals (
                name, age, gender, nationality, previous_crimes,
                sociological_factors, psychological_factors, cultural_factors,
                individual_factors, criminal_factors, risk_score, ai_analysis
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name, age, gender, nationality, previous_crimes,
                sociological_factors, psychological_factors, cultural_factors,
                individual_factors, criminal_factors, risk_score, ai_analysis
            )
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "name": name,
            "risk_score": risk_score,
            "ai_analysis": ai_analysis,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {str(e)}", "status": "error"})

if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
