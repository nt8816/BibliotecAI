# BibliotecAI - Sistema de Gestão de Biblioteca

## Visão Geral
BibliotecAI é um sistema de gestão de biblioteca com frontend em HTML/CSS/JS e backend em Node.js conectado ao Supabase Postgres.

## Estrutura do Projeto
```
.
├── login.html              # Tela de autenticação
├── index.html              # Redirecionamento para login
├── dashboard.html          # Painel principal com resumo de estatísticas
├── livros.html             # Gestão de livros (CRUD)
├── usuarios.html           # Gestão de usuários (CRUD)
├── emprestimos.html        # Gestão de empréstimos
├── relatorios.html         # Relatórios e geração de PDF
├── app.js                  # Funções compartilhadas (auth, API)
├── supabase-config.js      # URL/chaves públicas do Supabase
├── livros-backend.js       # Lógica para gestão de livros
├── usuarios-backend.js     # Lógica para gestão de usuários
├── dashboard-backend.js    # Lógica do dashboard
├── relatorios.js           # Lógica para relatórios e PDF
├── sidebar-fix.js          # Ajustes de navegação
├── style.css               # Estilos customizados
├── server.js               # Backend Node.js/Express
├── package.json            # Dependências Node.js
└── SUPABASE_SETUP.md       # Guia de configuração Supabase
```

## Stack
- Frontend: HTML5, CSS3, JavaScript
- Backend: Node.js + Express
- Banco: Supabase Postgres
- Auth: JWT + bcrypt

## Como rodar
1. Configure variáveis:
```bash
export SUPABASE_DB_URL="postgresql://postgres:<SENHA>@db.<PROJECT_REF>.supabase.co:5432/postgres"
export SUPABASE_URL="https://dhjkjwkitufsvhlhcsec.supabase.co"
export SUPABASE_ANON_KEY="<SUA_ANON_KEY_PUBLICA>"
export JWT_SECRET_KEY="troque-por-um-segredo-forte"
```

2. Instale dependências:
```bash
npm install
```

3. Inicie:
```bash
npm run start
```

4. Acesse:
- http://localhost:5000

## Credenciais iniciais
- Gestor: `admin`
- Senha: `admin`

## Endpoints
- `POST /api/login`
- `GET/POST /api/livros`
- `PUT/DELETE /api/livros/:livroId`
- `GET/POST /api/usuarios`
- `PUT/DELETE /api/usuarios/:usuarioId`
- `GET/POST /api/emprestimos`
- `POST /api/emprestimos/:emprestimoId/devolver`
- `GET /api/stats`
- `GET /api/health`
