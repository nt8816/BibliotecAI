from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import sqlite3
from datetime import datetime, timedelta
import os

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None
    dict_row = None

app = Flask(__name__, static_folder='.')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'bibliotecai-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

SQLITE_DATABASE = os.getenv('SQLITE_DATABASE', 'bibliotecai.db')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '').strip()
DB_MODE = 'postgres' if SUPABASE_DB_URL else 'sqlite'


def get_db():
    if DB_MODE == 'postgres':
        if psycopg is None:
            raise RuntimeError('psycopg não instalado. Adicione a dependência para usar Supabase/Postgres.')
        return psycopg.connect(SUPABASE_DB_URL, row_factory=dict_row)

    conn = sqlite3.connect(SQLITE_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def _placeholder(sql: str) -> str:
    if DB_MODE == 'postgres':
        parts = sql.split('?')
        if len(parts) == 1:
            return sql
        converted = [parts[0]]
        for i, part in enumerate(parts[1:], start=1):
            converted.append(f'${i}{part}')
        return ''.join(converted)
    return sql


def fetch_one(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        return dict(row)
    return row


def fetch_all(cursor):
    rows = cursor.fetchall()
    if not rows:
        return []
    if isinstance(rows[0], sqlite3.Row):
        return [dict(r) for r in rows]
    return rows


def execute(cursor, sql, params=()):
    cursor.execute(_placeholder(sql), params)


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    if DB_MODE == 'postgres':
        execute(cursor, '''
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
        ''')

        execute(cursor, '''
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
        ''')

        execute(cursor, '''
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
        ''')
    else:
        execute(cursor, '''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        ''')

        execute(cursor, '''
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        ''')

        execute(cursor, '''
            CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                livro_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_devolucao_prevista DATE NOT NULL,
                data_devolucao_real DATE,
                status TEXT DEFAULT 'ativo',
                observacoes TEXT,
                FOREIGN KEY (livro_id) REFERENCES livros(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')

    execute(cursor, 'SELECT COUNT(*) AS total FROM usuarios WHERE email = ?', ('admin',))
    result = fetch_one(cursor)
    if result and result['total'] == 0:
        senha_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
        if DB_MODE == 'postgres':
            execute(cursor, 'INSERT INTO usuarios (nome, tipo, email, senha) VALUES (?, ?, ?, ?) RETURNING id', ('Administrador', 'Gestor', 'admin', senha_hash))
            cursor.fetchone()
        else:
            execute(cursor, 'INSERT INTO usuarios (nome, tipo, email, senha) VALUES (?, ?, ?, ?)', ('Administrador', 'Gestor', 'admin', senha_hash))

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'ok': True, 'db_mode': DB_MODE})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email = (data.get('email') or '').strip()
    senha = data.get('senha') or ''
    tipo_perfil = data.get('tipo', 'Aluno')

    if not email or not senha:
        return jsonify({'success': False, 'message': 'Informe email/matrícula e senha'}), 400

    conn = get_db()
    cursor = conn.cursor()
    execute(cursor, 'SELECT * FROM usuarios WHERE email = ? OR matricula = ? LIMIT 1', (email, email))
    usuario = fetch_one(cursor)
    conn.close()

    if usuario and usuario.get('senha') and bcrypt.check_password_hash(usuario['senha'], senha):
        if usuario['tipo'] == 'Gestor' and tipo_perfil == 'Gestão':
            token = create_access_token(identity={'id': usuario['id'], 'tipo': usuario['tipo']})
            return jsonify({
                'success': True,
                'token': token,
                'usuario': {
                    'id': usuario['id'],
                    'nome': usuario['nome'],
                    'tipo': usuario['tipo'],
                    'email': usuario['email']
                }
            })

        if usuario['tipo'] == 'Aluno' and tipo_perfil == 'Aluno':
            token = create_access_token(identity={'id': usuario['id'], 'tipo': usuario['tipo']})
            return jsonify({
                'success': True,
                'token': token,
                'usuario': {
                    'id': usuario['id'],
                    'nome': usuario['nome'],
                    'tipo': usuario['tipo'],
                    'matricula': usuario['matricula']
                }
            })

    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401


@app.route('/api/livros', methods=['GET', 'POST'])
@jwt_required()
def livros():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        execute(cursor, 'SELECT * FROM livros ORDER BY id DESC')
        livros_data = fetch_all(cursor)
        conn.close()
        return jsonify(livros_data)

    data = request.json or {}
    required_fields = ['area', 'tombo', 'autor', 'titulo', 'editora', 'ano']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        conn.close()
        return jsonify({'success': False, 'message': f'Campos obrigatórios: {", ".join(missing)}'}), 400

    execute(cursor, '''
        INSERT INTO livros (area, tombo, autor, titulo, vol, edicao, local, editora, ano)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['area'], data['tombo'], data['autor'], data['titulo'],
        data.get('vol', ''), data.get('edicao', ''), data.get('local', ''),
        data['editora'], data['ano']
    ))

    livro_id = cursor.lastrowid if DB_MODE == 'sqlite' else None

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': livro_id}), 201


@app.route('/api/livros/<int:livro_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def livro_detail(livro_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'PUT':
        data = request.json or {}
        execute(cursor, '''
            UPDATE livros
            SET area=?, tombo=?, autor=?, titulo=?, vol=?, edicao=?, local=?, editora=?, ano=?
            WHERE id=?
        ''', (
            data.get('area', ''), data.get('tombo', ''), data.get('autor', ''), data.get('titulo', ''),
            data.get('vol', ''), data.get('edicao', ''), data.get('local', ''),
            data.get('editora', ''), data.get('ano', ''), livro_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    execute(cursor, 'DELETE FROM livros WHERE id=?', (livro_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/usuarios', methods=['GET', 'POST'])
@jwt_required()
def usuarios():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        execute(cursor, 'SELECT * FROM usuarios ORDER BY id DESC')
        usuarios_data = fetch_all(cursor)
        for usuario in usuarios_data:
            usuario.pop('senha', None)
        conn.close()
        return jsonify(usuarios_data)

    data = request.json or {}
    if not data.get('nome') or not data.get('tipo'):
        conn.close()
        return jsonify({'success': False, 'message': 'Nome e tipo são obrigatórios'}), 400

    senha_hash = bcrypt.generate_password_hash(data.get('senha', '123456')).decode('utf-8')
    execute(cursor, '''
        INSERT INTO usuarios (nome, tipo, matricula, cpf, turma, telefone, email, senha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['nome'], data['tipo'], data.get('matricula', ''), data.get('cpf', ''),
        data.get('turma', ''), data.get('telefone', ''), data.get('email', ''), senha_hash
    ))

    usuario_id = cursor.lastrowid if DB_MODE == 'sqlite' else None
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': usuario_id}), 201


@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def usuario_detail(usuario_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'PUT':
        data = request.json or {}
        execute(cursor, '''
            UPDATE usuarios
            SET nome=?, tipo=?, matricula=?, cpf=?, turma=?, telefone=?, email=?
            WHERE id=?
        ''', (
            data.get('nome', ''), data.get('tipo', ''), data.get('matricula', ''), data.get('cpf', ''),
            data.get('turma', ''), data.get('telefone', ''), data.get('email', ''), usuario_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    execute(cursor, 'DELETE FROM usuarios WHERE id=?', (usuario_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/emprestimos', methods=['GET', 'POST'])
@jwt_required()
def emprestimos():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        execute(cursor, '''
            SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
                   u.nome as usuario_nome, u.tipo as usuario_tipo, u.telefone as usuario_telefone
            FROM emprestimos e
            JOIN livros l ON e.livro_id = l.id
            JOIN usuarios u ON e.usuario_id = u.id
            ORDER BY e.id DESC
        ''')
        emprestimos_data = fetch_all(cursor)
        conn.close()
        return jsonify(emprestimos_data)

    data = request.json or {}
    livro_id = data.get('livro_id')
    usuario_id = data.get('usuario_id')
    if not livro_id or not usuario_id:
        conn.close()
        return jsonify({'success': False, 'message': 'Livro e usuário são obrigatórios'}), 400

    execute(cursor, 'SELECT id, disponivel FROM livros WHERE id = ? LIMIT 1', (livro_id,))
    livro = fetch_one(cursor)
    if not livro:
        conn.close()
        return jsonify({'success': False, 'message': 'Livro não encontrado'}), 404
    if int(livro.get('disponivel', 0)) != 1:
        conn.close()
        return jsonify({'success': False, 'message': 'Livro indisponível para empréstimo'}), 409

    data_devolucao = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

    execute(cursor, '''
        INSERT INTO emprestimos (livro_id, usuario_id, data_devolucao_prevista, observacoes)
        VALUES (?, ?, ?, ?)
    ''', (livro_id, usuario_id, data_devolucao, data.get('observacoes', '')))

    execute(cursor, 'UPDATE livros SET disponivel = 0 WHERE id = ?', (livro_id,))

    emprestimo_id = cursor.lastrowid if DB_MODE == 'sqlite' else None
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': emprestimo_id}), 201


@app.route('/api/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])
@jwt_required()
def devolver_livro(emprestimo_id):
    conn = get_db()
    cursor = conn.cursor()

    execute(cursor, 'SELECT livro_id, status FROM emprestimos WHERE id = ? LIMIT 1', (emprestimo_id,))
    result = fetch_one(cursor)

    if not result:
        conn.close()
        return jsonify({'success': False, 'message': 'Empréstimo não encontrado'}), 404

    if result.get('status') == 'devolvido':
        conn.close()
        return jsonify({'success': True, 'message': 'Livro já devolvido'})

    livro_id = result['livro_id']
    execute(cursor, '''
        UPDATE emprestimos SET status = 'devolvido', data_devolucao_real = ?
        WHERE id = ?
    ''', (datetime.now().strftime('%Y-%m-%d'), emprestimo_id))

    execute(cursor, 'UPDATE livros SET disponivel = 1 WHERE id = ?', (livro_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
@jwt_required()
def stats():
    conn = get_db()
    cursor = conn.cursor()

    execute(cursor, 'SELECT COUNT(*) as total FROM livros')
    total_livros = fetch_one(cursor)['total']

    execute(cursor, 'SELECT COUNT(*) as total FROM usuarios WHERE tipo != ? ', ('Gestor',))
    total_usuarios = fetch_one(cursor)['total']

    execute(cursor, 'SELECT COUNT(*) as total FROM emprestimos WHERE status = ?', ('ativo',))
    leituras_ativas = fetch_one(cursor)['total']

    if DB_MODE == 'postgres':
        execute(cursor, '''
            SELECT COUNT(*) as total FROM emprestimos
            WHERE status = ? AND data_devolucao_prevista < CURRENT_DATE
        ''', ('ativo',))
    else:
        execute(cursor, '''
            SELECT COUNT(*) as total FROM emprestimos
            WHERE status = ? AND date(data_devolucao_prevista) < date('now')
        ''', ('ativo',))
    alertas = fetch_one(cursor)['total']

    conn.close()

    return jsonify({
        'total_livros': total_livros,
        'total_usuarios': total_usuarios,
        'leituras_ativas': leituras_ativas,
        'alertas': alertas,
        'db_mode': DB_MODE
    })


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
