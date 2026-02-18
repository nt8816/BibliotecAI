from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime, timedelta
import os

import psycopg
from psycopg.rows import dict_row

app = Flask(__name__, static_folder='.')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'bibliotecai-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '').strip()


def get_db():
    if not SUPABASE_DB_URL:
        raise RuntimeError('SUPABASE_DB_URL não configurada. Configure a conexão Postgres do Supabase.')
    return psycopg.connect(SUPABASE_DB_URL, row_factory=dict_row)


def fetch_one(cursor):
    return cursor.fetchone()


def fetch_all(cursor):
    return cursor.fetchall() or []


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
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

    cursor.execute('''
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

    cursor.execute('''
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

    cursor.execute('SELECT COUNT(*) AS total FROM usuarios WHERE email = %s', ('admin',))
    result = fetch_one(cursor)
    if result and result['total'] == 0:
        senha_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
        cursor.execute(
            'INSERT INTO usuarios (nome, tipo, email, senha) VALUES (%s, %s, %s, %s)',
            ('Administrador', 'Gestor', 'admin', senha_hash),
        )

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
    return jsonify({'ok': True, 'db_mode': 'postgres'})


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
    cursor.execute('SELECT * FROM usuarios WHERE email = %s OR matricula = %s LIMIT 1', (email, email))
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
                    'email': usuario['email'],
                },
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
                    'matricula': usuario['matricula'],
                },
            })

    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401


@app.route('/api/livros', methods=['GET', 'POST'])
@jwt_required()
def livros():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM livros ORDER BY id DESC')
        livros_data = fetch_all(cursor)
        conn.close()
        return jsonify(livros_data)

    data = request.json or {}
    required_fields = ['area', 'tombo', 'autor', 'titulo', 'editora', 'ano']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        conn.close()
        return jsonify({'success': False, 'message': f'Campos obrigatórios: {", ".join(missing)}'}), 400

    cursor.execute(
        '''
        INSERT INTO livros (area, tombo, autor, titulo, vol, edicao, local, editora, ano)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
            data['area'],
            data['tombo'],
            data['autor'],
            data['titulo'],
            data.get('vol', ''),
            data.get('edicao', ''),
            data.get('local', ''),
            data['editora'],
            data['ano'],
        ),
    )
    livro_id = fetch_one(cursor)['id']

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
        cursor.execute(
            '''
            UPDATE livros
            SET area=%s, tombo=%s, autor=%s, titulo=%s, vol=%s, edicao=%s, local=%s, editora=%s, ano=%s
            WHERE id=%s
            ''',
            (
                data.get('area', ''),
                data.get('tombo', ''),
                data.get('autor', ''),
                data.get('titulo', ''),
                data.get('vol', ''),
                data.get('edicao', ''),
                data.get('local', ''),
                data.get('editora', ''),
                data.get('ano', ''),
                livro_id,
            ),
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    cursor.execute('DELETE FROM livros WHERE id=%s', (livro_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/usuarios', methods=['GET', 'POST'])
@jwt_required()
def usuarios():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM usuarios ORDER BY id DESC')
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
    cursor.execute(
        '''
        INSERT INTO usuarios (nome, tipo, matricula, cpf, turma, telefone, email, senha)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
            data['nome'],
            data['tipo'],
            data.get('matricula', ''),
            data.get('cpf', ''),
            data.get('turma', ''),
            data.get('telefone', ''),
            data.get('email', ''),
            senha_hash,
        ),
    )
    usuario_id = fetch_one(cursor)['id']

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
        cursor.execute(
            '''
            UPDATE usuarios
            SET nome=%s, tipo=%s, matricula=%s, cpf=%s, turma=%s, telefone=%s, email=%s
            WHERE id=%s
            ''',
            (
                data.get('nome', ''),
                data.get('tipo', ''),
                data.get('matricula', ''),
                data.get('cpf', ''),
                data.get('turma', ''),
                data.get('telefone', ''),
                data.get('email', ''),
                usuario_id,
            ),
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    cursor.execute('DELETE FROM usuarios WHERE id=%s', (usuario_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/emprestimos', methods=['GET', 'POST'])
@jwt_required()
def emprestimos():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute(
            '''
            SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
                   u.nome as usuario_nome, u.tipo as usuario_tipo, u.telefone as usuario_telefone
            FROM emprestimos e
            JOIN livros l ON e.livro_id = l.id
            JOIN usuarios u ON e.usuario_id = u.id
            ORDER BY e.id DESC
            '''
        )
        emprestimos_data = fetch_all(cursor)
        conn.close()
        return jsonify(emprestimos_data)

    data = request.json or {}
    livro_id = data.get('livro_id')
    usuario_id = data.get('usuario_id')
    if not livro_id or not usuario_id:
        conn.close()
        return jsonify({'success': False, 'message': 'Livro e usuário são obrigatórios'}), 400

    cursor.execute('SELECT id, disponivel FROM livros WHERE id = %s LIMIT 1', (livro_id,))
    livro = fetch_one(cursor)
    if not livro:
        conn.close()
        return jsonify({'success': False, 'message': 'Livro não encontrado'}), 404
    if int(livro.get('disponivel', 0)) != 1:
        conn.close()
        return jsonify({'success': False, 'message': 'Livro indisponível para empréstimo'}), 409

    data_devolucao = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

    cursor.execute(
        '''
        INSERT INTO emprestimos (livro_id, usuario_id, data_devolucao_prevista, observacoes)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        ''',
        (livro_id, usuario_id, data_devolucao, data.get('observacoes', '')),
    )
    emprestimo_id = fetch_one(cursor)['id']

    cursor.execute('UPDATE livros SET disponivel = 0 WHERE id = %s', (livro_id,))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': emprestimo_id}), 201


@app.route('/api/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])
@jwt_required()
def devolver_livro(emprestimo_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT livro_id, status FROM emprestimos WHERE id = %s LIMIT 1', (emprestimo_id,))
    result = fetch_one(cursor)

    if not result:
        conn.close()
        return jsonify({'success': False, 'message': 'Empréstimo não encontrado'}), 404

    if result.get('status') == 'devolvido':
        conn.close()
        return jsonify({'success': True, 'message': 'Livro já devolvido'})

    livro_id = result['livro_id']
    cursor.execute(
        '''
        UPDATE emprestimos SET status = 'devolvido', data_devolucao_real = %s
        WHERE id = %s
        ''',
        (datetime.now().strftime('%Y-%m-%d'), emprestimo_id),
    )

    cursor.execute('UPDATE livros SET disponivel = 1 WHERE id = %s', (livro_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
@jwt_required()
def stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM livros')
    total_livros = fetch_one(cursor)['total']

    cursor.execute('SELECT COUNT(*) as total FROM usuarios WHERE tipo != %s', ('Gestor',))
    total_usuarios = fetch_one(cursor)['total']

    cursor.execute('SELECT COUNT(*) as total FROM emprestimos WHERE status = %s', ('ativo',))
    leituras_ativas = fetch_one(cursor)['total']

    cursor.execute(
        '''
        SELECT COUNT(*) as total FROM emprestimos
        WHERE status = %s AND data_devolucao_prevista < CURRENT_DATE
        ''',
        ('ativo',),
    )
    alertas = fetch_one(cursor)['total']

    conn.close()

    return jsonify(
        {
            'total_livros': total_livros,
            'total_usuarios': total_usuarios,
            'leituras_ativas': leituras_ativas,
            'alertas': alertas,
            'db_mode': 'postgres',
        }
    )


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
