import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Carrega as variáveis do arquivo .env
load_dotenv()

class DatabaseConfig:
    # Carrega a URI completa do .env para uso com SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_connection():
        try:
            # Estabelece a conexão com o banco de dados MySQL usando variáveis individuais
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_DATABASE'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            return connection
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    @staticmethod
    def test_db_connection():
        connection = DatabaseConfig.get_connection()
        if connection:
            print("Conexão com o banco de dados bem-sucedida.")
            connection.close()  # Fechar a conexão após o teste
        else:
            print("Falha ao conectar com o banco de dados.")