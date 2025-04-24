from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/v1/")
    assert response.status_code == 404

def test_create_plano():
    response = client.post(
        "/api/v1/planos/",
        json={
            "nome_plano": "Plano Teste",
            "preco": 99.90,
            "descricao": "Plano para teste"
        }
    )
    assert response.status_code == 201
    assert response.json()["nome_plano"] == "Plano Teste"