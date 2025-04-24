from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Tuple
from datetime import date
from enum import Enum

class SexoEnum(str, Enum):
    """Enumeração para sexo"""
    MASCULINO = "M"
    FEMININO = "F"

class TurnoEnum(str, Enum):
    """Enumeração para turnos"""
    MANHA = "Manhã"
    TARDE = "Tarde"
    NOITE = "Noite"

# Modelos Base com documentação
class ModeloBase(BaseModel):
    """Modelo base com configuração comum"""
    model_config = ConfigDict(from_attributes=True)

# Modelos para Plano
class PlanoBase(ModeloBase):
    """Modelo base para Plano"""
    nome_plano: str = Field(
        ..., 
        max_length=45,
        description="Nome do plano",
        example="Plano Premium"
    )
    preco: float = Field(
        ..., 
        gt=0,
        description="Preço mensal do plano em reais",
        example=99.90
    )
    descricao: Optional[str] = Field(
        None, 
        max_length=180,
        description="Descrição detalhada do plano",
        example="Acesso completo à academia com direito a todas as modalidades"
    )

class PlanoCreate(PlanoBase):
    """Modelo para criação de plano"""
    class Config:
        json_schema_extra = {
            "example": {
                "nome_plano": "Plano Premium",
                "preco": 99.90,
                "descricao": "Acesso completo à academia"
            }
        }

class PlanoUpdate(PlanoBase):
    """Modelo para atualização de plano"""
    nome_plano: Optional[str] = Field(None, max_length=45)
    preco: Optional[float] = Field(None, gt=0)

class PlanoResponse(PlanoBase):
    """Modelo para resposta de plano"""
    codigo_plano: int = Field(
        ...,
        description="Código único do plano",
        example=1
    )

# Modelos para Contato
class ContatoBase(ModeloBase):
    """Modelo base para contatos"""
    telefone: str = Field(
        ..., 
        max_length=15,
        pattern=r"^\(\d{2}\)\d{4,5}-\d{4}$",
        description="Telefone no formato (99)99999-9999",
        example="(11)99999-9999"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Endereço de email válido",
        example="email@exemplo.com"
    )

class ContatoAlunoCreate(ContatoBase):
    """Modelo para criação de contato de aluno"""
    matricula: int = Field(
        ...,
        description="Matrícula do aluno",
        example=1
    )

class ContatoInstrutorCreate(ContatoBase):
    """Modelo para criação de contato de instrutor"""
    cref: int = Field(
        ...,
        description="CREF do instrutor",
        example=123456
    )

class ContatoUpdate(ModeloBase):
    """Modelo para atualização de contato"""
    telefone: Optional[str] = Field(
        None,
        max_length=15,
        pattern=r"^\(\d{2}\)\d{4,5}-\d{4}$"
    )
    email: Optional[EmailStr] = None

# Modelos para Aluno
class AlunoBase(ModeloBase):
    """Modelo base para Aluno"""
    cpf: str = Field(
        ..., 
        min_length=11,
        max_length=11,
        pattern=r"^\d{11}$",
        description="CPF (apenas números)",
        example="12345678901"
    )
    nome: str = Field(
        ..., 
        max_length=45,
        description="Nome completo do aluno",
        example="João da Silva"
    )
    sexo: SexoEnum = Field(
        ...,
        description="Sexo do aluno (M/F)",
        example="M"
    )
    data_nascimento: date = Field(
        ..., 
        description="Data de nascimento",
        example="1990-01-01"
    )
    data_matricula: date = Field(
        ...,
        description="Data da matrícula",
        example="2024-01-01"
    )
    codigo_plano: int = Field(
        ...,
        description="Código do plano",
        example=1
    )

class AlunoCreate(AlunoBase):
    """Modelo para criação de aluno"""
    contato: ContatoBase

class AlunoUpdate(ModeloBase):
    """Modelo para atualização de aluno"""
    cpf: Optional[str] = None
    nome: Optional[str] = None
    sexo: Optional[SexoEnum] = None
    data_nascimento: Optional[date] = None
    data_matricula: Optional[date] = None
    codigo_plano: Optional[int] = None
    contato: Optional[ContatoBase] = None

