import time
import redis
import psycopg2

# Configurações de conexão
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_LIST = 'minha_pilha'

PG_HOST = 'localhost'
PG_PORT = 5432
PG_DB = 'dw'
PG_USER = 'user'
PG_PASSWORD = 'senhaForte2025'
PG_TABLE = 'redis_history'  # Atualizado para a nova tabela

def create_table_if_not_exists(conn):
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {PG_TABLE} (
                id SERIAL PRIMARY KEY,
                valor VARCHAR,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()

def insert_into_postgres(conn, value):
    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO {PG_TABLE} (valor) VALUES (%s);", (value,))
    conn.commit()

def main():
    # Conexão com Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # Conexão com Postgres
    pg_conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

    create_table_if_not_exists(pg_conn)

    print("Iniciando loop de transferência da pilha para o Postgres...")
    while True:
        value = r.lpop(REDIS_LIST)
        if value:
            print(f"Inserindo no Postgres: {value}")
            insert_into_postgres(pg_conn, value)
        
        time.sleep(5)  # Aguarda 30 segundos entre cada iteração do loop

if __name__ == "__main__":
    main()