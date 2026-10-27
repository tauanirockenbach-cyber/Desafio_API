# API de sorvetes

API Flask para cadastrar e consultar fabricantes e sorvetes. Por padrão, os
dados ficam em um banco SQLite local; não é necessário instalar ou iniciar o
Docker.

## Requisitos

- Python 3.10 ou superior
- PowerShell no Windows

## Executar no Windows

Abra o PowerShell na pasta do projeto e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

Se o PowerShell bloquear a ativação do ambiente virtual, use o Python dele
diretamente, sem ativar:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

A API ficará disponível em `http://127.0.0.1:5000`. Para conferir se iniciou
corretamente, acesse `http://127.0.0.1:5000/health`; a resposta esperada é:

```json
{"status": "ok", "database": "connected"}
```

O SQLite é criado automaticamente em `instance/sorvetes.db` quando a aplicação
inicia. Se existir um arquivo `.env` com `DATABASE_URL` apontando para outro
banco, remova ou altere essa configuração para usar o SQLite local.

## Endpoints

### Fabricantes

```http
GET /fabricantes
POST /fabricantes
Content-Type: application/json

{"nome": "Gelados da Serra"}
```

### Sorvetes

```http
GET /sorvetes
POST /sorvetes
Content-Type: application/json

{
  "nome": "Picolé",
  "sabor": "Morango",
  "preco": 5,
  "fabricante_id": "<UUID retornado por POST /fabricantes>"
}
```

`preco` deve ser um número inteiro não negativo. Cada sorvete precisa estar
associado a um fabricante existente.

Exemplo para cadastrar um fabricante no PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/fabricantes `
  -ContentType "application/json" -Body '{"nome":"Gelados da Serra"}'
```