class AlunoResponse(AlunoBase):
    """Modelo para resposta de aluno"""
    matricula: int = Field(..., description="Matrícula do aluno", example=1)
    contato: Optional[ContatoBase] = None

# Modelos para Bioimpedância
class BioimpedanciaBase(ModeloBase):
    """Modelo base para Bioimpedância"""
    matricula: int = Field(
        ...,
        description="Matrícula do aluno",
        example=1
    )
    peso: float = Field(
        ..., 
        gt=0, 
        le=300,
        description="Peso em kg",
        example=70.5
    )
    altura: float = Field(
        ..., 
        gt=0, 
        le=3,
        description="Altura em metros",
        example=1.75
    )
    tmb: int = Field(
        ..., 
        gt=0,
        description="Taxa Metabólica Basal",
        example=1800
    )
    percentual_gordura: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Percentual de gordura corporal",
        example=15.5
    )
    quantidade_agua: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Percentual de água corporal",
        example=60.2
    )

class BioimpedanciaCreate(BioimpedanciaBase):
    """Modelo para criação de medição"""
    pass

class BioimpedanciaUpdate(ModeloBase):
    """Modelo para atualização de medição"""
    peso: Optional[float] = Field(None, gt=0, le=300)
    altura: Optional[float] = Field(None, gt=0, le=3)
    tmb: Optional[int] = Field(None, gt=0)
    percentual_gordura: Optional[float] = Field(None, ge=0, le=100)
    quantidade_agua: Optional[float] = Field(None, ge=0, le=100)

class BioimpedanciaResponse(BioimpedanciaBase):
    """Modelo para resposta de medição"""
    pass

# Modelos para Instrutor
class InstrutorBase(ModeloBase):
    cpf: str = Field(
        ..., 
        min_length=11, 
        max_length=11,
        pattern=r"^\d{11}$",
        description="CPF do instrutor (apenas números)",
        example="12345678901"
    )
    nome: str = Field(
        ..., 
        max_length=30,
        description="Nome completo do instrutor",
        example="José Santos"
    )
    data_nascimento: date = Field(
        ...,
        description="Data de nascimento",
        example="1985-01-01"
    )
    data_admissao: date = Field(
        ...,
        description="Data de admissão",
        example="2024-01-01"
    )
    turno: TurnoEnum = Field(
        ...,
        description="Turno de trabalho",
        example="Manhã"
    )

class InstrutorCreate(InstrutorBase):
    """Modelo para criação de instrutor"""
    cref: int = Field(
        ..., 
        description="Número do CREF",
        example=123456
    )
    contato: ContatoBase

class InstrutorUpdate(ModeloBase):
    """Modelo para atualização de instrutor"""
    cpf: Optional[str] = Field(
        None,
        min_length=11,
        max_length=11,
        pattern=r"^\d{11}$",
        description="CPF do instrutor (apenas números)"
    )
    nome: Optional[str] = Field(
        None,
        max_length=30,
        description="Nome do instrutor"
    )
    data_nascimento: Optional[date] = Field(
        None,
        description="Data de nascimento"
    )
    data_admissao: Optional[date] = Field(
        None,
        description="Data de admissão"
    )
    turno: Optional[TurnoEnum] = Field(
        None,
        description="Turno de trabalho"
    )
    contato: Optional[ContatoBase] = Field(
        None,
        description="Informações de contato"
    )

class InstrutorResponse(ModeloBase):
    """Modelo para resposta de instrutor"""
    cref: int
    cpf: str
    nome: str
    data_nascimento: date
    data_admissao: date
    turno: str
    contato: Optional[ContatoBase] = None

    @classmethod
    def from_tuple(cls, row: Tuple) -> "InstrutorResponse":
        """Converte uma tupla do banco em um objeto InstrutorResponse"""
        return cls(
            cref=row[0],
            cpf=row[1],
            nome=row[2],
            data_nascimento=row[3],
            data_admissao=row[4],
            turno=row[5],
            contato=ContatoBase(
                telefone=row[6],
                email=row[7]
            ) if row[6] or row[7] else None
        )

