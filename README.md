# Portal CPA — Faculdade Impacta

Portal web da **Comissão Própria de Avaliação (CPA)** da Faculdade Impacta. Ele centraliza, em um só lugar:

- **Transparência pública**: Mural de Devolutivas, Relatórios/Boletins em PDF e página de Contato, sem login.
- **Dashboards analíticos restritos**: painéis do Looker Studio (antigo Google Data Studio), exibidos por `<iframe>` conforme o perfil do usuário autenticado.
- **Painel administrativo**: a CPA gerencia dashboards, devolutivas, documentos e usuários sem alterar o código.

> **Status:** Fase 1 (requisitos) concluída. O banco de dados (Fase 2) está implementado em `supabase/`. A aplicação Flask e o front-end são os próximos passos.

---

## Sumário

1. [Visão geral](#visão-geral)
2. [Perfis e permissões](#perfis-e-permissões)
3. [Stack tecnológica](#stack-tecnológica)
4. [Arquitetura](#arquitetura)
5. [Estrutura do repositório](#estrutura-do-repositório)
6. [Banco de dados](#banco-de-dados)
7. [Segurança](#segurança)
8. [Configuração e execução](#configuração-e-execução)
9. [Requisitos](#requisitos)
10. [Roadmap](#roadmap)
11. [Contribuindo](#contribuindo)

---

## Visão geral

| Área | Quem acessa | O que faz |
|---|---|---|
| Página inicial | Todos | Apresentação institucional da CPA |
| Mural de Devolutivas | Todos (leitura) / Admin (gestão) | Demanda, área responsável, ação executada, status e data |
| Relatórios e Boletins | Todos (download) / Admin (upload) | PDFs organizados por ano e categoria |
| Contato | Todos | Informações da CPA e links para Google Chat e Google Meet |
| Dashboards | Usuários logados, por perfil | Painéis do Looker Studio incorporados |
| Gestão de usuários | Admin | Definir perfis e ativar ou desativar usuários |

### Dashboards

| Código | Nome | Conteúdo | Perfis |
|---|---|---|---|
| DASH-01 | Pesquisa Institucional CPA | Satisfação geral, infraestrutura, laboratórios, biblioteca, atendimento | Aluno, Coordenador, Avaliador MEC, Admin |
| DASH-02 | Avaliação Docente por Curso | Didática, plano de ensino, feedback docente | Coordenador, Avaliador MEC, Admin |
| DASH-03 | Acompanhamento de Egressos | Empregabilidade, área de atuação, faixa salarial, continuidade acadêmica | Coordenador, Avaliador MEC, Admin |

As URLs atuais são **links de demonstração**. O Admin as substitui pelo painel quando a CPA enviar os links oficiais.

### Documentos

| Código | Categoria | Formato |
|---|---|---|
| DOC-01 | Relatórios de Autoavaliação | PDF |
| DOC-02 | Boletins Informativos | PDF |

---

## Perfis e permissões

O **Visitante** não é um perfil cadastrado: é o usuário sem login (papel `anon`). Os outros quatro são linhas da tabela `perfis`.

| Funcionalidade | Visitante | Aluno | Coordenador | Avaliador MEC | Admin |
|---|:-:|:-:|:-:|:-:|:-:|
| Página inicial | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mural de Devolutivas | Leitura | Leitura | Leitura | Leitura | Leitura + CRUD |
| Relatórios e Boletins | Baixar | Baixar | Baixar | Baixar | Baixar + Upload/Excluir |
| Contato | ✅ | ✅ | ✅ | ✅ | ✅ |
| DASH-01 Pesquisa CPA | ❌ | ✅ | ✅ | ✅ | ✅ + gerenciar link |
| DASH-02 Avaliação Docente | ❌ | ❌ | ✅ | ✅ | ✅ + gerenciar link |
| DASH-03 Egressos | ❌ | ❌ | ✅ | ✅ | ✅ + gerenciar link |
| Gestão de usuários | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Stack tecnológica

| Camada | Tecnologia | Papel |
|---|---|---|
| Front-end | **HTML5, CSS3, JavaScript** | Páginas responsivas renderizadas pelo Flask (templates Jinja2) |
| Back-end | **Python 3 + Flask** | Rotas, sessão, controle de acesso por perfil e painel administrativo |
| Banco de dados | **PostgreSQL (Supabase)** | Dados do portal, com Row Level Security |
| Autenticação | **Supabase Auth** | Login por e-mail e senha, hash bcrypt, emissão de JWT |
| Arquivos | **Supabase Storage** | Bucket `documentos`, somente PDF |
| Dashboards | **Looker Studio** | Painéis incorporados por `<iframe>` |
| Bibliotecas Python | `supabase`, `python-dotenv`, `PyJWT` | Cliente da API, leitura do `.env`, validação de token |
| Versionamento | **Git + GitHub** | Código, migrations e documentação (RNF05) |

### Por que Supabase em vez de MySQL

A Fase 1 previa **Flask + MySQL** (RNF06). O Flask, o Python e o front em HTML/CSS/JS foram mantidos; **o MySQL foi substituído pelo PostgreSQL do Supabase**, porque ele já entrega pronto o que o projeto precisaria construir à mão:

| Necessidade (Fase 1) | Com MySQL | Com Supabase |
|---|---|---|
| Senha com hash (RNF02) | Implementar no Flask | Supabase Auth (bcrypt) |
| Consultas parametrizadas (RNF02) | Cuidar em cada query | API do Supabase já parametriza |
| Filtrar dashboards por perfil (RF02, RN02) | Só no Flask | No Flask **e** no banco (RLS) |
| Upload de PDF (RF08, RN04) | Salvar no servidor | Storage com filtro de tipo e tamanho |
| Hospedagem do banco | Configurar servidor | Gerenciada |

Os requisitos funcionais continuam valendo integralmente. Recomenda-se registrar a troca em ata e atualizar o texto do RNF06.

---

## Arquitetura

```
Navegador (HTML/CSS/JS)
        │  HTTP
        ▼
Flask (Python) ─────────────────────────────┐
  • rotas públicas e protegidas             │
  • sessão com o JWT do usuário             │
  • decide menus e páginas pelo perfil      │
        │                                    │
        │ supabase-py                        │ <iframe>
        ▼                                    ▼
Supabase                              Looker Studio
  • Auth (login, JWT)
  • PostgreSQL + RLS
  • Storage (PDFs)
```

**Fluxo de login:**

1. O usuário envia e-mail e senha para o Flask.
2. O Flask chama o Supabase Auth, que devolve um JWT.
3. O Flask valida o token pela `SUPABASE_JWKS_URL` e guarda a sessão.
4. As consultas são feitas **com o token do usuário**, então a RLS do banco filtra os dados automaticamente.

**Duas chaves, dois usos:**

- `SUPABASE_PUBLISHABLE_KEY` — chave pública. Usada nas consultas normais, sempre junto do token do usuário, respeitando a RLS.
- `SUPABASE_SECRET_KEY` — chave secreta, **ignora a RLS**. Fica só no servidor, para tarefas administrativas pontuais. Nunca vai para o navegador.

Assim há **defesa em dupla camada**: mesmo que uma rota do Flask esqueça de checar o perfil, o banco recusa o acesso.

---

## Estrutura do repositório

```
cpa-developer/
├── README.md
├── LICENSE
├── .env.example            # modelo das variáveis de ambiente
├── .env                    # valores reais (NÃO versionado)
├── .gitignore
├── docs/
│   ├── README.md                 # índice da documentação
│   ├── plano-do-projeto.md       # 6 fases, 24 tarefas, progresso
│   ├── setup-supabase.md         # guia de configuração do Supabase
│   └── fase-1-requisitos/
│       ├── 01-ata-reuniao.md
│       ├── 02-perfis-e-permissoes.md
│       ├── 03-catalogo-dashboards-documentos.md
│       └── 04-requisitos.md
└── supabase/
    ├── migrations/
    │   └── 20261116000000_schema_inicial.sql
    └── seed.sql
```

Estrutura planejada para a aplicação Flask (Fase 3):

```
app/
├── __init__.py          # create_app(), carrega o .env
├── supabase_client.py   # clientes Supabase (público e admin)
├── auth.py              # login, logout, decorators @login_required / @perfil_required
├── routes/
│   ├── publico.py       # home, devolutivas, relatórios, contato
│   ├── dashboards.py    # área logada
│   └── admin.py         # painel administrativo
├── templates/           # Jinja2 (HTML)
└── static/              # CSS, JS, imagens
requirements.txt
```

---

## Banco de dados

### Modelo

```
auth.users (Supabase Auth)
     │ 1:1  (trigger on_auth_user_created)
     ▼
usuarios ──N:1──► perfis
     │
     ├─ updated_by ──► dashboards ◄──N:M──► perfis   (via dashboard_perfis)
     ├─ created_by ──► devolutivas
     └─ created_by ──► documentos ──(storage_path)──► Storage: bucket "documentos"
```

| Tabela | Função |
|---|---|
| `perfis` | Domínio fixo: `aluno`, `coordenador`, `avaliador_mec`, `admin` |
| `usuarios` | Espelho de `auth.users` com nome, e-mail, perfil e `ativo`. **Sem coluna de senha** |
| `dashboards` | Código, nome, descrição, `url_embed`, `ativo`, `ordem` |
| `dashboard_perfis` | Quais perfis acessam cada dashboard (N:M) |
| `devolutivas` | Título, área responsável, ação, status (`planejado` / `em_andamento` / `concluido`), data |
| `documentos` | Metadados do PDF: título, descrição, categoria, ano, `storage_path` |

### Funções e triggers

| Item | O que faz |
|---|---|
| `perfil_atual()` | Código do perfil do usuário logado (ou `null` se inativo) |
| `is_admin()` | Atalho booleano usado nas policies |
| `set_updated_at()` | Atualiza `updated_at` em cada `UPDATE` |
| `handle_new_user()` | Todo novo cadastro no Auth vira **aluno** automaticamente |

### Regras de acesso (RLS)

| Tabela | Visitante | Usuário logado | Admin |
|---|---|---|---|
| `perfis` | — | leitura | — |
| `usuarios` | sem acesso | só a própria linha | lê e atualiza todas |
| `dashboards` | sem acesso | ativos do seu perfil; Avaliador MEC vê todos os ativos | tudo |
| `dashboard_perfis` | sem acesso | — | tudo |
| `devolutivas` | leitura | leitura | tudo |
| `documentos` | leitura | leitura | tudo |
| Storage `documentos` | leitura | leitura | upload, update, delete |

Admin e Avaliador MEC veem todos os dashboards **por regra na policy** (RN03), sem precisar de linhas em `dashboard_perfis`.

---

## Segurança

- **Sem escalada de privilégio no cadastro**: o perfil nunca vem dos dados enviados pelo cliente. Todo novo usuário é `aluno`; só um admin promove.
- **Sem auto-promoção**: não existe policy que permita ao usuário editar a própria linha em `usuarios`.
- **Usuário inativo** perde todas as permissões.
- **`url_embed` restrita** aos domínios `lookerstudio.google.com` e `datastudio.google.com`.
- **Storage**: somente `application/pdf`, até 20 MB (RN04).
- **Funções `security definer`** com `search_path = ''`.
- **Segredos fora do Git**: `.env` está no `.gitignore`. A `SUPABASE_SECRET_KEY` só existe no servidor.

---

## Configuração e execução

### Pré-requisitos

- Python 3.11+
- [Supabase CLI](https://supabase.com/docs/guides/cli) (para aplicar migrations)
- Acesso ao projeto Supabase

### 1. Variáveis de ambiente

```bash
cp .env.example .env
# preencha com os valores do Dashboard > Project Settings
```

| Variável | Uso |
|---|---|
| `SUPABASE_URL` | Endereço da API |
| `SUPABASE_PUBLISHABLE_KEY` | Chave pública (respeita RLS) |
| `SUPABASE_SECRET_KEY` | Chave secreta, só no backend |
| `SUPABASE_JWKS_URL` | Validação dos tokens no Flask |
| `SUPABASE_DB_HOST` / `PORT` / `NAME` / `USER` / `PASSWORD` | Conexão direta ao PostgreSQL |
| `FLASK_SECRET_KEY` | Assinatura da sessão do Flask |

Detalhes da conexão e o que fazer se uma chave vazar: [docs/setup-supabase.md](docs/setup-supabase.md).

### 2. Aplicar o banco

```bash
supabase login
supabase link --project-ref <project-ref>
supabase db push
```

Depois rode `supabase/seed.sql` no **SQL Editor** para criar os dashboards de demonstração.

### 3. Criar o primeiro administrador

1. Dashboard › **Authentication › Users** › crie um usuário.
2. No **SQL Editor**:

```sql
update public.usuarios
set perfil_id = (select id from public.perfis where codigo = 'admin')
where email = 'admin@exemplo.com';
```

### 4. Rodar o Flask (quando a aplicação existir)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  |  source .venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
flask run
```

### Checklist de permissões

- Visitante lê `devolutivas` e `documentos`, mas **não** `dashboards`.
- Aluno vê apenas o DASH-01.
- Coordenador e Avaliador MEC veem os 3 dashboards.
- Aluno **não** consegue alterar `usuarios`.
- Upload de arquivo que não seja PDF é recusado.

---

## Requisitos

### Funcionais

| ID | Resumo | Situação |
|---|---|---|
| RF01 | Login com e-mail institucional e senha | Auth pronto; falta tela e rota Flask |
| RF02 | Controle de acesso por perfil (menus e URL direta) | RLS pronta; faltam decorators Flask |
| RF03 | Dashboards por perfil via iframe | Dados e RLS prontos; falta página |
| RF04 | Admin gerencia URLs dos dashboards | Permissão pronta; falta interface |
| RF05 | Mural público de devolutivas | Tabela e RLS prontas; falta página |
| RF06 | Admin gerencia devolutivas | Permissão pronta; falta interface |
| RF07 | Lista pública de relatórios/boletins | Tabela, Storage e RLS prontos; falta página |
| RF08 | Admin faz upload de PDF | Permissão pronta; falta interface |
| RF09 | Página de contato (Google Chat e Meet) | Pendente |

### Não funcionais

| ID | Requisito | Situação |
|---|---|---|
| RNF01 | Responsividade | Pendente (front) |
| RNF02 | Senhas com hash e consultas parametrizadas | Atendido por Supabase Auth e API |
| RNF03 | Usabilidade, contraste, seções públicas em até 2 cliques | Pendente (front) |
| RNF04 | Chrome, Firefox, Edge e Safari | Pendente (front) |
| RNF05 | Versionamento no GitHub | Em andamento |
| RNF06 | HTML/CSS/JS + Flask + banco relacional | Atualizado: MySQL → PostgreSQL (Supabase) |

### Regras de negócio

- **RN01** — Devolutivas, Relatórios/Boletins e Contato **nunca** exigem login.
- **RN02** — Dashboards de Avaliação Docente e Egressos não podem ser listados nem acessados por alunos.
- **RN03** — Avaliador MEC tem leitura irrestrita dos dashboards ativos, sem edição.
- **RN04** — Apenas PDF é aceito na área de relatórios.

---

## Roadmap

Conforme o [Plano do projeto](docs/plano-do-projeto.md). Requisitos completos em [docs/](docs/README.md).

| Fase | Foco | Situação |
|---|---|---|
| 1 | Levantamento de requisitos | ✅ Concluída |
| 2 | Modelagem e design | 🟡 Banco pronto; faltam protótipos, navegação e validação com a CPA |
| 3 | Portal: ambiente, login, controle de acesso, dashboards, home | ⏳ A fazer |
| 4 | Mural, relatórios, contato, acessibilidade | ⏳ A fazer |
| 5 | Testes funcionais, de usabilidade e de segurança | ⏳ A fazer |
| 6 | Deploy, manual do usuário e treinamento | ⏳ A fazer |

### Próximos passos

1. Aplicar a migration e o seed no projeto Supabase.
2. Criar o esqueleto Flask (`app/`, `requirements.txt`) com leitura do `.env`.
3. Páginas públicas: Home, Mural, Relatórios e Contato.
4. Login, sessão e área logada com dashboards por perfil.
5. Painel administrativo: dashboards, devolutivas, upload de PDF e usuários.
6. Testes por perfil e troca dos links de demonstração pelos oficiais.

---

## Contribuindo

- Código e scripts de banco ficam no GitHub; evidências que não são código (atas, protótipos) ficam no Drive.
- Mudança de banco = **nova migration** em `supabase/migrations/` (`AAAAMMDDHHMMSS_descricao.sql`). Não edite migrations já aplicadas.
- Toda tabela nova precisa de **RLS habilitada** e policies explícitas.
- Nunca commite `.env`, senhas ou a `SUPABASE_SECRET_KEY`.

## Licença

Veja [LICENSE](LICENSE).
