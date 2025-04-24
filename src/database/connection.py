import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# Carrega as variáveis de ambiente
load_dotenv()

def get_admin_connection():
    """Estabelece uma conexão administrativa com o PostgreSQL."""
    try:
        connection = psycopg2.connect(
            dbname='postgres',
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        connection.autocommit = True
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def get_connection():
    """Estabelece uma conexão com o banco de dados da aplicação."""
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'gim_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise e

@contextmanager
def get_db_connection():
    """Context manager para conexão com o banco de dados."""
    conn = None
    try:
        conn = get_connection()
        yield conn
    finally:
        if conn is not None:
            conn.close()

def close_connection(connection):
    """Fecha a conexão com o banco de dados."""
    if connection:
        connection.close()

def init_database():
    """Inicializa o banco de dados e cria todas as tabelas."""
    # Conecta ao PostgreSQL como admin
    admin_conn = get_admin_connection()
    if not admin_conn:
        return False

    try:
        # Cria o banco de dados se não existir
        with admin_conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'gim_db'")
            if not cursor.fetchone():
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier('gim_db')
                ))
        
        # Fecha conexão administrativa
        close_connection(admin_conn)

        # Conecta ao banco da aplicação
        conn = get_connection()
        if not conn:
            return False

        # Cria as tabelas
        with conn.cursor() as cursor:
            cursor.execute("""
                DROP TABLE IF EXISTS turma_instrutor_aluno CASCADE;
                DROP TABLE IF EXISTS turma CASCADE;
                DROP TABLE IF EXISTS contato_instrutor CASCADE;
                DROP TABLE IF EXISTS instrutor CASCADE;
                DROP TABLE IF EXISTS bioimpedancia CASCADE;
                DROP TABLE IF EXISTS contato_aluno CASCADE;
                DROP TABLE IF EXISTS aluno CASCADE;
                DROP TABLE IF EXISTS plano CASCADE;

                -- Tabela de planos
                CREATE TABLE IF NOT EXISTS plano (
                    codigo_plano SERIAL PRIMARY KEY,
                    nome_plano VARCHAR(45) NOT NULL,
                    preco NUMERIC(10,2) NOT NULL,
                    descricao VARCHAR(180)
                );

                -- Tabela de alunos
                CREATE TABLE IF NOT EXISTS aluno (
                    matricula SERIAL PRIMARY KEY,
                    cpf VARCHAR(11) UNIQUE NOT NULL,
                    nome VARCHAR(45) NOT NULL,
                    sexo CHAR(1) CHECK (sexo IN ('M', 'F')),
                    data_nascimento DATE NOT NULL,
                    data_matricula DATE NOT NULL,
                    codigo_plano INTEGER NOT NULL,
                    FOREIGN KEY (codigo_plano) REFERENCES plano(codigo_plano) ON DELETE CASCADE ON UPDATE CASCADE
                );

                -- Contato dos alunos
                CREATE TABLE IF NOT EXISTS contato_aluno (
                    telefone VARCHAR(15) PRIMARY KEY,
                    email VARCHAR(45),
                    matricula INTEGER NOT NULL,
                    FOREIGN KEY (matricula) REFERENCES aluno(matricula) ON DELETE CASCADE ON UPDATE CASCADE
                );

                -- Bioimpedância dos alunos
                CREATE TABLE IF NOT EXISTS bioimpedancia (
                    matricula INTEGER PRIMARY KEY,
                    peso NUMERIC(5,2) NOT NULL,
                    altura NUMERIC(4,2) NOT NULL,
                    tmb INTEGER NOT NULL,
                    percentual_gordura NUMERIC(5,2) NOT NULL,
                    quantidade_agua NUMERIC(5,2) NOT NULL,
                    FOREIGN KEY (matricula) REFERENCES aluno(matricula) ON DELETE CASCADE ON UPDATE CASCADE
                );

                -- Tabela de instrutores
                CREATE TABLE IF NOT EXISTS instrutor (
                    cref INTEGER PRIMARY KEY,
                    cpf VARCHAR(11) UNIQUE NOT NULL,
                    nome VARCHAR(30) NOT NULL,
                    data_nascimento DATE NOT NULL,
                    data_admissao DATE NOT NULL,
                    turno VARCHAR(15) NOT NULL,
                    CHECK (AGE(current_date, data_nascimento) >= INTERVAL '18 years')
                );

                -- Contato dos instrutores
                CREATE TABLE IF NOT EXISTS contato_instrutor (
                    telefone VARCHAR(15) PRIMARY KEY,
                    email VARCHAR(45),
                    cref INTEGER NOT NULL,
                    FOREIGN KEY (cref) REFERENCES instrutor(cref) ON DELETE CASCADE ON UPDATE CASCADE
                );

                -- Turmas com instrutor vinculado
                CREATE TABLE IF NOT EXISTS turma (
                    id_turma SERIAL PRIMARY KEY,
                    nome_atividade VARCHAR(45) NOT NULL,
                    quantidade_vagas INTEGER CHECK (quantidade_vagas > 0),
                    turno VARCHAR(15) NOT NULL,
                    cref INTEGER NOT NULL,
                    FOREIGN KEY (cref) REFERENCES instrutor(cref) ON DELETE CASCADE ON UPDATE CASCADE
                );

                -- Associação entre alunos e turmas
                CREATE TABLE IF NOT EXISTS turma_instrutor_aluno (
                    id_turma INTEGER,
                    matricula INTEGER,
                    PRIMARY KEY (id_turma, matricula),
                    FOREIGN KEY (id_turma) REFERENCES turma(id_turma) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (matricula) REFERENCES aluno(matricula) ON DELETE CASCADE ON UPDATE CASCADE
                );
            """)

            # Após criar todas as tabelas, adicionar as funções e triggers
            cursor.execute("""
                -- Função para verificar vagas
                CREATE OR REPLACE FUNCTION verificar_vagas_turma()
                RETURNS TRIGGER AS $$
                DECLARE
                    vagas_disponiveis INTEGER;
                    alunos_matriculados INTEGER;
                BEGIN
                    SELECT quantidade_vagas INTO vagas_disponiveis
                    FROM turma
                    WHERE id_turma = NEW.id_turma;

                    SELECT COUNT(*) INTO alunos_matriculados
                    FROM turma_instrutor_aluno
                    WHERE id_turma = NEW.id_turma;

                    IF alunos_matriculados >= vagas_disponiveis THEN
                        RAISE EXCEPTION 'Não há mais vagas disponíveis para esta turma.';
                    END IF;

                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                -- Trigger para verificar vagas
                DROP TRIGGER IF EXISTS trigger_verificar_vagas ON turma_instrutor_aluno;
                CREATE TRIGGER trigger_verificar_vagas
                BEFORE INSERT ON turma_instrutor_aluno
                FOR EACH ROW
                EXECUTE FUNCTION verificar_vagas_turma();

                -- Função para atualizar plano
                CREATE OR REPLACE FUNCTION atualizar_plano_aluno(
                    p_matricula INTEGER,
                    p_novo_plano INTEGER
                ) RETURNS TEXT AS $$
                DECLARE
                    preco_atual NUMERIC(10,2);
                    preco_novo NUMERIC(10,2);
                BEGIN
                    SELECT p.preco INTO preco_atual
                    FROM aluno a
                    JOIN plano p ON a.codigo_plano = p.codigo_plano
                    WHERE a.matricula = p_matricula;

                    SELECT preco INTO preco_novo
                    FROM plano
                    WHERE codigo_plano = p_novo_plano;

                    IF preco_novo <= preco_atual THEN
                        RETURN 'Erro: O novo plano deve ser mais caro que o atual!';
                    END IF;

                    UPDATE aluno
                    SET codigo_plano = p_novo_plano,
                        data_matricula = CURRENT_DATE
                    WHERE matricula = p_matricula;

                    RETURN 'Plano alterado com sucesso!';
                END;
                $$ LANGUAGE plpgsql;

                -- View para relatório de alunos
                CREATE OR REPLACE VIEW vw_relatorio_alunos AS
                SELECT 
                    a.matricula, 
                    a.nome AS nome_aluno, 
                    a.cpf, 
                    DATE_PART('year', AGE(current_date, a.data_nascimento)) AS idade,
                    a.data_matricula, 
                    p.nome_plano, 
                    p.preco AS valor_plano
                FROM aluno a
                JOIN plano p ON a.codigo_plano = p.codigo_plano;
            """)

            conn.commit()
            print("Banco de dados inicializado com sucesso!")
            return True

    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        return False

    finally:
        close_connection(conn)