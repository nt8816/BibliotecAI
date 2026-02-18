const express = require('express');
const cors = require('cors');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');

const app = express();
const PORT = Number(process.env.PORT || 5000);
const JWT_SECRET = (process.env.JWT_SECRET_KEY || '').trim() || 'bibliotecai-secret-key-2025';
const JWT_EXPIRES = '24h';
const SUPABASE_DB_URL = (process.env.SUPABASE_DB_URL || '').trim();

if (!SUPABASE_DB_URL) {
  throw new Error('SUPABASE_DB_URL não configurada. Configure a conexão Postgres do Supabase.');
}

const pool = new Pool({
  connectionString: SUPABASE_DB_URL,
  ssl: process.env.PGSSLMODE === 'disable' ? false : { rejectUnauthorized: false }
});

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));


function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

function signToken(usuario) {
  return jwt.sign({ id: usuario.id, tipo: usuario.tipo }, JWT_SECRET, { expiresIn: JWT_EXPIRES });
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization || '';
  const [, token] = authHeader.split(' ');

  if (!token) {
    return res.status(401).json({ success: false, message: 'Token ausente' });
  }

  try {
    req.user = jwt.verify(token, JWT_SECRET);
    return next();
  } catch (error) {
    return res.status(401).json({ success: false, message: 'Token inválido ou expirado' });
  }
}


function parseId(value) {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
}

