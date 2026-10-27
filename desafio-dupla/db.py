from flask_sqlalchemy import SQLAlchemy

# Cria a instância global do SQLAlchemy. 
# Fazemos isso aqui em um arquivo separado para evitar problemas de importação
# quando os modelos e o arquivo principal do app precisarem usar o banco.
db = SQLAlchemy()
