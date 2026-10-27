from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db


class Fabricante(db.Model):
    # Nome exato da tabela que vai ser criada lá no banco de dados
    __tablename__ = "fabricantes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Nome do fabricante é obrigatório (nullable=False) e não pode repetir no banco (unique=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Cria uma relação virtual para buscar todos os sorvetes desse fabricante facilmente
    sorvetes: Mapped[list["Sorvete"]] = relationship(back_populates="fabricante")

    # Método para transformar a classe em um dicionário Python comum (útil para APIs)
    def dict(self):
        return {
            "id": str(self.id),
            "nome": self.nome,
            # Já roda um loop e serializa todos os sorvetes vinculados a ele também
            "sorvetes": [sorvete.dict() for sorvete in self.sorvetes],
        }


class Sorvete(db.Model):
    __tablename__ = "sorvetes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    sabor: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Guardamos o preço como inteiro (geralmente centavos) para evitar problemas de arredondamento de float
    preco: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Chave estrangeira que aponta diretamente para o ID do fabricante na tabela de fabricantes
    fabricante_id: Mapped[str] = mapped_column(String(36), ForeignKey("fabricantes.id"), nullable=False)
    
    # Cria o link inverso para que o sorvete consiga acessar as propriedades do seu fabricante (ex: sorvete.fabricante.nome)
    fabricante: Mapped[Fabricante] = relationship(back_populates="sorvetes")

    # Outro método auxiliar de conversão para dicionário, focando apenas nos dados do próprio sorvete
    def as_dict(self):
        return {
            "id": str(self.id),
            "nome": self.nome,
            "sabor": self.sabor,
            "preco": self.preco,
            "fabricante_id": str(self.fabricante_id),
        }
