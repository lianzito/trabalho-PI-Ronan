from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import execute_one, iniciar_bd, execute_query
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '123456'

iniciar_bd() # inicia o BD e as tabelas

def garantir_admin():
    """Cria um administrador padrão caso não exista nenhum usuário (evita lockout)."""
    try:
        total = execute_one('SELECT COUNT(*) AS total FROM usuarios')
        if total and total['total'] == 0:
            funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',))
            if not funcao:
                execute_query(
                    """INSERT INTO funcoes (nome, status, descricao,
                       gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)
                       VALUES (%s, 'Ativo', %s, 1, 1, 1)""",
                    ('Administrador', 'Acesso total ao sistema')
                )
                funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',))
            execute_query(
                """INSERT INTO usuarios (nome, cpf, email, celular, estado, senha, status, funcao_id)
                   VALUES (%s, %s, %s, %s, %s, %s, 'Ativo', %s)""",
                ('Administrador', '000.000.000-00', 'admin@casagestor.com', '(00) 00000-0000', 'SP',
                 generate_password_hash('admin1234'), funcao['id_funcao'])
            )
            print('Usuário administrador padrão criado: admin@casagestor.com / admin1234')
    except Exception as e:
        print(f'Erro ao garantir admin: {e}')

garantir_admin()

