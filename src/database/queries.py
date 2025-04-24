# filepath: gim/src/database/queries.py

import psycopg2
from psycopg2 import sql
from datetime import date
from typing import List, Optional, Tuple, Any

def execute_query(connection: psycopg2.extensions.connection, 
                 query: str, 
                 params: Optional[Tuple[Any, ...]] = None) -> List[Tuple]:
    """
    Executa uma query no banco de dados.
    
    Args:
        connection: Conexão com o banco de dados
        query: Query SQL a ser executada
        params: Parâmetros para a query (opcional)
    
    Returns:
        List[Tuple]: Resultado da query
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description is not None:
                return cursor.fetchall()
            return []
    except psycopg2.Error as e:
        connection.rollback()
        raise Exception(f"Erro ao executar query: {str(e)}")

# Funções para Planos
def create_plano(conn: psycopg2.extensions.connection,
                nome_plano: str,
                preco: float,
                descricao: Optional[str] = None) -> List[Tuple]:
    """Cria um novo plano no banco de dados"""
    query = """
        INSERT INTO plano (nome_plano, preco, descricao)
        VALUES (%s, %s, %s)
        RETURNING codigo_plano;
    """
    return execute_query(conn, query, (nome_plano, preco, descricao))

def read_plano(conn: psycopg2.extensions.connection,
               codigo_plano: Optional[int] = None) -> List[Tuple]:
    """Busca planos no banco de dados"""
    try:
        if codigo_plano:
            query = """
                SELECT codigo_plano, nome_plano, preco, descricao 
                FROM plano 
                WHERE codigo_plano = %s;
            """
            return execute_query(conn, query, (codigo_plano,))
        
        query = """
            SELECT codigo_plano, nome_plano, preco, descricao 
            FROM plano 
            ORDER BY codigo_plano;
        """
        return execute_query(conn, query)
    except Exception as e:
        print(f"Erro ao buscar plano(s): {str(e)}")
        raise

def update_plano(conn: psycopg2.extensions.connection,
                codigo_plano: int,
                nome_plano: Optional[str] = None,
                preco: Optional[float] = None,
                descricao: Optional[str] = None) -> None:
    """
    Atualiza um plano existente.
    
    Args:
        conn: Conexão com o banco
        codigo_plano: Código do plano
        nome_plano: Novo nome do plano
        preco: Novo preço
        descricao: Nova descrição
    """
    updates = []
    params = []
    
    if nome_plano is not None:
        updates.append("nome_plano = %s")
        params.append(nome_plano)
    
    if preco is not None:
        updates.append("preco = %s")
        params.append(preco)
    
    if descricao is not None:
        updates.append("descricao = %s")
        params.append(descricao)
    
    if updates:
        query = f"""
            UPDATE plano 
            SET {', '.join(updates)}
            WHERE codigo_plano = %s;
        """
        params.append(codigo_plano)
        execute_query(conn, query, tuple(params))

def delete_plano(conn: psycopg2.extensions.connection,
                codigo_plano: int) -> None:
    """Remove um plano do banco de dados"""
    query = "DELETE FROM plano WHERE codigo_plano = %s;"
    execute_query(conn, query, (codigo_plano,))

# Funções para Turmas
def create_turma(conn: psycopg2.extensions.connection,
                nome_atividade: str,
                quantidade_vagas: int,
                turno: str,
                cref: int) -> List[Tuple]:
    """
    Cria uma nova turma no banco de dados.
    
    Args:
        conn: Conexão com o banco
        nome_atividade: Nome da atividade
        quantidade_vagas: Número de vagas
        turno: Turno da turma
        cref: CREF do instrutor
        
    Returns:
        List[Tuple]: ID da turma criada
    """
    query = """
        INSERT INTO turma (nome_atividade, quantidade_vagas, turno, cref)
        VALUES (%s, %s, %s, %s)
        RETURNING id_turma;
    """
    return execute_query(
        conn, 
        query, 
        (nome_atividade, quantidade_vagas, turno, cref)
    )

def read_turma(conn: psycopg2.extensions.connection,
               id_turma: Optional[int] = None) -> List[Tuple]:
    """Busca turmas no banco de dados"""
    try:
        if id_turma:
            query = """
                SELECT 
                    t.id_turma,
                    t.nome_atividade,
                    t.quantidade_vagas,
                    t.turno,
                    t.cref,
                    i.cpf,
                    i.nome,
                    i.data_nascimento,
                    i.data_admissao,
                    i.turno as instrutor_turno,
                    ci.telefone,
                    ci.email,
                    array_agg(a.matricula) FILTER (WHERE a.matricula IS NOT NULL)
                FROM turma t
                JOIN instrutor i ON t.cref = i.cref
                LEFT JOIN contato_instrutor ci ON i.cref = ci.cref
                LEFT JOIN turma_instrutor_aluno tia ON t.id_turma = tia.id_turma
                LEFT JOIN aluno a ON tia.matricula = a.matricula
                WHERE t.id_turma = %s
                GROUP BY t.id_turma, t.nome_atividade, t.quantidade_vagas, 
                         t.turno, t.cref, i.cpf, i.nome, i.data_nascimento,
                         i.data_admissao, i.turno, ci.telefone, ci.email;
            """
            return execute_query(conn, query, (id_turma,))
        
        query = """
            SELECT 
                t.id_turma,
                t.nome_atividade,
                t.quantidade_vagas,
                t.turno,
                t.cref,
                i.cpf,
                i.nome,
                i.data_nascimento,
                i.data_admissao,
                i.turno as instrutor_turno,
                ci.telefone,
                ci.email,
                array_agg(a.matricula) FILTER (WHERE a.matricula IS NOT NULL)
            FROM turma t
            JOIN instrutor i ON t.cref = i.cref
            LEFT JOIN contato_instrutor ci ON i.cref = ci.cref
            LEFT JOIN turma_instrutor_aluno tia ON t.id_turma = tia.id_turma
            LEFT JOIN aluno a ON tia.matricula = a.matricula
            GROUP BY t.id_turma, t.nome_atividade, t.quantidade_vagas, 
                     t.turno, t.cref, i.cpf, i.nome, i.data_nascimento,
                     i.data_admissao, i.turno, ci.telefone, ci.email
            ORDER BY t.nome_atividade;
        """
        return execute_query(conn, query)
    except Exception as e:
        print(f"Erro ao buscar turma(s): {str(e)}")
        raise

def update_turma(conn: psycopg2.extensions.connection,
                id_turma: int,
                nome_atividade: Optional[str] = None,
                quantidade_vagas: Optional[int] = None,
                turno: Optional[str] = None,
                cref: Optional[int] = None) -> None:
    """
    Atualiza uma turma existente.
    
    Args:
        conn: Conexão com o banco
        id_turma: ID da turma a ser atualizada
        nome_atividade: Novo nome da atividade (opcional)
        quantidade_vagas: Nova quantidade de vagas (opcional)
        turno: Novo turno (opcional)
        cref: Novo CREF do instrutor (opcional)
    """
    updates = []
    params = []
    
    if nome_atividade is not None:
        updates.append("nome_atividade = %s")
        params.append(nome_atividade)
    
    if quantidade_vagas is not None:
        updates.append("quantidade_vagas = %s")
        params.append(quantidade_vagas)
    
    if turno is not None:
        updates.append("turno = %s")
        params.append(turno)
    
    if cref is not None:
        updates.append("cref = %s")
        params.append(cref)
    
    if updates:
        query = f"""
            UPDATE turma 
            SET {', '.join(updates)}
            WHERE id_turma = %s;
        """
        params.append(id_turma)
        execute_query(conn, query, tuple(params))

def delete_turma(conn: psycopg2.extensions.connection,
                id_turma: int) -> None:
    """
    Remove uma turma do banco de dados.
    
    Args:
        conn: Conexão com o banco
        id_turma: ID da turma a ser removida
    """
    query = "DELETE FROM turma WHERE id_turma = %s;"
    execute_query(conn, query, (id_turma,))

def create_matricula_turma(conn: psycopg2.extensions.connection,
                         id_turma: int,
                         matricula: int) -> None:
    """Matricula um aluno em uma turma"""
    try:
        # Verifica se há vagas disponíveis
        query_vagas = """
            SELECT quantidade_vagas, 
                   (SELECT COUNT(*) FROM turma_instrutor_aluno 
                    WHERE id_turma = %s) as alunos_matriculados
            FROM turma WHERE id_turma = %s;
        """
        result = execute_query(conn, query_vagas, (id_turma, id_turma))
        if not result:
            raise Exception("Turma não encontrada")
            
        vagas_totais = result[0][0]
        alunos_matriculados = result[0][1]
        
        if alunos_matriculados >= vagas_totais:
            raise Exception("Turma sem vagas disponíveis")
            
        # Realiza a matrícula
        query = """
            INSERT INTO turma_instrutor_aluno (id_turma, matricula)
            VALUES (%s, %s);
        """
        execute_query(conn, query, (id_turma, matricula))
    except Exception as e:
        print(f"Erro ao matricular aluno: {str(e)}")
        raise

def delete_matricula_turma(conn: psycopg2.extensions.connection,
                         id_turma: int,
                         matricula: int) -> None:
    """
    Remove um aluno de uma turma.
    
    Args:
        conn: Conexão com o banco
        id_turma: ID da turma
        matricula: Matrícula do aluno
    """
    query = """
        DELETE FROM turma_instrutor_aluno 
        WHERE id_turma = %s AND matricula = %s;
    """
    execute_query(conn, query, (id_turma, matricula))

# Funções para Alunos
def create_aluno(conn: psycopg2.extensions.connection,
                cpf: str,
                nome: str,
                sexo: str,
                data_nascimento: date,
                data_matricula: date,
                codigo_plano: int) -> List[Tuple]:
    """
    Cria um novo aluno no banco de dados.
    
    Returns:
        List[Tuple]: Matrícula do aluno criado
    """
    query = """
        INSERT INTO aluno (cpf, nome, sexo, data_nascimento, data_matricula, codigo_plano)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING matricula;
    """
    return execute_query(
        conn, 
        query,
        (cpf, nome, sexo, data_nascimento, data_matricula, codigo_plano)
    )

def read_aluno(conn: psycopg2.extensions.connection,
               matricula: Optional[int] = None) -> List[Tuple]:
    """Busca alunos no banco de dados"""
    try:
        if matricula:
            query = """
                SELECT 
                    a.matricula,
                    a.cpf,
                    a.nome,
                    a.sexo,
                    a.data_nascimento,
                    a.data_matricula,
                    a.codigo_plano,
                    c.telefone,
                    c.email
                FROM aluno a
                LEFT JOIN contato_aluno c ON a.matricula = c.matricula
                WHERE a.matricula = %s;
            """
            return execute_query(conn, query, (matricula,))
        
        query = """
            SELECT 
                a.matricula,
                a.cpf,
                a.nome,
                a.sexo,
                a.data_nascimento,
                a.data_matricula,
                a.codigo_plano,
                c.telefone,
                c.email
            FROM aluno a
            LEFT JOIN contato_aluno c ON a.matricula = c.matricula
            ORDER BY a.nome;
        """
        return execute_query(conn, query)
    except Exception as e:
        print(f"Erro ao buscar aluno(s): {str(e)}")
        raise

def update_aluno(conn: psycopg2.extensions.connection,
                matricula: int,
                cpf: Optional[str] = None,
                nome: Optional[str] = None,
                sexo: Optional[str] = None,
                data_nascimento: Optional[date] = None,
                data_matricula: Optional[date] = None,
                codigo_plano: Optional[int] = None) -> None:
    """Atualiza os dados de um aluno"""
    updates = []
    params = []
    
    if cpf is not None:
        updates.append("cpf = %s")
        params.append(cpf)
    
    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)
    
    if sexo is not None:
        updates.append("sexo = %s")
        params.append(sexo)
    
    if data_nascimento is not None:
        updates.append("data_nascimento = %s")
        params.append(data_nascimento)
    
    if data_matricula is not None:
        updates.append("data_matricula = %s")
        params.append(data_matricula)
    
    if codigo_plano is not None:
        updates.append("codigo_plano = %s")
        params.append(codigo_plano)
    
    if updates:
        query = f"""
            UPDATE aluno 
            SET {', '.join(updates)}
            WHERE matricula = %s;
        """
        params.append(matricula)
        execute_query(conn, query, tuple(params))

def delete_aluno(conn: psycopg2.extensions.connection,
                matricula: int) -> None:
    """Remove um aluno do banco de dados"""
    query = "DELETE FROM aluno WHERE matricula = %s;"
    execute_query(conn, query, (matricula,))

# Funções para Contatos
def create_contato_aluno(conn: psycopg2.extensions.connection,
                        matricula: int,
                        telefone: str,
                        email: Optional[str] = None) -> None:
    """Cria um novo contato para aluno"""
    query = """
        INSERT INTO contato_aluno (matricula, telefone, email)
        VALUES (%s, %s, %s);
    """
    execute_query(conn, query, (matricula, telefone, email))

def create_contato_instrutor(conn: psycopg2.extensions.connection,
                           cref: int,
                           telefone: str,
                           email: Optional[str] = None) -> None:
    """Cria um novo contato para instrutor"""
    query = """
        INSERT INTO contato_instrutor (cref, telefone, email)
        VALUES (%s, %s, %s);
    """
    execute_query(conn, query, (cref, telefone, email))

def update_contato_aluno(conn: psycopg2.extensions.connection,
                        matricula: int,
                        telefone: Optional[str] = None,
                        email: Optional[str] = None) -> None:
    """Atualiza o contato de um aluno"""
    updates = []
    params = []
    
    if telefone is not None:
        updates.append("telefone = %s")
        params.append(telefone)
    
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    
    if updates:
        query = f"""
            UPDATE contato_aluno 
            SET {', '.join(updates)}
            WHERE matricula = %s;
        """
        params.append(matricula)
        execute_query(conn, query, tuple(params))

def update_contato_instrutor(conn: psycopg2.extensions.connection,
                           cref: int,
                           telefone: Optional[str] = None,
                           email: Optional[str] = None) -> None:
    """Atualiza o contato de um instrutor"""
    updates = []
    params = []
    
    if telefone is not None:
        updates.append("telefone = %s")
        params.append(telefone)
    
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    
    if updates:
        query = f"""
            UPDATE contato_instrutor 
            SET {', '.join(updates)}
            WHERE cref = %s;
        """
        params.append(cref)
        execute_query(conn, query, tuple(params))

# Funções para Bioimpedância
def read_bioimpedancia(conn: psycopg2.extensions.connection,
                      matricula: Optional[int] = None) -> List[Tuple]:
    """Busca medições de bioimpedância"""
    try:
        if matricula:
            query = """
                SELECT 
                    matricula,
                    peso,
                    altura,
                    tmb,
                    percentual_gordura,
                    quantidade_agua
                FROM bioimpedancia 
                WHERE matricula = %s;
            """
            return execute_query(conn, query, (matricula,))
        
        query = """
            SELECT 
                matricula,
                peso,
                altura,
                tmb,
                percentual_gordura,
                quantidade_agua
            FROM bioimpedancia;
        """
        return execute_query(conn, query)
    except Exception as e:
        print(f"Erro ao buscar bioimpedância: {str(e)}")
        raise

def create_bioimpedancia(conn: psycopg2.extensions.connection,
                        matricula: int,
                        peso: float,
                        altura: float,
                        tmb: int,
                        percentual_gordura: float,
                        quantidade_agua: float) -> None:
    """Cria uma nova medição de bioimpedância"""
    query = """
        INSERT INTO bioimpedancia (
            matricula, 
            peso, 
            altura, 
            tmb, 
            percentual_gordura, 
            quantidade_agua
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    execute_query(
        conn, 
        query,
        (matricula, peso, altura, tmb, percentual_gordura, quantidade_agua)
    )

def update_bioimpedancia(conn: psycopg2.extensions.connection,
                        matricula: int,
                        peso: Optional[float] = None,
                        altura: Optional[float] = None,
                        tmb: Optional[int] = None,
                        percentual_gordura: Optional[float] = None,
                        quantidade_agua: Optional[float] = None) -> None:
    """Atualiza uma medição de bioimpedância"""
    updates = []
    params = []
    
    if peso is not None:
        updates.append("peso = %s")
        params.append(peso)
    
    if altura is not None:
        updates.append("altura = %s")
        params.append(altura)
    
    if tmb is not None:
        updates.append("tmb = %s")
        params.append(tmb)
    
    if percentual_gordura is not None:
        updates.append("percentual_gordura = %s")
        params.append(percentual_gordura)
    
    if quantidade_agua is not None:
        updates.append("quantidade_agua = %s")
        params.append(quantidade_agua)
    
    if updates:
        query = f"""
            UPDATE bioimpedancia 
            SET {', '.join(updates)}
            WHERE matricula = %s;
        """
        params.append(matricula)
        execute_query(conn, query, tuple(params))

def delete_bioimpedancia(conn: psycopg2.extensions.connection,
                        matricula: int) -> None:
    """Remove uma medição de bioimpedância"""
    query = "DELETE FROM bioimpedancia WHERE matricula = %s;"
    execute_query(conn, query, (matricula,))

# Funções para Instrutores
def create_instrutor(conn: psycopg2.extensions.connection,
                    cref: int,
                    cpf: str,
                    nome: str,
                    data_nascimento: date,
                    data_admissao: date,
                    turno: str) -> None:
    """Cria um novo instrutor"""
    query = """
        INSERT INTO instrutor (
            cref, cpf, nome, data_nascimento, 
            data_admissao, turno
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    execute_query(
        conn, 
        query,
        (cref, cpf, nome, data_nascimento, data_admissao, turno)
    )

def read_instrutor(conn: psycopg2.extensions.connection,
                  cref: Optional[int] = None) -> List[Tuple]:
    """
    Busca instrutores no banco de dados.
    
    Args:
        conn: Conexão com o banco
        cref: CREF do instrutor (opcional)
        
    Returns:
        List[Tuple]: Lista de instrutores encontrados
    """
    try:
        if cref:
            query = """
                SELECT 
                    i.cref,
                    i.cpf,
                    i.nome,
                    i.data_nascimento,
                    i.data_admissao,
                    i.turno,
                    c.telefone,
                    c.email
                FROM instrutor i
                LEFT JOIN contato_instrutor c ON i.cref = c.cref
                WHERE i.cref = %s;
            """
            result = execute_query(conn, query, (cref,))
            if not result:
                raise Exception("Instrutor não encontrado")
            return result
            
        query = """
            SELECT 
                i.cref,
                i.cpf,
                i.nome,
                i.data_nascimento,
                i.data_admissao,
                i.turno,
                c.telefone,
                c.email
            FROM instrutor i
            LEFT JOIN contato_instrutor c ON i.cref = c.cref
            ORDER BY i.nome;
        """
        return execute_query(conn, query)
        
    except Exception as e:
        print(f"Erro ao buscar instrutor(es): {str(e)}")
        raise

def read_instrutor_por_cref(conn: psycopg2.extensions.connection, cref: int) -> List[Tuple]:
    """Busca um instrutor específico pelo CREF"""
    try:
        query = """
            SELECT 
                i.cref,
                i.cpf,
                i.nome,
                i.data_nascimento,
                i.data_admissao,
                i.turno,
                ci.telefone,
                ci.email
            FROM instrutor i
            LEFT JOIN contato_instrutor ci ON i.cref = ci.cref
            WHERE i.cref = %s;
        """
        return execute_query(conn, query, (cref,))
    except Exception as e:
        print(f"Erro ao buscar instrutor: {str(e)}")
        raise

def update_instrutor(conn: psycopg2.extensions.connection,
                    cref: int,
                    cpf: Optional[str] = None,
                    nome: Optional[str] = None,
                    data_nascimento: Optional[date] = None,
                    data_admissao: Optional[date] = None,
                    turno: Optional[str] = None) -> None:
    """Atualiza os dados de um instrutor"""
    updates = []
    params = []
    
    if cpf is not None:
        updates.append("cpf = %s")
        params.append(cpf)
    
    if nome is not None:
        updates.append("nome = %s")
        params.append(nome)
    
    if data_nascimento is not None:
        updates.append("data_nascimento = %s")
        params.append(data_nascimento)
    
    if data_admissao is not None:
        updates.append("data_admissao = %s")
        params.append(data_admissao)
    
    if turno is not None:
        updates.append("turno = %s")
        params.append(turno)
    
    if updates:
        query = f"""
            UPDATE instrutor 
            SET {', '.join(updates)}
            WHERE cref = %s;
        """
        params.append(cref)
        execute_query(conn, query, tuple(params))

def delete_instrutor(conn: psycopg2.extensions.connection,
                    cref: int) -> None:
    """Remove um instrutor"""
    query = "DELETE FROM instrutor WHERE cref = %s;"
    execute_query(conn, query, (cref,))

def get_relatorio_alunos(conn: psycopg2.extensions.connection) -> List[Tuple]:
    """Retorna o relatório de alunos da view"""
    try:
        query = "SELECT * FROM vw_relatorio_alunos ORDER BY nome_aluno;"
        return execute_query(conn, query)
    except Exception as e:
        print(f"Erro ao buscar relatório de alunos: {str(e)}")
        raise