async function initDb() {
  const client = await pool.connect();
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,
        matricula TEXT,
        cpf TEXT,
        turma TEXT,
        telefone TEXT,
        email TEXT,
        senha TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await client.query(`
      CREATE TABLE IF NOT EXISTS livros (
        id SERIAL PRIMARY KEY,
        area TEXT NOT NULL,
        tombo TEXT NOT NULL,
        autor TEXT NOT NULL,
        titulo TEXT NOT NULL,
        vol TEXT,
        edicao TEXT,
        local TEXT,
        editora TEXT NOT NULL,
        ano INTEGER NOT NULL,
        disponivel INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await client.query(`
      CREATE TABLE IF NOT EXISTS emprestimos (
        id SERIAL PRIMARY KEY,
        livro_id INTEGER NOT NULL REFERENCES livros(id),
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_devolucao_prevista DATE NOT NULL,
        data_devolucao_real DATE,
        status TEXT DEFAULT 'ativo',
        observacoes TEXT
      )
    `);

    const adminCheck = await client.query('SELECT COUNT(*)::int AS total FROM usuarios WHERE email = $1', ['admin']);
    if (adminCheck.rows[0].total === 0) {
      const senhaHash = await bcrypt.hash('admin', 10);
      await client.query(
        'INSERT INTO usuarios (nome, tipo, email, senha) VALUES ($1, $2, $3, $4)',
        ['Administrador', 'Gestor', 'admin', senhaHash]
      );
    }
  } finally {
    client.release();
  }
}

app.get('/api/health', asyncHandler(async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    return res.json({ ok: true, db_mode: 'postgres' });
  } catch (error) {
    return res.status(500).json({ ok: false, message: 'Falha na conexão com Postgres' });
  }
}));

app.post('/api/login', asyncHandler(async (req, res) => {
  const { email = '', senha = '', tipo = 'Aluno' } = req.body || {};
  const userId = String(email).trim();

  if (!userId || !senha) {
    return res.status(400).json({ success: false, message: 'Informe email/matrícula e senha' });
  }

  const { rows } = await pool.query(
    'SELECT * FROM usuarios WHERE email = $1 OR matricula = $1 LIMIT 1',
    [userId]
  );
  const usuario = rows[0];

  if (!usuario || !usuario.senha || !(await bcrypt.compare(senha, usuario.senha))) {
    return res.status(401).json({ success: false, message: 'Credenciais inválidas' });
  }

  if (usuario.tipo === 'Gestor' && tipo === 'Gestão') {
    const token = signToken(usuario);
    return res.json({
      success: true,
      token,
      usuario: { id: usuario.id, nome: usuario.nome, tipo: usuario.tipo, email: usuario.email }
    });
  }

  if (usuario.tipo === 'Aluno' && tipo === 'Aluno') {
    const token = signToken(usuario);
    return res.json({
      success: true,
      token,
      usuario: { id: usuario.id, nome: usuario.nome, tipo: usuario.tipo, matricula: usuario.matricula }
    });
  }

  return res.status(401).json({ success: false, message: 'Perfil não autorizado para este login' });
}));

app.get('/api/livros', authMiddleware, asyncHandler(async (_req, res) => {
  const { rows } = await pool.query('SELECT * FROM livros ORDER BY id DESC');
  return res.json(rows);
}));

app.post('/api/livros', authMiddleware, asyncHandler(async (req, res) => {
  const data = req.body || {};
  const required = ['area', 'tombo', 'autor', 'titulo', 'editora', 'ano'];
  const missing = required.filter((f) => !data[f]);
  if (missing.length) {
    return res.status(400).json({ success: false, message: `Campos obrigatórios: ${missing.join(', ')}` });
  }

  const { rows } = await pool.query(
    `INSERT INTO livros (area, tombo, autor, titulo, vol, edicao, local, editora, ano)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING id`,
    [
      data.area,
      data.tombo,
      data.autor,
      data.titulo,
      data.vol || '',
      data.edicao || '',
      data.local || '',
      data.editora,
      Number(data.ano)
    ]
  );
  return res.status(201).json({ success: true, id: rows[0].id });
}));

app.put('/api/livros/:livroId', authMiddleware, asyncHandler(async (req, res) => {
  const id = parseId(req.params.livroId);
  if (!id) return res.status(400).json({ success: false, message: 'ID do livro inválido' });

  const d = req.body || {};
  const result = await pool.query(
    `UPDATE livros SET area=$1, tombo=$2, autor=$3, titulo=$4, vol=$5, edicao=$6, local=$7, editora=$8, ano=$9
     WHERE id=$10`,
    [d.area || '', d.tombo || '', d.autor || '', d.titulo || '', d.vol || '', d.edicao || '', d.local || '', d.editora || '', Number(d.ano || 0), id]
  );

  if (result.rowCount === 0) {
    return res.status(404).json({ success: false, message: 'Livro não encontrado' });
  }

  return res.json({ success: true });
}));

app.delete('/api/livros/:livroId', authMiddleware, asyncHandler(async (req, res) => {
  const id = parseId(req.params.livroId);
  if (!id) return res.status(400).json({ success: false, message: 'ID do livro inválido' });

  const result = await pool.query('DELETE FROM livros WHERE id = $1', [id]);
  if (result.rowCount === 0) {
    return res.status(404).json({ success: false, message: 'Livro não encontrado' });
  }

  return res.json({ success: true });
}));

app.get('/api/usuarios', authMiddleware, asyncHandler(async (_req, res) => {
  const { rows } = await pool.query('SELECT * FROM usuarios ORDER BY id DESC');
  const sanitized = rows.map(({ senha, ...rest }) => rest);
  return res.json(sanitized);
}));

app.post('/api/usuarios', authMiddleware, asyncHandler(async (req, res) => {
  const d = req.body || {};
  if (!d.nome || !d.tipo) {
    return res.status(400).json({ success: false, message: 'Nome e tipo são obrigatórios' });
  }

  const senhaHash = await bcrypt.hash(d.senha || '123456', 10);
  const { rows } = await pool.query(
    `INSERT INTO usuarios (nome, tipo, matricula, cpf, turma, telefone, email, senha)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id`,
    [d.nome, d.tipo, d.matricula || '', d.cpf || '', d.turma || '', d.telefone || '', d.email || '', senhaHash]
  );

  return res.status(201).json({ success: true, id: rows[0].id });
}));

app.put('/api/usuarios/:usuarioId', authMiddleware, asyncHandler(async (req, res) => {
  const id = parseId(req.params.usuarioId);
  if (!id) return res.status(400).json({ success: false, message: 'ID do usuário inválido' });

  const d = req.body || {};
  const result = await pool.query(
    `UPDATE usuarios SET nome=$1, tipo=$2, matricula=$3, cpf=$4, turma=$5, telefone=$6, email=$7 WHERE id=$8`,
    [d.nome || '', d.tipo || '', d.matricula || '', d.cpf || '', d.turma || '', d.telefone || '', d.email || '', id]
  );

  if (result.rowCount === 0) {
    return res.status(404).json({ success: false, message: 'Usuário não encontrado' });
  }

  return res.json({ success: true });
}));

app.delete('/api/usuarios/:usuarioId', authMiddleware, asyncHandler(async (req, res) => {
  const id = parseId(req.params.usuarioId);
  if (!id) return res.status(400).json({ success: false, message: 'ID do usuário inválido' });

  const result = await pool.query('DELETE FROM usuarios WHERE id = $1', [id]);
  if (result.rowCount === 0) {
    return res.status(404).json({ success: false, message: 'Usuário não encontrado' });
  }

  return res.json({ success: true });
}));

app.get('/api/emprestimos', authMiddleware, asyncHandler(async (_req, res) => {
  const { rows } = await pool.query(`
    SELECT e.*, l.titulo AS livro_titulo, l.autor AS livro_autor,
           u.nome AS usuario_nome, u.tipo AS usuario_tipo, u.telefone AS usuario_telefone
    FROM emprestimos e
    JOIN livros l ON e.livro_id = l.id
    JOIN usuarios u ON e.usuario_id = u.id
    ORDER BY e.id DESC
  `);
  return res.json(rows);
}));

app.post('/api/emprestimos', authMiddleware, asyncHandler(async (req, res) => {
  const d = req.body || {};
  const livroId = parseId(d.livro_id);
  const usuarioId = parseId(d.usuario_id);

  if (!livroId || !usuarioId) {
    return res.status(400).json({ success: false, message: 'Livro e usuário são obrigatórios' });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const livroRes = await client.query('SELECT id, disponivel FROM livros WHERE id = $1 FOR UPDATE', [livroId]);
    const livro = livroRes.rows[0];
    if (!livro) {
      await client.query('ROLLBACK');
      return res.status(404).json({ success: false, message: 'Livro não encontrado' });
    }

    if (Number(livro.disponivel) !== 1) {
      await client.query('ROLLBACK');
      return res.status(409).json({ success: false, message: 'Livro indisponível para empréstimo' });
    }

    const dataDevolucao = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    const insert = await client.query(
      `INSERT INTO emprestimos (livro_id, usuario_id, data_devolucao_prevista, observacoes)
       VALUES ($1,$2,$3,$4) RETURNING id`,
      [livroId, usuarioId, dataDevolucao, d.observacoes || '']
    );

    await client.query('UPDATE livros SET disponivel = 0 WHERE id = $1', [livroId]);

    await client.query('COMMIT');
    return res.status(201).json({ success: true, id: insert.rows[0].id });
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}));

app.post('/api/emprestimos/:emprestimoId/devolver', authMiddleware, asyncHandler(async (req, res) => {
  const id = parseId(req.params.emprestimoId);
  if (!id) return res.status(400).json({ success: false, message: 'ID do empréstimo inválido' });

  const result = await pool.query('SELECT livro_id, status FROM emprestimos WHERE id = $1 LIMIT 1', [id]);
  const emprestimo = result.rows[0];
  if (!emprestimo) return res.status(404).json({ success: false, message: 'Empréstimo não encontrado' });
  if (emprestimo.status === 'devolvido') return res.json({ success: true, message: 'Livro já devolvido' });

  const hoje = new Date().toISOString().slice(0, 10);
  await pool.query("UPDATE emprestimos SET status = 'devolvido', data_devolucao_real = $1 WHERE id = $2", [hoje, id]);
  await pool.query('UPDATE livros SET disponivel = 1 WHERE id = $1', [emprestimo.livro_id]);
  return res.json({ success: true });
}));

app.get('/api/stats', authMiddleware, asyncHandler(async (_req, res) => {
  const [livros, usuarios, ativos, atrasados] = await Promise.all([
    pool.query('SELECT COUNT(*)::int AS total FROM livros'),
    pool.query("SELECT COUNT(*)::int AS total FROM usuarios WHERE tipo != 'Gestor'"),
    pool.query("SELECT COUNT(*)::int AS total FROM emprestimos WHERE status = 'ativo'"),
    pool.query("SELECT COUNT(*)::int AS total FROM emprestimos WHERE status = 'ativo' AND data_devolucao_prevista < CURRENT_DATE")
  ]);

  return res.json({
    total_livros: livros.rows[0].total,
    total_usuarios: usuarios.rows[0].total,
    leituras_ativas: ativos.rows[0].total,
    alertas: atrasados.rows[0].total,
    db_mode: 'postgres'
  });
}));

app.get('/', (_req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.use((err, _req, res, _next) => {
  console.error('Erro inesperado:', err);
  res.status(500).json({ success: false, message: 'Erro interno no servidor' });
});

initDb()
  .then(() => {
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`BibliotecAI Node API rodando em http://0.0.0.0:${PORT}`);
    });
  })
  .catch((error) => {
    console.error('Falha ao inicializar o banco:', error);
    process.exit(1);
  });
