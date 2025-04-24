# helpers.py

def format_response(data, status_code=200):
    return {
        "status": status_code,
        "data": data
    }

def handle_error(message, status_code=400):
    return {
        "status": status_code,
        "error": message
    }

def validate_input(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"
    return True, ""

def plano_to_dict(row: tuple) -> dict:
    """Converte tupla de plano em dicionário"""
    return {
        "codigo_plano": row[0],
        "nome_plano": row[1],
        "preco": float(row[2]),
        "descricao": row[3]
    }

def aluno_to_dict(row: tuple) -> dict:
    """Converte tupla de aluno em dicionário"""
    return {
        "matricula": row[0],
        "cpf": row[1],
        "nome": row[2],
        "sexo": row[3],
        "data_nascimento": row[4],
        "data_matricula": row[5],
        "codigo_plano": row[6],
        "contato": {
            "telefone": row[7],
            "email": row[8]
        } if row[7] or row[8] else None
    }

def bioimpedancia_to_dict(row: tuple) -> dict:
    """Converte tupla de bioimpedância em dicionário"""
    return {
        "matricula": row[0],
        "peso": float(row[1]),
        "altura": float(row[2]),
        "tmb": row[3],
        "percentual_gordura": float(row[4]),
        "quantidade_agua": float(row[5])
    }

def instrutor_to_dict(row: tuple) -> dict:
    """Converte tupla de instrutor em dicionário"""
    return {
        "cref": row[0],
        "cpf": row[1],
        "nome": row[2],
        "data_nascimento": row[3],
        "data_admissao": row[4],
        "turno": row[5],
        "contato": {
            "telefone": row[6],
            "email": row[7]
        } if row[6] or row[7] else None
    }

def turma_to_dict(row: tuple) -> dict:
    """Converte tupla de turma em dicionário"""
    return {
        "id_turma": row[0],
        "nome_atividade": row[1],
        "quantidade_vagas": row[2],
        "turno": row[3],
        "cref": row[4],
        "instrutor": instrutor_to_dict(row[5:13]),
        "alunos": row[-1] if row[-1] else []
    }