# Modelos para Turma
class TurmaBase(ModeloBase):
    """Modelo base para Turma"""
    nome_atividade: str = Field(
        ..., 
        max_length=45,
        description="Nome da atividade",
        example="Musculação"
    )
    quantidade_vagas: int = Field(
        ..., 
        gt=0,
        description="Número de vagas disponíveis",
        example=20
    )
    turno: TurnoEnum = Field(
        ...,
        description="Turno da atividade",
        example="Manhã"
    )
    cref: int = Field(
        ...,
        description="CREF do instrutor responsável",
        example=123456
    )

class TurmaCreate(TurmaBase):
    """Modelo para criação de turma"""
    pass

class TurmaUpdate(ModeloBase):
    """Modelo para atualização de turma"""
    nome_atividade: Optional[str] = Field(
        None, 
        max_length=45,
        description="Nome da atividade"
    )
    quantidade_vagas: Optional[int] = Field(
        None, 
        gt=0,
        description="Número de vagas"
    )
    turno: Optional[TurnoEnum] = Field(
        None,
        description="Turno da atividade"
    )
    cref: Optional[int] = Field(
        None,
        description="CREF do instrutor"
    )

class TurmaResponse(TurmaBase):
    """Modelo para resposta de turma"""
    id_turma: int = Field(..., description="ID único da turma")
    instrutor: InstrutorResponse = Field(..., description="Dados do instrutor responsável")
    alunos: List[int] = Field(default=[], description="Lista de matrículas dos alunos")

    @classmethod
    def from_tuple(cls, row: Tuple) -> "TurmaResponse":
        """Converte uma tupla do banco em um objeto TurmaResponse"""
        return cls(
            id_turma=row[0],
            nome_atividade=row[1],
            quantidade_vagas=row[2],
            turno=row[3],
            cref=row[4],
            instrutor=InstrutorResponse(
                cref=row[4],
                cpf=row[5],
                nome=row[6],
                data_nascimento=row[7],
                data_admissao=row[8],
                turno=row[9],
                contato=ContatoBase(
                    telefone=row[10],
                    email=row[11]
                ) if row[10] or row[11] else None
            ),
            alunos=row[12] if row[12] else []
        )

# Modelos para Matrícula em Turma
class MatriculaTurmaCreate(ModeloBase):
    """Modelo para matrícula em turma"""
    id_turma: int = Field(
        ...,
        description="ID da turma",
        example=1
    )
    matricula: int = Field(
        ...,
        description="Matrícula do aluno",
        example=1
    )

class MatriculaTurmaResponse(MatriculaTurmaCreate):
    """Modelo para resposta de matrícula em turma"""
    data_matricula: date = Field(
        ...,
        description="Data da matrícula na turma",
        example="2024-01-01"
    )

# Modelos para Respostas HTTP
class MessageResponse(ModeloBase):
    """Modelo para mensagens de resposta"""
    message: str = Field(
        ...,
        description="Mensagem de resposta",
        example="Operação realizada com sucesso"
    )

class ErrorResponse(ModeloBase):
    """Modelo para mensagens de erro"""
    detail: str = Field(
        ...,
        description="Detalhes do erro",
        example="Erro ao processar requisição"
    )

class RelatorioAlunoResponse(ModeloBase):
    """Modelo para resposta do relatório de alunos"""
    matricula: int
    nome_aluno: str
    cpf: str
    idade: int
    data_matricula: date
    nome_plano: str
    valor_plano: float

    class Config:
        json_schema_extra = {
            "example": {
                "matricula": 1,
                "nome_aluno": "João Silva",
                "cpf": "12345678901",
                "idade": 25,
                "data_matricula": "2024-01-01",
                "nome_plano": "Premium",
                "valor_plano": 99.90
            }
        }