from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from src.routes.api import router

# Definindo os metadados das tags para o Swagger
tags_metadata = [
    {
        "name": "Planos",
        "description": "Gerenciamento de planos da academia",
    },
    {
        "name": "Alunos",
        "description": "Operações relacionadas aos alunos",
    },
    {
        "name": "Bioimpedância",
        "description": "Medições e acompanhamento físico",
    },
    {
        "name": "Instrutores",
        "description": "Gerenciamento de instrutores",
    },
    {
        "name": "Turmas",
        "description": "Controle de turmas e atividades",
    },
    {
        "name": "Relatórios",
        "description": "Relatórios e análises do sistema",
    }
]

description = """
# GIM - Sistema de Gerenciamento de Academia

## Funcionalidades

### 🏋️ Planos
* Cadastro e gerenciamento de planos
* Definição de valores e benefícios
* Controle de matrículas

### 👥 Alunos
* Cadastro completo de alunos
* Gestão de matrículas
* Histórico de pagamentos
* Acompanhamento de frequência

### 📊 Bioimpedância
* Registro de medições
* Acompanhamento de evolução
* Relatórios detalhados
* Histórico completo

### 👨‍🏫 Instrutores
* Cadastro de profissionais
* Controle de horários
* Gestão de turmas
* Avaliações

### 📅 Turmas
* Criação e gestão de turmas
* Controle de vagas
* Agendamentos
* Frequência

## Notas
* Autenticação necessária para todas as rotas (exceto documentação)
* Dados sensíveis são protegidos
* Suporte a múltiplos formatos de resposta
"""

app = FastAPI(
    title="GIM - Sistema de Academia",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,  # Adicionando as tags ao FastAPI
    terms_of_service="http://gim.com.br/terms/",
    contact={
        "name": "Suporte GIM",
        "url": "http://gim.com.br/support",
        "email": "suporte@gim.com.br",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)