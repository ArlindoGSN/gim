from fastapi import APIRouter, HTTPException, Depends, Path, Query, Body, status
from typing import List, Optional
from src.models.schemas import *
from src.database.connection import get_connection
from src.database.queries import *
from datetime import date
from src.utils.helpers import (
    plano_to_dict,
    aluno_to_dict,
    bioimpedancia_to_dict,
    instrutor_to_dict,
    turma_to_dict
)

router = APIRouter()

# CRUD Rotas de Planos
@router.post(
    "/planos/",
    response_model=PlanoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo plano",
    tags=["Planos"]  # Usando tag já definida
)
async def criar_plano(plano: PlanoCreate):
    """
    Cria um novo plano de academia.
    
    **Parâmetros**:
    - **nome_plano**: Nome do plano
    - **preco**: Valor mensal
    - **descricao**: Descrição opcional
    """
    try:
        conn = get_connection()
        result = create_plano(
            conn,
            plano.nome_plano,
            plano.preco,
            plano.descricao
        )
        conn.commit()
        return PlanoResponse(codigo_plano=result[0][0], **plano.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Rotas GET de Planos
@router.get(
    "/planos/",
    response_model=List[PlanoResponse],
    summary="Listar planos",
    description="Retorna a lista de todos os planos cadastrados",
    tags=["Planos"]
)
async def listar_planos(skip: int = 0, limit: int = 100):
    try:
        conn = get_connection()
        result = read_plano(conn)
        planos = [plano_to_dict(row) for row in result]
        return planos[skip : skip + limit]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/planos/{codigo_plano}",
    response_model=PlanoResponse,
    summary="Buscar plano",
    description="Retorna um plano específico pelo código",
    tags=["Planos"]
)
async def buscar_plano(codigo_plano: int):
    try:
        conn = get_connection()
        result = read_plano(conn, codigo_plano)
        if not result:
            raise HTTPException(404, "Plano não encontrado")
        return plano_to_dict(result[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/planos/{codigo_plano}",
    response_model=PlanoResponse,
    summary="Atualizar plano",
    tags=["Planos"]
)
async def atualizar_plano(codigo_plano: int, plano: PlanoUpdate):
    """
    Atualiza um plano existente com novos dados.

    - **codigo_plano**: código do plano (obrigatório)
    - **plano**: novos dados do plano (obrigatório)
    """
    try:
        conn = get_connection()
        update_plano(
            conn,
            codigo_plano,
            plano.nome_plano,
            plano.preco,
            plano.descricao
        )
        conn.commit()
        return PlanoResponse(
            codigo_plano=codigo_plano,
            **plano.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=str(e)
        )

@router.delete(
    "/planos/{codigo_plano}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar plano",
    tags=["Planos"]
)
async def deletar_plano(codigo_plano: int):
    """
    Deleta um plano existente.

    - **codigo_plano**: código do plano (obrigatório)
    """
    try:
        conn = get_connection()
        delete_plano(conn, codigo_plano)
        conn.commit()
        return {"message": "Plano deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CRUD Rotas de Alunos
@router.post(
    "/alunos/",
    response_model=AlunoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo aluno",
    tags=["Alunos"]  # Usando tag já definida
)
async def criar_aluno(aluno: AlunoCreate):
    """
    Cadastra um novo aluno na academia.
    
    **Parâmetros**:
    - **cpf**: CPF do aluno
    - **nome**: Nome completo
    - **sexo**: M ou F
    - **data_nascimento**: Data de nascimento
    - **data_matricula**: Data da matrícula
    - **codigo_plano**: Código do plano escolhido
    - **contato**: Informações de contato
    """
    try:
        conn = get_connection()
        # Criar aluno
        result = create_aluno(
            conn,
            aluno.cpf,
            aluno.nome,
            aluno.sexo,
            aluno.data_nascimento,
            aluno.data_matricula,
            aluno.codigo_plano
        )
        matricula = result[0][0]
        
        # Criar contato do aluno
        create_contato_aluno(
            conn,
            matricula,
            aluno.contato.telefone,
            aluno.contato.email
        )
        
        conn.commit()
        return AlunoResponse(
            matricula=matricula,
            contato=aluno.contato,
            **aluno.model_dump(exclude={'contato'})
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rotas GET de Alunos
@router.get(
    "/alunos/",
    response_model=List[AlunoResponse],
    summary="Listar alunos",
    description="Retorna a lista de todos os alunos cadastrados",
    tags=["Alunos"]
)
async def listar_alunos(skip: int = 0, limit: int = 100):
    try:
        conn = get_connection()
        result = read_aluno(conn)
        alunos = [aluno_to_dict(row) for row in result]
        return alunos[skip : skip + limit]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/alunos/{matricula}",
    response_model=AlunoResponse,
    summary="Buscar aluno",
    description="Retorna um aluno específico pela matrícula",
    tags=["Alunos"]
)
async def buscar_aluno(matricula: int):
    try:
        conn = get_connection()
        result = read_aluno(conn, matricula)
        if not result:
            raise HTTPException(404, "Aluno não encontrado")
        return aluno_to_dict(result[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/alunos/{matricula}",
    response_model=AlunoResponse,
    summary="Atualizar aluno",
    tags=["Alunos"]
)
async def atualizar_aluno(matricula: int, aluno: AlunoUpdate):
    """
    Atualiza um aluno existente com novos dados.

    - **matricula**: matrícula do aluno (obrigatório)
    - **aluno**: novos dados do aluno (obrigatório)
    """
    try:
        conn = get_connection()
        update_aluno(
            conn,
            matricula,
            aluno.cpf,
            aluno.nome,
            aluno.sexo,
            aluno.data_nascimento,
            aluno.data_matricula,
            aluno.codigo_plano
        )
        if aluno.contato:
            # Atualizar contato se fornecido
            update_contato_aluno(
                conn,
                matricula,
                aluno.contato.telefone,
                aluno.contato.email
            )
        conn.commit()
        return await buscar_aluno(matricula)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/alunos/{matricula}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar aluno",
    tags=["Alunos"]
)
async def deletar_aluno(matricula: int):
    """
    Deleta um aluno existente.

    - **matricula**: matrícula do aluno (obrigatório)
    """
    try:
        conn = get_connection()
        delete_aluno(conn, matricula)
        conn.commit()
        return {"message": "Aluno deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CRUD Rotas de Bioimpedância
@router.post(
    "/bioimpedancia/",
    response_model=BioimpedanciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar medição",
    tags=["Bioimpedância"]  # Usando tag já definida
)
async def criar_bioimpedancia(bio: BioimpedanciaCreate):
    """
    Registra uma nova medição de bioimpedância.
    
    **Parâmetros**:
    - **matricula**: Matrícula do aluno
    - **peso**: Peso em kg
    - **altura**: Altura em metros
    - **tmb**: Taxa Metabólica Basal
    - **percentual_gordura**: % de gordura
    - **quantidade_agua**: % de água
    """
    try:
        conn = get_connection()
        create_bioimpedancia(
            conn,
            bio.matricula,
            bio.peso,
            bio.altura,
            bio.tmb,
            bio.percentual_gordura,
            bio.quantidade_agua
        )
        conn.commit()
        return BioimpedanciaResponse(**bio.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rotas GET de Bioimpedância
@router.get(
    "/bioimpedancia/",
    response_model=List[BioimpedanciaResponse],
    summary="Listar medições",
    description="Retorna todas as medições de bioimpedância",
    tags=["Bioimpedância"]
)
async def listar_bioimpedancias(skip: int = 0, limit: int = 100):
    try:
        conn = get_connection()
        result = read_bioimpedancia(conn)
        bios = [bioimpedancia_to_dict(row) for row in result]
        return bios[skip : skip + limit]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/bioimpedancia/{matricula}",
    response_model=BioimpedanciaResponse,
    summary="Buscar medição",
    description="Retorna a medição de um aluno específico",
    tags=["Bioimpedância"]
)
async def buscar_bioimpedancia(matricula: int):
    try:
        conn = get_connection()
        result = read_bioimpedancia(conn, matricula)
        if not result:
            raise HTTPException(404, "Medição não encontrada")
        return bioimpedancia_to_dict(result[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/bioimpedancia/{matricula}",
    response_model=BioimpedanciaResponse,
    summary="Atualizar medição",
    tags=["Bioimpedância"]
)
async def atualizar_bioimpedancia(
    matricula: int,
    bio: BioimpedanciaCreate
):
    """
    Atualiza uma medição existente com novos dados.

    - **matricula**: matrícula do aluno (obrigatório)
    - **bio**: novos dados da medição (obrigatório)
    """
    try:
        conn = get_connection()
        update_bioimpedancia(
            conn,
            matricula,
            bio.peso,
            bio.altura,
            bio.tmb,
            bio.percentual_gordura,
            bio.quantidade_agua
        )
        conn.commit()
        return await buscar_bioimpedancia(matricula)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/bioimpedancia/{matricula}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar medição",
    tags=["Bioimpedância"]
)
async def deletar_bioimpedancia(matricula: int):
    """
    Deleta uma medição existente.

    - **matricula**: matrícula do aluno (obrigatório)
    """
    try:
        conn = get_connection()
        delete_bioimpedancia(conn, matricula)
        conn.commit()
        return {"message": "Medição deletada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CRUD Rotas de Instrutores
@router.post(
    "/instrutores/",
    response_model=InstrutorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo instrutor",
    tags=["Instrutores"]  # Usando tag já definida
)
async def criar_instrutor(instrutor: InstrutorCreate):
    """
    Cadastra um novo instrutor.
    
    **Parâmetros**:
    - **cref**: Número do CREF
    - **cpf**: CPF do instrutor
    - **nome**: Nome completo
    - **data_nascimento**: Data de nascimento
    - **data_admissao**: Data de admissão
    - **turno**: Turno de trabalho
    - **contato**: Informações de contato
    """
    try:
        conn = get_connection()
        # Criar instrutor
        create_instrutor(
            conn,
            instrutor.cref,
            instrutor.cpf,
            instrutor.nome,
            instrutor.data_nascimento,
            instrutor.data_admissao,
            instrutor.turno
        )
        
        # Criar contato do instrutor
        create_contato_instrutor(
            conn,
            instrutor.cref,
            instrutor.contato.telefone,
            instrutor.contato.email
        )
        
        conn.commit()
        return InstrutorResponse(
            contato=instrutor.contato,
            **instrutor.model_dump(exclude={'contato'})
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rotas GET de Instrutores
@router.get(
    "/instrutores/",
    response_model=List[InstrutorResponse],
    summary="Listar instrutores",
    description="Retorna a lista de todos os instrutores",
    tags=["Instrutores"]
)
async def listar_instrutores(skip: int = 0, limit: int = 100):
    try:
        conn = get_connection()
        result = read_instrutor(conn)
        instrutores = [instrutor_to_dict(row) for row in result]
        return instrutores[skip : skip + limit]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/instrutores/{cref}",
    response_model=InstrutorResponse,
    summary="Buscar instrutor",
    description="Retorna um instrutor específico pelo CREF",
    tags=["Instrutores"]
)
async def buscar_instrutor(cref: int):
    try:
        conn = get_connection()
        result = read_instrutor(conn, cref)
        if not result:
            raise HTTPException(404, "Instrutor não encontrado")
        return instrutor_to_dict(result[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/instrutores/{cref}",
    response_model=InstrutorResponse,
    summary="Atualizar instrutor",
    tags=["Instrutores"]
)
async def atualizar_instrutor(cref: int, instrutor: InstrutorUpdate):
    """
    Atualiza um instrutor existente.

    - **cref**: número do CREF (obrigatório)
    - **instrutor**: novos dados do instrutor (obrigatório)
    """
    try:
        conn = get_connection()
        update_instrutor(
            conn,
            cref,
            instrutor.cpf,
            instrutor.nome,
            instrutor.data_nascimento,
            instrutor.data_admissao,
            instrutor.turno
        )
        if instrutor.contato:
            update_contato_instrutor(
                conn,
                cref,
                instrutor.contato.telefone,
                instrutor.contato.email
            )
        conn.commit()
        return await buscar_instrutor(cref)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/instrutores/{cref}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar instrutor",
    tags=["Instrutores"]
)
async def deletar_instrutor(cref: int):
    """
    Remove um instrutor do sistema.

    - **cref**: número do CREF (obrigatório)
    """
    try:
        conn = get_connection()
        delete_instrutor(conn, cref)
        conn.commit()
        return {"message": "Instrutor deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# CRUD Rotas de Turmas
@router.post(
    "/turmas/",
    response_model=TurmaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova turma",
    tags=["Turmas"]  # Usando tag já definida
)
async def criar_turma(turma: TurmaCreate):
    """
    Cria uma nova turma.
    
    **Parâmetros**:
    - **nome_atividade**: Nome da atividade
    - **quantidade_vagas**: Número de vagas
    - **turno**: Turno da turma
    - **cref**: CREF do instrutor responsável
    """
    try:
        conn = get_connection()
        
        # Verifica se o instrutor existe
        instrutor_result = read_instrutor_por_cref(conn, turma.cref)
        if not instrutor_result:
            raise HTTPException(
                status_code=404,
                detail="Instrutor não encontrado"
            )
            
        # Cria a turma
        result = create_turma(
            conn,
            turma.nome_atividade,
            turma.quantidade_vagas,
            turma.turno,
            turma.cref
        )
        
        conn.commit()
        
        # Monta a resposta com os dados do instrutor
        return TurmaResponse(
            id_turma=result[0][0],
            nome_atividade=turma.nome_atividade,
            quantidade_vagas=turma.quantidade_vagas,
            turno=turma.turno,
            cref=turma.cref,
            instrutor=InstrutorResponse.from_tuple(instrutor_result[0]),
            alunos=[]
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get(
    "/turmas/",
    response_model=List[TurmaResponse],
    summary="Listar turmas",
    description="Retorna a lista de todas as turmas cadastradas",
    tags=["Turmas"]
)
async def listar_turmas(
    skip: int = Query(0, description="Registros para pular"),
    limit: int = Query(100, description="Limite de registros")
):
    """Lista todas as turmas cadastradas."""
    try:
        conn = get_connection()
        result = read_turma(conn)
        
        # Converte os resultados em objetos TurmaResponse
        turmas = [TurmaResponse.from_tuple(row) for row in result]
        
        # Aplica a paginação
        return turmas[skip : skip + limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Rotas GET de Turmas
@router.get(
    "/turmas/{id_turma}",
    response_model=TurmaResponse,
    summary="Buscar turma",
    description="Retorna uma turma específica pelo ID",
    tags=["Turmas"]
)
async def buscar_turma(id_turma: int):
    try:
        conn = get_connection()
        result = read_turma(conn, id_turma)
        if not result:
            raise HTTPException(404, "Turma não encontrada")
        return turma_to_dict(result[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/turmas/{id_turma}",
    response_model=TurmaResponse,
    summary="Atualizar turma",
    tags=["Turmas"]
)
async def atualizar_turma(id_turma: int, turma: TurmaUpdate):
    """
    Atualiza uma turma existente.

    - **id_turma**: ID da turma (obrigatório)
    - **turma**: novos dados da turma (obrigatório)
    """
    try:
        conn = get_connection()
        update_turma(
            conn,
            id_turma,
            turma.nome_atividade,
            turma.quantidade_vagas,
            turma.turno,
            turma.cref
        )
        conn.commit()
        return await buscar_turma(id_turma)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/turmas/{id_turma}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar turma",
    tags=["Turmas"]
)
async def deletar_turma(id_turma: int):
    """
    Remove uma turma do sistema.

    - **id_turma**: ID da turma (obrigatório)
    """
    try:
        conn = get_connection()
        delete_turma(conn, id_turma)
        conn.commit()
        return {"message": "Turma deletada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/turmas/{id_turma}/alunos/{matricula}",
    status_code=status.HTTP_201_CREATED,
    summary="Matricular aluno em turma",
    tags=["Turmas"]
)
async def matricular_aluno_turma(
    id_turma: int = Path(..., description="ID da turma"),
    matricula: int = Path(..., description="Matrícula do aluno")
):
    """
    Matricula um aluno em uma turma.

    - **id_turma**: ID da turma
    - **matricula**: Matrícula do aluno
    """
    try:
        conn = get_connection()
        create_matricula_turma(conn, id_turma, matricula)
        conn.commit()
        return {"message": "Aluno matriculado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/turmas/{id_turma}/alunos/{matricula}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover aluno da turma",
    tags=["Turmas"]
)
async def remover_aluno_turma(
    id_turma: int = Path(..., description="ID da turma"),
    matricula: int = Path(..., description="Matrícula do aluno")
):
    """
    Remove um aluno de uma turma.

    - **id_turma**: ID da turma
    - **matricula**: Matrícula do aluno
    """
    try:
        conn = get_connection()
        delete_matricula_turma(conn, id_turma, matricula)
        conn.commit()
        return {"message": "Aluno removido da turma com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/relatorios/alunos/",
    response_model=List[RelatorioAlunoResponse],
    summary="Relatório de alunos",
    description="Retorna relatório detalhado de todos os alunos",
    tags=["Relatórios"]
)
async def relatorio_alunos(
    skip: int = Query(0, description="Registros para pular"),
    limit: int = Query(100, description="Limite de registros")
):
    """Retorna o relatório de alunos"""
    try:
        conn = get_connection()
        result = get_relatorio_alunos(conn)
        
        relatorio = []
        for row in result:
            relatorio.append({
                "matricula": row[0],
                "nome_aluno": row[1],
                "cpf": row[2],
                "idade": row[3],
                "data_matricula": row[4],
                "nome_plano": row[5],
                "valor_plano": float(row[6])
            })
            
        return relatorio[skip : skip + limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )