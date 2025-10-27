from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='.')
app.config['JWT_SECRET_KEY'] = 'bibliotecai-secret-key-2025'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

DATABASE = 'bibliotecai.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
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
    
    cursor.execute('''
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
    
    cursor.execute('''
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
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = 'admin'")
    if cursor.fetchone()[0] == 0:
        senha_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
        cursor.execute('''
            INSERT INTO usuarios (nome, tipo, email, senha)
            VALUES (?, ?, ?, ?)
        ''', ('Administrador', 'Gestor', 'admin', senha_hash))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')
    tipo_perfil = data.get('tipo', 'Aluno')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = ? OR matricula = ?', (email, email))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario and bcrypt.check_password_hash(usuario['senha'], senha):
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
        elif usuario['tipo'] == 'Aluno' and tipo_perfil == 'Aluno':
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
        cursor.execute('SELECT * FROM livros ORDER BY id DESC')
        livros = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(livros)
    
    elif request.method == 'POST':
        data = request.json
        cursor.execute('''
            INSERT INTO livros (area, tombo, autor, titulo, vol, edicao, local, editora, ano)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['area'], data['tombo'], data['autor'], data['titulo'],
            data.get('vol', ''), data.get('edicao', ''), data.get('local', ''),
            data['editora'], data['ano']
        ))
        conn.commit()
        livro_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': livro_id}), 201

@app.route('/api/livros/<int:livro_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def livro_detail(livro_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE livros SET area=?, tombo=?, autor=?, titulo=?, vol=?, edicao=?, local=?, editora=?, ano=?
            WHERE id=?
        ''', (
            data['area'], data['tombo'], data['autor'], data['titulo'],
            data.get('vol', ''), data.get('edicao', ''), data.get('local', ''),
            data['editora'], data['ano'], livro_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM livros WHERE id=?', (livro_id,))
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
        usuarios = [dict(row) for row in cursor.fetchall()]
        for usuario in usuarios:
            if 'senha' in usuario:
                del usuario['senha']
        conn.close()
        return jsonify(usuarios)
    
    elif request.method == 'POST':
        data = request.json
        senha_hash = bcrypt.generate_password_hash(data.get('senha', '123456')).decode('utf-8')
        cursor.execute('''
            INSERT INTO usuarios (nome, tipo, matricula, cpf, turma, telefone, email, senha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['nome'], data['tipo'], data.get('matricula', ''), data.get('cpf', ''),
            data.get('turma', ''), data.get('telefone', ''), data.get('email', ''), senha_hash
        ))
        conn.commit()
        usuario_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': usuario_id}), 201

@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def usuario_detail(usuario_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE usuarios SET nome=?, tipo=?, matricula=?, cpf=?, turma=?, telefone=?, email=?
            WHERE id=?
        ''', (
            data['nome'], data['tipo'], data.get('matricula', ''), data.get('cpf', ''),
            data.get('turma', ''), data.get('telefone', ''), data.get('email', ''), usuario_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM usuarios WHERE id=?', (usuario_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/emprestimos', methods=['GET', 'POST'])
@jwt_required()
def emprestimos():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute('''
            SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
                   u.nome as usuario_nome, u.tipo as usuario_tipo, u.telefone as usuario_telefone
            FROM emprestimos e
            JOIN livros l ON e.livro_id = l.id
            JOIN usuarios u ON e.usuario_id = u.id
            ORDER BY e.id DESC
        ''')
        emprestimos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(emprestimos)
    
    elif request.method == 'POST':
        data = request.json
        data_devolucao = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO emprestimos (livro_id, usuario_id, data_devolucao_prevista, observacoes)
            VALUES (?, ?, ?, ?)
        ''', (data['livro_id'], data['usuario_id'], data_devolucao, data.get('observacoes', '')))
        
        cursor.execute('UPDATE livros SET disponivel = 0 WHERE id = ?', (data['livro_id'],))
        
        conn.commit()
        emprestimo_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': emprestimo_id}), 201

@app.route('/api/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])
@jwt_required()
def devolver_livro(emprestimo_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT livro_id FROM emprestimos WHERE id = ?', (emprestimo_id,))
    result = cursor.fetchone()
    
    if result:
        livro_id = result['livro_id']
        cursor.execute('''
            UPDATE emprestimos SET status = 'devolvido', data_devolucao_real = ?
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d'), emprestimo_id))
        
        cursor.execute('UPDATE livros SET disponivel = 1 WHERE id = ?', (livro_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    conn.close()
    return jsonify({'success': False, 'message': 'Empréstimo não encontrado'}), 404

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM livros')
    total_livros = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM usuarios WHERE tipo != "Gestor"')
    total_usuarios = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM emprestimos WHERE status = "ativo"')
    leituras_ativas = cursor.fetchone()['total']
    
    cursor.execute('''
        SELECT COUNT(*) as total FROM emprestimos 
        WHERE status = "ativo" AND date(data_devolucao_prevista) < date("now")
    ''')
    alertas = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'total_livros': total_livros,
        'total_usuarios': total_usuarios,
        'leituras_ativas': leituras_ativas,
        'alertas': alertas
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
