# Configuração do Supabase (Postgres) para BibliotecAI (Node.js)

## 1) Criar projeto no Supabase
1. Acesse https://supabase.com e clique em **New project**.
2. Escolha organização, nome, senha do banco e região.
3. Aguarde o provisionamento.

## 2) Pegar connection string
No painel do projeto:
- **Connect** → **Connection string** → **URI**
- Formato:

```txt
postgresql://postgres:<SENHA>@db.<PROJECT_REF>.supabase.co:5432/postgres
```

## 3) Configurar variáveis de ambiente
```bash
export SUPABASE_DB_URL="postgresql://postgres:<SENHA>@db.<PROJECT_REF>.supabase.co:5432/postgres"
export JWT_SECRET_KEY="troque-por-um-segredo-forte"
export PORT=5000
```

## 4) Instalar dependências
```bash
npm install
```

## 5) Subir aplicação
```bash
npm run start
```

## 6) Validar
- Healthcheck:
  - `http://localhost:5000/api/health`
  - esperado: `{ "ok": true, "db_mode": "postgres" }`
- Login gestor padrão:
  - usuário: `admin`
  - senha: `admin`

> Na primeira inicialização, as tabelas e o usuário admin são criados automaticamente.

## 7) Frontend em outro host
Se o frontend não estiver no mesmo domínio da API, informe a URL da API na tela de login.


## 8) Dados que você me enviou (já integrados no front)
- URL do projeto: `https://dhjkjwkitufsvhlhcsec.supabase.co`
- Chave anônima: configurada em `supabase-config.js`
- Chave publicável: configurada em `supabase-config.js`

> Importante: essas chaves públicas **não substituem** `SUPABASE_DB_URL` no backend.
