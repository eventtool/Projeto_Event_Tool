from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from models import Usuario, Evento, Certificado, Presenca
import config
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = config.DatabaseConfig.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS

# Testando a conexão com o banco
config.DatabaseConfig.test_db_connection()


db = SQLAlchemy(app)


# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)