# Configuração do Supabase (Postgres) para BibliotecAI

## 1) Criar projeto no Supabase
1. Acesse https://supabase.com e clique em **New project**.
2. Escolha organização, nome do projeto, senha do banco e região.
3. Aguarde o projeto subir (1-2 minutos).

## 2) Obter string de conexão Postgres
1. No dashboard do projeto, vá em **Connect**.
2. Selecione **Connection string** > **URI**.
3. Copie a string no formato:

```txt
postgresql://postgres:<SENHA>@db.<PROJECT_REF>.supabase.co:5432/postgres
```

> Use a senha do banco definida na criação do projeto.

## 3) Configurar variáveis de ambiente no backend
No ambiente onde roda o Flask, configure:

```bash
export SUPABASE_DB_URL="postgresql://postgres:<SENHA>@db.<PROJECT_REF>.supabase.co:5432/postgres"
export JWT_SECRET_KEY="troque-por-um-segredo-forte"
```

## 4) Instalar dependências
```bash
pip install -r requirements.txt  # se existir
# ou
pip install flask flask-bcrypt flask-cors flask-jwt-extended "psycopg[binary]"
```

## 5) Subir backend
```bash
python server.py
```

Na primeira inicialização, o app cria automaticamente as tabelas:
- `usuarios`
- `livros`
- `emprestimos`

e cria o usuário admin padrão:
- email: `admin`
- senha: `admin`

## 6) Validar conexão
Abra no navegador:

```txt
http://localhost:5000/api/health
```

Resposta esperada:

```json
{ "ok": true, "db_mode": "postgres" }
```

## 7) Configurar frontend (se estiver em outro host)
Na tela de login do front, informe a URL da API (exemplo):

```txt
http://localhost:5000
```

ou a URL pública do backend implantado.

## 8) Dicas de produção
- Nunca usar `debug=True` em produção.
- Usar Gunicorn/Uvicorn + proxy (Nginx/Render/Fly/Railway).
- Rotacionar `JWT_SECRET_KEY`.
- Aplicar políticas de backup no Supabase.
