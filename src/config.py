import psycopg2

try:
    # Conectando ao banco de dados usando "with" para garantir o fechamento
    with psycopg2.connect(
        host="dpg-cvfel80fnakc739nr4v0-a.virginia-postgres.render.com",
        port="5432",
        database="postgres",
        user="projetc_event_tool_user",
        password="6paqgMFFDNuBAeQ75s2fBRbbcepCJEaN"
    ) as conn:
        
        # Criando um cursor para executar comandos SQL
        with conn.cursor() as cursor:
            # Verificando se a conexão foi bem-sucedida
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            print(f"Versão do PostgreSQL: {result[0]}")

            # Consultando os bancos de dados disponíveis
            cursor.execute("SELECT datname FROM pg_database;")
            databases = cursor.fetchall()
            print("Bancos de dados disponíveis:")
            for db in databases:
                print(f" - {db[0]}")

except psycopg2.OperationalError as e:
    print(f"Erro operacional: {e}")

except psycopg2.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e.pgcode} - {e.pgerror}")

except Exception as e:
    print(f"Erro inesperado: {e}")