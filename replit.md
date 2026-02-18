# BibliotecAI - Sistema de Gestão de Biblioteca

## Visão Geral
BibliotecAI é um sistema de gestão de biblioteca desenvolvido em HTML, CSS e JavaScript puro. O sistema permite gerenciar livros, usuários (alunos e professores) e gerar relatórios em PDF.

## Estrutura do Projeto
```
.
├── login.html              # Tela de autenticação
├── index.html              # Redirecionamento para login
├── dashboard.html          # Painel principal com resumo de estatísticas
├── livros.html             # Gestão de livros (CRUD)
├── usuarios.html           # Gestão de usuários (CRUD)
├── emprestimos.html        # Gestão de empréstimos (NOVO)
├── relatorios.html         # Relatórios e geração de PDF
├── app.js                  # Funções compartilhadas (auth, API)
├── livros-backend.js       # Lógica para gestão de livros
├── usuarios-backend.js     # Lógica para gestão de usuários
├── dashboard-backend.js    # Lógica do dashboard
├── relatorios.js           # Lógica para relatórios e PDF
├── sidebar-fix.js          # Adiciona menu de empréstimos dinamicamente
├── style.css               # Estilos customizados
├── server.py               # Backend Flask com APIs REST
└── SUPABASE_SETUP.md       # Guia de configuração Supabase
```

## Tecnologias Utilizadas
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Flask (Python)
- **Banco de Dados**: Supabase Postgres
- **Autenticação**: JWT (JSON Web Tokens)
- **Frameworks CSS**: TailwindCSS (via CDN)
- **Ícones**: Font Awesome 6.4.0
- **Fontes**: Google Fonts (Nunito)
- **Bibliotecas JS**:
  - html2canvas (para captura de tela)
  - jsPDF (para geração de PDF)
- **Bibliotecas Python**:
  - Flask
  - Flask-CORS
  - Flask-Bcrypt
  - Flask-JWT-Extended

## Funcionalidades

### Autenticação
- Tela de login com seleção de perfil (Aluno/Gestão)
- Autenticação JWT segura
- Credenciais padrão: **admin/admin** para gestor
- Proteção de rotas com verificação de token

### Dashboard
- Resumo visual em tempo real do banco de dados:
  - Total de livros
  - Total de usuários
  - Leituras ativas (empréstimos)
  - Alertas (empréstimos atrasados)
- Feed de atividades recentes

### Gestão de Livros
- Adicionar novos livros com campos:
  - Área do conhecimento
  - Tombo, ID
  - Autor, Título
  - Volume, Edição
  - Local, Editora, Ano
- Editar livros existentes
- Deletar livros
- Integração completa com banco de dados
- Controle de disponibilidade (emprestado/disponível)

### Gestão de Usuários
- Adicionar usuários (Aluno/Professor/Outro)
- Campos dinâmicos baseados no tipo:
  - **Aluno**: Matrícula, Turma, Telefone, E-mail
  - **Professor**: CPF, Telefone, E-mail
- Editar e deletar usuários
- Senhas criptografadas com bcrypt
- Persistência em banco de dados

### Gestão de Empréstimos (NOVO)
- Registrar novos empréstimos
- Selecionar livro disponível
- Selecionar usuário (aluno ou professor)
- Prazo automático de 14 dias
- Registrar devolução de livros
- Controlar status (ativo/devolvido/atrasado)
- Histórico completo de empréstimos

### Relatórios
- Visualização de estatísticas gerais:
  - Total de livros
  - Total de usuários
  - Alunos e professores
  - Pendências
- Tabela de usuários com pendências
- Geração de relatórios em PDF

## Como Executar

O servidor Flask está configurado para rodar automaticamente na porta 5000.

### Manualmente
```bash
python server.py
```

### Primeiro Acesso
1. Acesse: http://localhost:5000/
2. Será redirecionado para a tela de login
3. Use as credenciais padrão:
   - **Gestor**: Email: `admin` | Senha: `admin`
4. Após login, você terá acesso a todas as funcionalidades


### Configuração com Supabase (Postgres)
O backend agora suporta Supabase via string de conexão Postgres.

1. Crie um banco no Supabase e copie a connection string (URI Postgres).
2. Defina a variável de ambiente:
   - `SUPABASE_DB_URL=postgresql://USER:PASS@HOST:5432/postgres`
3. Inicie o servidor normalmente:
   - `python server.py`

`SUPABASE_DB_URL` é obrigatória nesta versão.

## Persistência de Dados
- Os dados são armazenados em **Supabase Postgres**
- Dados persistem entre sessões
- Suporta operações CRUD completas
- Integridade referencial entre tabelas

## Arquitetura
Este é um aplicativo **full-stack** com:
- **Frontend**: HTML/CSS/JavaScript puro
- **Backend**: Flask com APIs REST
- **Banco de Dados**: Supabase Postgres
- **Autenticação**: JWT (JSON Web Tokens)
- **Segurança**: Senhas criptografadas com bcrypt
- **Comunicação**: APIs REST com JSON

## Navegação
O sistema possui uma sidebar fixa com navegação entre:
1. Dashboard (dashboard.html)
2. Livros (livros.html)
3. Usuários (usuarios.html)
4. Empréstimos (emprestimos.html) **NOVO**
5. Relatórios (relatorios.html)

## APIs Disponíveis

### Autenticação
- `POST /api/login` - Autenticar usuário

### Livros
- `GET /api/livros` - Listar todos os livros
- `POST /api/livros` - Criar novo livro
- `PUT /api/livros/<id>` - Atualizar livro
- `DELETE /api/livros/<id>` - Deletar livro

### Usuários
- `GET /api/usuarios` - Listar todos os usuários
- `POST /api/usuarios` - Criar novo usuário
- `PUT /api/usuarios/<id>` - Atualizar usuário
- `DELETE /api/usuarios/<id>` - Deletar usuário

### Empréstimos
- `GET /api/emprestimos` - Listar todos os empréstimos
- `POST /api/emprestimos` - Criar novo empréstimo
- `POST /api/emprestimos/<id>/devolver` - Registrar devolução

### Estatísticas
- `GET /api/stats` - Obter estatísticas do dashboard

## Estado Atual
- ✅ Backend Flask completo e funcional
- ✅ Banco de dados Supabase Postgres integrado
- ✅ Sistema de autenticação JWT
- ✅ Tela de login customizada
- ✅ Sistema de CRUD para livros
- ✅ Sistema de CRUD para usuários
- ✅ Sistema de gestão de empréstimos **NOVO**
- ✅ Geração de relatórios em PDF
- ✅ Interface responsiva
- ✅ APIs REST completas

## Próximos Passos Potenciais
- Implementar busca funcional nas tabelas
- Adicionar notificações de empréstimos atrasados
- Implementar diferentes níveis de permissão
- Adicionar histórico de atividades
- Migrar para PostgreSQL para produção
- Adicionar validações mais robustas no frontend
- Implementar paginação nas tabelas

## Versão
2.0 - Sistema completo com backend e banco de dados (27 de outubro de 2025)
