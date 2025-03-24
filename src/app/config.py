import psycopg2
from psycopg2 import OperationalError

class DatabaseConfig:
    SQLALCHEMY_DATABASE_URI = (
        'postgresql://projetc_event_tool_user:6paqgMFFDNuBAeQ75s2fBRbbcepCJEaN@dpg-cvfel80fnakc739nr4v0-a.virginia-postgres.render.com:5432/postgres'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Para desabilitar a notificação de modificações

    @staticmethod
    def get_connection():
        try:
            # Estabelece a conexão com o banco de dados PostgreSQL
            connection = psycopg2.connect(
                host="dpg-cvfel80fnakc739nr4v0-a.virginia-postgres.render.com",
                database="postgres",
                user="projetc_event_tool_user",
                password="6paqgMFFDNuBAeQ75s2fBRbbcepCJEaN",
                port="5432"
            )
            return connection
        except OperationalError as e:
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
