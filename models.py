"""Models mapeados para as tabelas do Supabase (criadas pelas migrations).

As tabelas NÃO são criadas pelo SQLAlchemy (sem db.create_all()): a fonte da
verdade do schema são os arquivos em supabase/migrations/.
"""

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()

# Código usado pelas rotas/templates  ->  código gravado no banco
PERFIL_APP_PARA_BANCO = {
    "aluno": "aluno",
    "coordenador": "coordenador",
    "avaliador": "avaliador_mec",
    "admin": "admin",
}
PERFIL_BANCO_PARA_APP = {banco: app for app, banco in PERFIL_APP_PARA_BANCO.items()}
PERFIS_VALIDOS = list(PERFIL_APP_PARA_BANCO)


class Perfil(db.Model):
    __tablename__ = "perfis"

    id = db.Column(db.SmallInteger, primary_key=True)
    codigo = db.Column(db.Text, unique=True, nullable=False)
    nome = db.Column(db.Text, nullable=False)

    @classmethod
    def por_codigo_app(cls, codigo_app: str) -> "Perfil":
        return cls.query.filter_by(codigo=PERFIL_APP_PARA_BANCO[codigo_app]).one()


class Usuario(db.Model, UserMixin):
    """Espelho de auth.users. A senha fica no Supabase Auth, não aqui."""

    __tablename__ = "usuarios"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    nome = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    perfil_id = db.Column(db.SmallInteger, db.ForeignKey("perfis.id"), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.true())

    perfil_rel = db.relationship(Perfil, lazy="joined")

    @property
    def perfil(self) -> str:
        """Código do perfil no formato usado pelo app ('avaliador', não 'avaliador_mec')."""
        return PERFIL_BANCO_PARA_APP[self.perfil_rel.codigo]

    @property
    def is_active(self) -> bool:
        return self.ativo

    @classmethod
    def query_por_perfil(cls, codigo_app: str):
        return cls.query.join(Perfil).filter(Perfil.codigo == PERFIL_APP_PARA_BANCO[codigo_app])


class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"

    id = db.Column(db.BigInteger, primary_key=True)
    titulo = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    status = db.Column(db.Text, nullable=False, server_default="Agendada")


class Participacao(db.Model):
    __tablename__ = "participacoes"

    id = db.Column(db.BigInteger, primary_key=True)
    aluno_id = db.Column(UUID(as_uuid=True), db.ForeignKey("usuarios.id"), nullable=False)
    avaliacao_id = db.Column(db.BigInteger, db.ForeignKey("avaliacoes.id"), nullable=False)
    respondida = db.Column(db.Boolean, nullable=False, server_default=db.false())