def login_required(f):
    """Bloqueia o acesso às rotas do dashboard quando não há usuário logado."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('usuario'):
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.context_processor
def injetar_usuario():
    """Disponibiliza o usuário logado em todos os templates."""
    return dict(usuario_logado=session.get('usuario'))

# ── Rotas públicas ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        usuario = execute_one(
            '''SELECT u.id_usuario, u.nome, u.email, u.senha, u.status,
                      f.nome AS funcao,
                      f.gerenciar_funcoes, f.gerenciar_usuarios, f.gerenciar_tarefas
               FROM usuarios AS u
               INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
               WHERE u.email = %s''',
            (email,)
        )

        if not usuario or not check_password_hash(usuario['senha'], senha):
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('login'))

        if usuario['status'] != 'Ativo':
            flash('Usuário inativo. Contate o administrador.', 'warning')
            return redirect(url_for('login'))

        partes = usuario['nome'].split()
        iniciais = (partes[0][0] + partes[-1][0]).upper() if len(partes) > 1 else partes[0][:2].upper()

        session['usuario'] = {
            'id': usuario['id_usuario'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'funcao': usuario['funcao'],
            'iniciais': iniciais,
            'gerenciar_funcoes': usuario['gerenciar_funcoes'],
            'gerenciar_usuarios': usuario['gerenciar_usuarios'],
            'gerenciar_tarefas': usuario['gerenciar_tarefas'],
        }
        flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
        return redirect(url_for('home'))

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/cadastro')
def cadastro():
    return render_template('auth/register.html')

@app.route('/recuperar-senha')
def recuperar_senha():
    return render_template('auth/forgot_password.html')

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/home')
@login_required
def home():
    # Consultando os cards do dashboard
    totais = {
        'tarefas_pendentes': execute_one("SELECT COUNT(*) AS qtde FROM tarefas WHERE status != 'Concluído'")['qtde'],
        'tarefas_concluidas': execute_one("SELECT COUNT(*) AS qtde FROM tarefas WHERE status = 'Concluído'")['qtde'],
        'ambientes_ativos': execute_one("SELECT COUNT(*) AS qtde FROM ambientes WHERE status = 'Ativo'")['qtde'],
        'despesas_pendentes': execute_one("SELECT COUNT(*) AS qtde FROM despesas WHERE status = 'Pendente'")['qtde']
    }
    
    # Busca as 5 tarefas mais recentes para a tabela
    sql_recentes = '''
        SELECT t.titulo, t.prioridade, t.status, t.prazo, u.nome AS responsavel 
        FROM tarefas t
        LEFT JOIN usuarios u ON t.responsavel_id = u.id_usuario
        ORDER BY t.id_tarefa DESC LIMIT 5
    '''
    tarefas_recentes = execute_query(sql_recentes, fetch=True)

    return render_template('dashboard/home.html', totais=totais, tarefas=tarefas_recentes)

# CRUD DE USUÁRIOS
@app.route('/usuarios/listar')
@login_required
def usuarios_listar():
    sql = '''
            SELECT
                id_usuario,
                u.nome AS nome,
                email,
                celular,
                f.nome AS funcao,
                u.status
            FROM usuarios AS u
            INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
            ORDER BY id_usuario DESC;                
        '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('dashboard/usuarios/listar.html', dados=lista_dados)

@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
@login_required
def usuarios_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip() or None
        email = request.form.get('email', '').strip()
        celular = request.form.get('celular', '').strip()
        cep = request.form.get('cep', '').strip()
        logradouro = request.form.get('logradouro', '').strip()
        numero = request.form.get('numero', '').strip()
        complemento = request.form.get('complemento', '').strip()
        bairro = request.form.get('bairro', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()
        senha = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        funcao_id = request.form.get('funcao_id', '').strip()
        status = request.form.get('status', '').strip()

        if not all([nome, cpf, email, celular, estado, senha]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        if senha != confirmar_senha:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))
        
        sql = 'SELECT nome AS qtde FROM usuarios WHERE email = %s OR cpf = %s;'
        existente = execute_one(sql, (email, cpf))
        if existente:
            flash('E-mail ou CPF já cadastrados!', 'danger')
            return redirect(url_for('usuarios_cadastrar'))
        
        senha_hash = generate_password_hash(senha)
        
        try:
            execute_query(
                """INSERT INTO usuarios (nome, cpf, data_nascimento, email, celular,
                   cep, logradouro, numero, complemento, bairro, cidade, estado,
                   senha, status, funcao_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (nome, cpf, data_nascimento, email, celular,
                 cep, logradouro, numero, complemento, bairro, cidade, estado,
                 senha_hash, status, funcao_id)
            )
            flash('Usuário cadastrado com sucesso', 'success')
            return redirect(url_for('usuarios_listar'))
        except Exception as e:
            flash(f'Erro ao criar Usuário: {e}', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

    sql = 'SELECT id_funcao, nome FROM funcoes'
    lista_funcoes = execute_query(sql, fetch=True)
    return render_template('dashboard/usuarios/form.html', titulo='Cadastrar Usuário', modo='cadastrar', item=None, lista_funcoes=lista_funcoes)

@app.route('/usuarios/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def usuarios_alterar(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip() or None
        email = request.form.get('email', '').strip()
        celular = request.form.get('celular', '').strip()
        cep = request.form.get('cep', '').strip()
        logradouro = request.form.get('logradouro', '').strip()
        numero = request.form.get('numero', '').strip()
        complemento = request.form.get('complemento', '').strip()
        bairro = request.form.get('bairro', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()
        senha = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        funcao_id = request.form.get('funcao_id', '').strip()
        status = request.form.get('status', '').strip()

        if not all([nome, cpf, email, celular, estado]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

        existente = execute_one(
            '''SELECT id_usuario FROM usuarios
               WHERE (email = %s OR cpf = %s) AND id_usuario <> %s''',
            (email, cpf, id)
        )
        if existente:
            flash('E-mail ou CPF já cadastrados em outro usuário!', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

        if senha:
            if senha != confirmar_senha:
                flash('As senhas não conferem.', 'danger')
                return redirect(url_for('usuarios_alterar', id=id))
            if len(senha) < 8:
                flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
                return redirect(url_for('usuarios_alterar', id=id))

        try:
            if senha:
                execute_query(
                    """UPDATE usuarios SET
                       nome=%s, cpf=%s, data_nascimento=%s, email=%s, celular=%s,
                       cep=%s, logradouro=%s, numero=%s, complemento=%s, bairro=%s,
                       cidade=%s, estado=%s, senha=%s, status=%s, funcao_id=%s
                       WHERE id_usuario=%s""",
                    (nome, cpf, data_nascimento, email, celular,
                     cep, logradouro, numero, complemento, bairro, cidade, estado,
                     generate_password_hash(senha), status, funcao_id, id)
                )
            else:
                execute_query(
                    """UPDATE usuarios SET
                       nome=%s, cpf=%s, data_nascimento=%s, email=%s, celular=%s,
                       cep=%s, logradouro=%s, numero=%s, complemento=%s, bairro=%s,
                       cidade=%s, estado=%s, status=%s, funcao_id=%s
                       WHERE id_usuario=%s""",
                    (nome, cpf, data_nascimento, email, celular,
                     cep, logradouro, numero, complemento, bairro, cidade, estado,
                     status, funcao_id, id)
                )
            flash('Usuário alterado com sucesso', 'success')
            return redirect(url_for('usuarios_listar'))
        except Exception as e:
            flash(f'Erro ao alterar Usuário: {e}', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

    item = execute_one('SELECT * FROM usuarios WHERE id_usuario = %s', (id,))
    if not item:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('usuarios_listar'))

    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('dashboard/usuarios/form.html', titulo='Alterar Usuário', modo='alterar', item=item, lista_funcoes=lista_funcoes)

@app.route('/usuarios/visualizar/<int:id>')
@login_required
def usuarios_visualizar(id):
    item = execute_one(
        '''SELECT u.*, f.nome AS funcao
           FROM usuarios AS u
           INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
           WHERE u.id_usuario = %s''',
        (id,)
    )
    if not item:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('usuarios_listar'))
    return render_template('dashboard/usuarios/visualizar.html', item=item)

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def usuarios_excluir(id):
    try:
        execute_query('DELETE FROM usuarios WHERE id_usuario = %s', (id,))
        flash('Usuário excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {e}', 'danger')
    return redirect(url_for('usuarios_listar'))

@app.route('/usuarios/relatorio')
@login_required
def usuarios_relatorio():
    return render_template('dashboard/usuarios/relatorio.html')

# CRUD DE FUNÇÕES
@app.route('/funcoes/listar')
@login_required
def funcoes_listar():
    sql = '''
            SELECT id_funcao, nome, status, descricao, 
                   gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas,
                   criado_em, alterado_em
            FROM funcoes ORDER BY id_funcao DESC;
        '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('dashboard/funcoes/listar.html', dados=lista_dados)

@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
@login_required
def funcoes_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        status = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()
        gerenciar_funcoes = 1 if request.form.get('gerenciar_funcoes') else 0
        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_tarefas = 1 if request.form.get('gerenciar_tarefas') else 0

        if not nome:
            flash('O campo NOME é obrigatório', 'danger')
            return redirect(url_for('funcoes_cadastrar'))

        try:
            sql = '''INSERT INTO funcoes (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)
                     VALUES (%s, %s, %s, %s, %s, %s);'''
            execute_query(sql, (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas))
            flash(f'A função {nome} inserida com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))
        except Exception as e:
            flash(f'Erro ao salvar: {e}', 'danger')
            return redirect(url_for('funcoes_cadastrar'))
    
    return render_template('dashboard/funcoes/form.html', titulo='Cadastrar Função', modo='cadastrar', item=None)

# Lógica de atualizar as funções conectada ao BD
@app.route('/funcoes/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def funcoes_alterar(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        status = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()
        gerenciar_funcoes = 1 if request.form.get('gerenciar_funcoes') else 0
        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_tarefas = 1 if request.form.get('gerenciar_tarefas') else 0

        if not nome:
            flash('O campo NOME é obrigatório', 'danger')
            return redirect(url_for('funcoes_alterar', id=id))

        try:
            sql = '''UPDATE funcoes SET nome=%s, status=%s, descricao=%s, 
                     gerenciar_funcoes=%s, gerenciar_usuarios=%s, gerenciar_tarefas=%s
                     WHERE id_funcao=%s'''
            execute_query(sql, (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas, id))
            flash('Função alterada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))
        except Exception as e:
            flash(f'Erro ao alterar função: {e}', 'danger')
            return redirect(url_for('funcoes_alterar', id=id))

    item = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))
    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))

    return render_template('dashboard/funcoes/form.html', titulo='Alterar Função', modo='alterar', item=item)

# Lógica de visualização no BD
@app.route('/funcoes/visualizar/<int:id>')
@login_required
def funcoes_visualizar(id):
    item = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))
    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))
    return render_template('dashboard/funcoes/visualizar.html', item=item)

# Adicionada rota de exclusão que faltava
@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
@login_required
def funcoes_excluir(id):
    try:
        execute_query('DELETE FROM funcoes WHERE id_funcao = %s', (id,))
        flash('Função excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Não foi possível excluir a função (pode haver usuários atrelados). Erro: {e}', 'danger')
    return redirect(url_for('funcoes_listar'))

@app.route('/funcoes/relatorio')
@login_required
def funcoes_relatorio():
    return render_template('dashboard/funcoes/relatorio.html')

# CRUD DE TAREFAS 

# Listar tarefas extraídas direto do DB, buscando o nome do responsávl
@app.route('/tarefas/listar')
@login_required
def tarefas_listar():
    sql = '''
        SELECT t.*, u.nome AS responsavel 
        FROM tarefas t
        LEFT JOIN usuarios u ON t.responsavel_id = u.id_usuario
        ORDER BY t.id_tarefa DESC
    '''
    lista_tarefas = execute_query(sql, fetch=True)
    return render_template('dashboard/tarefas/listar.html', itens=lista_tarefas)

# Cadastro inserindo no BD e buscando usuários para popular o select
@app.route('/tarefas/cadastrar', methods=['GET', 'POST'])
@login_required
def tarefas_cadastrar():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        prioridade = request.form.get('prioridade', 'Média')
        status = request.form.get('status', 'Pendente')
        prazo = request.form.get('prazo', '').strip() or None
        responsavel_id = request.form.get('responsavel_id', '').strip() or None

        if not titulo:
            flash('O campo Título é obrigatório.', 'danger')
            return redirect(url_for('tarefas_cadastrar'))

        try:
            sql = '''INSERT INTO tarefas (titulo, descricao, prioridade, status, prazo, responsavel_id)
                     VALUES (%s, %s, %s, %s, %s, %s)'''
            execute_query(sql, (titulo, descricao, prioridade, status, prazo, responsavel_id))
            flash('Tarefa cadastrada com sucesso!', 'success')
            return redirect(url_for('tarefas_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar tarefa: {e}', 'danger')
            return redirect(url_for('tarefas_cadastrar'))
            
    lista_usuarios = execute_query('SELECT id_usuario, nome FROM usuarios', fetch=True)
    return render_template('dashboard/tarefas/form.html', titulo='Cadastrar Tarefa', modo='cadastrar', item=None, lista_usuarios=lista_usuarios)

# Alterar com os dados do BD
@app.route('/tarefas/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def tarefas_alterar(id):
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        prioridade = request.form.get('prioridade', 'Média')
        status = request.form.get('status', 'Pendente')
        prazo = request.form.get('prazo', '').strip() or None
        responsavel_id = request.form.get('responsavel_id', '').strip() or None

        if not titulo:
            flash('O campo Título é obrigatório.', 'danger')
            return redirect(url_for('tarefas_alterar', id=id))

        try:
            sql = '''UPDATE tarefas SET titulo=%s, descricao=%s, prioridade=%s, 
                     status=%s, prazo=%s, responsavel_id=%s WHERE id_tarefa=%s'''
            execute_query(sql, (titulo, descricao, prioridade, status, prazo, responsavel_id, id))
            flash('Tarefa alterada com sucesso!', 'success')
            return redirect(url_for('tarefas_listar'))
        except Exception as e:
            flash(f'Erro ao alterar tarefa: {e}', 'danger')
            return redirect(url_for('tarefas_alterar', id=id))

    item = execute_one('SELECT * FROM tarefas WHERE id_tarefa = %s', (id,))
    if not item:
        flash('Tarefa não encontrada.', 'danger')
        return redirect(url_for('tarefas_listar'))
        
    lista_usuarios = execute_query('SELECT id_usuario, nome FROM usuarios', fetch=True)
    return render_template('dashboard/tarefas/form.html', titulo='Alterar Tarefa', modo='alterar', item=item, lista_usuarios=lista_usuarios)

# Visualizar uma tarefa específica
@app.route('/tarefas/visualizar/<int:id>')
@login_required
def tarefas_visualizar(id):
    sql = '''
        SELECT t.*, u.nome AS responsavel 
        FROM tarefas t
        LEFT JOIN usuarios u ON t.responsavel_id = u.id_usuario
        WHERE t.id_tarefa = %s
    '''
    item = execute_one(sql, (id,))
    if not item:
        flash('Tarefa não encontrada.', 'danger')
        return redirect(url_for('tarefas_listar'))
    return render_template('dashboard/tarefas/visualizar.html', item=item)

# Rota de Excluir Tarefas
@app.route('/tarefas/excluir/<int:id>', methods=['POST'])
@login_required
def tarefas_excluir(id):
    try:
        execute_query('DELETE FROM tarefas WHERE id_tarefa = %s', (id,))
        flash('Tarefa excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir tarefa: {e}', 'danger')
    return redirect(url_for('tarefas_listar'))

@app.route('/tarefas/relatorio')
@login_required
def tarefas_relatorio():
    return render_template('dashboard/tarefas/relatorio.html')

# CRUD DA 1ª TABELA AMBIENTES
@app.route('/ambientes/listar')
@login_required
def ambientes_listar():
    lista = execute_query('SELECT * FROM ambientes ORDER BY id_ambiente DESC', fetch=True)
    return render_template('dashboard/ambientes/listar.html', dados=lista)

@app.route('/ambientes/cadastrar', methods=['GET', 'POST'])
@login_required
def ambientes_cadastrar():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        tipo = request.form.get('tipo', 'Interno')
        status = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()

        if not nome:
            flash('O campo Nome é obrigatório.', 'danger')
            return redirect(url_for('ambientes_cadastrar'))

        try:
            execute_query('INSERT INTO ambientes (nome, tipo, status, descricao) VALUES (%s, %s, %s, %s)', (nome, tipo, status, descricao))
            flash('Ambiente cadastrado com sucesso!', 'success')
            return redirect(url_for('ambientes_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar ambiente: {e}', 'danger')
            return redirect(url_for('ambientes_cadastrar'))

    return render_template('dashboard/ambientes/form.html', titulo='Cadastrar Ambiente', modo='cadastrar', item=None)

@app.route('/ambientes/visualizar/<int:id>')
@login_required
def ambientes_visualizar(id):
    item = execute_one('SELECT * FROM ambientes WHERE id_ambiente = %s', (id,))
    if not item:
        flash('Ambiente não encontrado.', 'danger')
        return redirect(url_for('ambientes_listar'))
    return render_template('dashboard/ambientes/visualizar.html', item=item)

@app.route('/ambientes/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def ambientes_alterar(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        tipo = request.form.get('tipo', 'Interno')
        status = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()

        if not nome:
            flash('O campo Nome é obrigatório.', 'danger')
            return redirect(url_for('ambientes_alterar', id=id))

        try:
            execute_query('UPDATE ambientes SET nome=%s, tipo=%s, status=%s, descricao=%s WHERE id_ambiente=%s', (nome, tipo, status, descricao, id))
            flash('Ambiente alterado com sucesso!', 'success')
            return redirect(url_for('ambientes_listar'))
        except Exception as e:
            flash(f'Erro ao alterar ambiente: {e}', 'danger')
            return redirect(url_for('ambientes_alterar', id=id))

    item = execute_one('SELECT * FROM ambientes WHERE id_ambiente = %s', (id,))
    return render_template('dashboard/ambientes/form.html', titulo='Alterar Ambiente', modo='alterar', item=item)

@app.route('/ambientes/excluir/<int:id>', methods=['POST'])
@login_required
def ambientes_excluir(id):
    try:
        execute_query('DELETE FROM ambientes WHERE id_ambiente = %s', (id,))
        flash('Ambiente excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir: {e}', 'danger')
    return redirect(url_for('ambientes_listar'))


#CRUD DA 2ª TABELA DESPESAS
@app.route('/despesas/listar')
@login_required
def despesas_listar():
    sql = '''
        SELECT d.*, u.nome AS usuario_nome 
        FROM despesas d 
        LEFT JOIN usuarios u ON d.usuario_id = u.id_usuario 
        ORDER BY d.vencimento ASC
    '''
    lista = execute_query(sql, fetch=True)
    return render_template('dashboard/despesas/listar.html', dados=lista)

@app.route('/despesas/cadastrar', methods=['GET', 'POST'])
@login_required
def despesas_cadastrar():
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        valor = request.form.get('valor', '').strip()
        vencimento = request.form.get('vencimento', '').strip()
        status = request.form.get('status', 'Pendente')
        usuario_id = request.form.get('usuario_id', '').strip()

        if not descricao or not valor or not vencimento or not usuario_id:
            flash('Preencha os campos obrigatórios.', 'danger')
            return redirect(url_for('despesas_cadastrar'))

        try:
            sql = 'INSERT INTO despesas (descricao, valor, vencimento, status, usuario_id) VALUES (%s, %s, %s, %s, %s)'
            execute_query(sql, (descricao, valor, vencimento, status, usuario_id))
            flash('Despesa lançada com sucesso!', 'success')
            return redirect(url_for('despesas_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar despesa: {e}', 'danger')
            return redirect(url_for('despesas_cadastrar'))

    usuarios = execute_query('SELECT id_usuario, nome FROM usuarios', fetch=True)
    return render_template('dashboard/despesas/form.html', titulo='Nova Despesa', modo='cadastrar', item=None, lista_usuarios=usuarios)

@app.route('/despesas/visualizar/<int:id>')
@login_required
def despesas_visualizar(id):
    sql = '''
        SELECT d.*, u.nome AS usuario_nome 
        FROM despesas d 
        LEFT JOIN usuarios u ON d.usuario_id = u.id_usuario 
        WHERE d.id_despesa = %s
    '''
    item = execute_one(sql, (id,))
    if not item:
        flash('Despesa não encontrada.', 'danger')
        return redirect(url_for('despesas_listar'))
    return render_template('dashboard/despesas/visualizar.html', item=item)

@app.route('/despesas/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def despesas_alterar(id):
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        valor = request.form.get('valor', '').strip()
        vencimento = request.form.get('vencimento', '').strip()
        status = request.form.get('status', 'Pendente')
        usuario_id = request.form.get('usuario_id', '').strip()

        if not descricao or not valor or not vencimento or not usuario_id:
            flash('Preencha os campos obrigatórios.', 'danger')
            return redirect(url_for('despesas_alterar', id=id))

        try:
            sql = 'UPDATE despesas SET descricao=%s, valor=%s, vencimento=%s, status=%s, usuario_id=%s WHERE id_despesa=%s'
            execute_query(sql, (descricao, valor, vencimento, status, usuario_id, id))
            flash('Despesa atualizada com sucesso!', 'success')
            return redirect(url_for('despesas_listar'))
        except Exception as e:
            flash(f'Erro ao alterar despesa: {e}', 'danger')
            return redirect(url_for('despesas_alterar', id=id))

    item = execute_one('SELECT * FROM despesas WHERE id_despesa = %s', (id,))
    usuarios = execute_query('SELECT id_usuario, nome FROM usuarios', fetch=True)
    return render_template('dashboard/despesas/form.html', titulo='Alterar Despesa', modo='alterar', item=item, lista_usuarios=usuarios)

@app.route('/despesas/excluir/<int:id>', methods=['POST'])
@login_required
def despesas_excluir(id):
    try:
        execute_query('DELETE FROM despesas WHERE id_despesa = %s', (id,))
        flash('Despesa excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir despesa: {e}', 'danger')
    return redirect(url_for('despesas_listar'))


if __name__ == '__main__':
    app.run(debug=True)