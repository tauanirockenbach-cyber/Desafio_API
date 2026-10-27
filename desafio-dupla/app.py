import os
from uuid import UUID
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from db import db
from flask_migrate import Migrate
from models.book import Fabricante, Sorvete

def create_app(test_config: dict[str, object] | None = None) -> Flask:
    # Carrega as variáveis de ambiente do arquivo .env (senhas, urls de banco, etc)
    load_dotenv()
    
    app = Flask(__name__)
    
    # Desativa o rastreamento de modificações do SQLAlchemy para economizar memória
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Descobre onde o arquivo atual está e cria uma pasta 'instance' para o banco SQLite se ela não existir
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    
    # Define o SQLite local como banco padrão caso ninguém passe outra URL no .env
    default_database_url = f"sqlite:///{os.path.join(instance_dir, 'sorvetes.db')}"
    configured_database_url = os.getenv("DATABASE_URL")
    
    database_url = default_database_url
    
    # Se houver uma URL configurada no ambiente e ela for do SQLite, a gente usa ela
    if configured_database_url:
        candidate = configured_database_url.strip()
        if candidate.lower().startswith("sqlite"):
            database_url = candidate
            
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    # Se o app estiver rodando em modo de teste, a gente sobrescreve as configurações normais
    if test_config is not None:
        app.config.update(test_config)
        
    # Inicializa o banco de dados e as migrações no Flask
    db.init_app(app)
    Migrate(app, db)
    
    # Cria as tabelas do banco automaticamente se elas ainda não existirem
    with app.app_context():
        db.create_all()

    # Rota básica de saúde só para checar se o servidor e o banco estão de pé
    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}, 200

    # Lista todos os fabricantes ordenados por nome em ordem alfabética
    @app.get("/fabricantes")
    def list_fabricantes():
        fabricantes = Fabricante.query.order_by(Fabricante.nome).all()
        return jsonify([{"id": str(item.id), "nome": item.nome} for item in fabricantes])

    # Cria um novo fabricante no banco de dados
    @app.post("/fabricantes")
    def create_fabricante():
        payload = request.get_json(silent=True)
        nome = payload.get("nome") if isinstance(payload, dict) else None
        
        # Garante que o nome foi enviado e não está em branco
        if not isinstance(nome, str) or not nome.strip():
            return {"error": "Informe um nome de fabricante."}, 400
            
        fabricante = Fabricante(nome=nome.strip())
        db.session.add(fabricante)
        
        try:
            db.session.commit()
        except IntegrityError:
            # Se der erro de nome duplicado (Unique Constraint), desfaz a alteração e avisa o cliente
            db.session.rollback()
            return {"error": "Já existe um fabricante com esse nome."}, 409
            
        return jsonify({"id": str(fabricante.id), "nome": fabricante.nome}), 201

    # Lista todos os sorvetes cadastrados no sistema
    @app.get("/sorvetes")
    def list_sorvetes():
        sorvetes = Sorvete.query.order_by(Sorvete.nome).all()
        return jsonify([serialize_sorvete(item) for item in sorvetes])

    # Cadastra um novo sorvete vinculando ele a um fabricante
    @app.post("/sorvetes")
    def create_sorvete():
        payload = request.get_json(silent=True)
        
        # Valida se o corpo da requisição veio no formato JSON correto
        if not isinstance(payload, dict):
            return {"error": "O corpo da requisição deve ser um objeto JSON."}, 400
            
        nome = payload.get("nome")
        sabor = payload.get("sabor")
        preco = payload.get("preco")
        fabricante_id = payload.get("fabricante_id")
        
        # Bateria de validações dos campos obrigatórios
        if not isinstance(nome, str) or not nome.strip():
            return {"error": "Informe o nome do sorvete."}, 400
            
        if not isinstance(sabor, str) or not sabor.strip():
            return {"error": "Informe o sabor do sorvete."}, 400
            
        # O preço precisa ser um número inteiro (geralmente centavos) e não pode ser negativo
        if isinstance(preco, bool) or not isinstance(preco, int) or preco < 0:
            return {"error": "O preço deve ser um número inteiro não negativo."}, 400
            
        if not isinstance(fabricante_id, str):
            return {"error": "Informe um UUID válido em fabricante_id."}, 400
            
        # Tenta converter a string do ID para o formato UUID real
        try:
            parsed_fabricante_id = UUID(fabricante_id)
        except (TypeError, ValueError):
            return {"error": "Informe um UUID válido em fabricante_id."}, 400
            
        # Procura o fabricante no banco. Se não achar, não faz sentido cadastrar o sorvete
        fabricante = db.session.get(Fabricante, str(parsed_fabricante_id))
        if fabricante is None:
            return {"error": "Fabricante não encontrado."}, 404
            
        # Salva o sorvete com as informações validadas
        sorvete = Sorvete(
            nome=nome.strip(),
            sabor=sabor.strip(),
            preco=preco,
            fabricante=fabricante,
        )
        db.session.add(sorvete)
        db.session.commit()
        
        return jsonify(serialize_sorvete(sorvete)), 201

    return app

# Cria a instância global do aplicativo Flask
app = create_app()

# Função auxiliar para transformar o objeto do banco de dados em um dicionário/JSON amigável
def serialize_sorvete(sorvete: Sorvete) -> dict[str, str | int]:
    return {
        "id": str(sorvete.id),
        "nome": sorvete.nome,
        "sabor": sorvete.sabor,
        "preco": sorvete.preco,
        "fabricante_id": str(sorvete.fabricante_id),
        "fabricante": sorvete.fabricante.nome, # Puxa o nome direto da relação com o fabricante
    }

# Roda o servidor local em modo de desenvolvimento se o script for executado direto
if __name__ == "__main__":
    app.run(debug=True)
