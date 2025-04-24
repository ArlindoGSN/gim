# GIM - Sistema de Gerenciamento de Academia

API RESTful construída com FastAPI para gerenciamento de academia.

## Estrutura do Projeto

```
gim
├── src
│   ├── app.py
│   ├── database
│   │   ├── connection.py
│   │   └── queries.py
│   ├── controllers
│   │   └── routes.py
│   └── utils
│       └── helpers.py
├── tests
│   └── test_app.py
├── requirements.txt
└── README.md
```

## Tecnologias Utilizadas

- FastAPI
- Pydantic
- PostgreSQL
- Uvicorn

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd gim
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para iniciar a aplicação, execute o seguinte comando:
```
python src/app.py
```

## Testes

Para executar os testes, utilize:
```
python -m unittest discover -s tests
``` 

## Contribuição

Sinta-se à vontade para contribuir com melhorias ou correções.