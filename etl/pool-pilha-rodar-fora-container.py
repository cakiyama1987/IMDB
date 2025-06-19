# etl/pool-pilha-rodar-fora-container.py (VERSÃO FINAL COMPLETA)
import time
import redis
import psycopg2
import json

# --- CONFIGURAÇÕES ---
REDIS_HOST = 'redis' # Usa o nome do serviço do docker-compose
REDIS_PORT = 6379
PG_HOST = 'postgres_db'
PG_PORT = 5432
PG_DB = 'postgres'
PG_USER = 'postgres'
PG_PASSWORD = '123456'

# --- FUNÇÕES DE BANCO DE DADOS ---

def create_tables(conn):
    print('criando tabelas')    
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY,
                question_text TEXT,
                alternativa_a TEXT,
                alternativa_b TEXT,
                alternativa_c TEXT,
                alternativa_d TEXT,
                alternativa_correta VARCHAR(15),
                dificuldade VARCHAR(50),
                assunto VARCHAR(255)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id SERIAL PRIMARY KEY,
                question_id INTEGER REFERENCES questions(question_id),
                alternativa_escolhida VARCHAR(15),
                datahora TIMESTAMP,
                usuario VARCHAR(255),
                nro_tentativa INTEGER
            );
        """)
    conn.commit()
    print("Tabelas 'questions' e 'answers' verificadas/criadas com sucesso.")

def insert_question_into_postgres(conn, question_data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO questions (question_id, question_text, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_correta, dificuldade, assunto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (question_id) DO NOTHING;
        """, (
            question_data.get('question_id'), question_data.get('question_text'),
            question_data.get('alternativa_a'), question_data.get('alternativa_b'),
            question_data.get('alternativa_c'), question_data.get('alternativa_d'),
            question_data.get('alternativa_correta'), question_data.get('dificuldade'),
            question_data.get('assunto')
        ))
    conn.commit()

def insert_answer_into_postgres(conn, answer_data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO answers (question_id, alternativa_escolhida, datahora, usuario, nro_tentativa)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            answer_data.get('question_id'), answer_data.get('alternativa_escolhida'),
            answer_data.get('datahora'), answer_data.get('usuario'),
            answer_data.get('nro_tentativa')
        ))
    conn.commit()

# --- FUNÇÃO PRINCIPAL ---

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    pg_conn = None
    retries = 5
    while retries > 0:
        try:
            print("Tentando se conectar ao Postgres...")
            pg_conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD)
            print("Conexão com o Postgres bem-sucedida!")
            break
        except psycopg2.OperationalError as e:
            print(f"Falha ao conectar, tentando novamente em 5 segundos...")
            retries -= 1
            time.sleep(5)
    
    if pg_conn is None:
        print("Não foi possível conectar ao Postgres. Abortando.")
        exit(1)

    create_tables(pg_conn)

    # Processar PERGUNTAS
    question_keys = r.keys('question:*')
    print(f"\nEncontradas {len(question_keys)} chaves de PERGUNTAS para processar...")
    for key in question_keys:
        question_data_map = r.hgetall(key)
        if question_data_map:
            question_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in question_data_map.items()}
            try:
                question_id = int(key.decode('utf-8').split(':')[-1])
                question_data['question_id'] = question_id
                print(f"Carregando Pergunta ID: {question_id}")
                insert_question_into_postgres(pg_conn, question_data)
            except (IndexError, ValueError):
                print(f"Não foi possível extrair um ID válido da chave: {key.decode('utf-8')}")

    # Processar RESPOSTAS
    answer_keys = r.keys('answer:*')
    print(f"\nEncontradas {len(answer_keys)} chaves de RESPOSTAS para processar...")
    for key in answer_keys:
        answer_data_map = r.hgetall(key)
        if answer_data_map:
            answer_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in answer_data_map.items()}
            try:
                key_parts = key.decode('utf-8').split(':')
                answer_data['usuario'] = key_parts[1]
                answer_data['question_id'] = int(key_parts[2])
                answer_data['nro_tentativa'] = int(key_parts[3])
                print(f"Carregando Resposta do Usuário: {answer_data['usuario']} para a Questão ID: {answer_data['question_id']}")
                insert_answer_into_postgres(pg_conn, answer_data)
            except (IndexError, ValueError):
                print(f"Não foi possível extrair dados válidos da chave: {key.decode('utf-8')}")
    
    pg_conn.close()
    print("\nTransferência ETL concluída e conexão com Postgres fechada.")

if __name__ == "__main__":
    main()