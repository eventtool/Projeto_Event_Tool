from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import os
# from dotenv import load_dotenv

# Carrega variáveis de ambiente
# load_dotenv()

app = Flask(__name__)
# Rota para a página de cadastro
@app.route('/cadastrar')
def cadastrar():
    return render_template('cadastro.html')

# Configuração do banco de dados
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )
    return conn



if __name__ == '__main__':
    app.run(debug=True)