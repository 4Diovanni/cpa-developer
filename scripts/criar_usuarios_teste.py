"""Cria os 4 usuários de teste no Supabase Auth com seus perfis.

Substitui o seed que ficava no app.py (que gravava senhas no SQLite).
Uso, na raiz do projeto:  python -m scripts.criar_usuarios_teste
"""

from uuid import UUID

from app import app
from models import Perfil, Usuario, db
from supabase_client import cliente_admin

USUARIOS_TESTE = [
    ("Aluno Teste", "aluno@portal.com", "aluno", "Aluno@123"),
    ("Coordenador Teste", "coordenador@portal.com", "coordenador", "Coord@123"),
    ("Avaliador Teste", "avaliador@portal.com", "avaliador", "Avaliador@123"),
    ("Administrador CPA", "admin@portal.com", "admin", "Admin@123"),
]


def main():
    with app.app_context():
        admin = cliente_admin()
        for nome, email, perfil, senha in USUARIOS_TESTE:
            if Usuario.query.filter_by(email=email).first():
                print(f"já existe: {email}")
                continue

            resposta = admin.auth.admin.create_user(
                {
                    "email": email,
                    "password": senha,
                    "email_confirm": True,
                    "user_metadata": {"nome": nome},
                }
            )
            usuario = db.session.get(Usuario, UUID(resposta.user.id))
            usuario.perfil_id = Perfil.por_codigo_app(perfil).id
            db.session.commit()
            print(f"criado: {email} ({perfil})")


if __name__ == "__main__":
    main()
