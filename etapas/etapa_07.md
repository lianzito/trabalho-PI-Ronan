# Etapa 07 - Listagem e Cadastro de Usuários

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Atualizar a rota `usuarios_listar` para buscar os dados reais do banco
- Atualizar o template `usuarios/listar.html` para exibir os dados dinâmicos
- Atualizar a rota `usuarios_cadastrar` para processar o formulário e gravar no banco
- Atualizar o template `usuarios/form.html` para pré-carregar a lista de funções do banco
- Instalar e usar o `werkzeug` para armazenar senhas com segurança (hash)
- Testar o fluxo completo de listagem e cadastro de usuários
- Enviar as alterações para o GitHub

---

## Como o fluxo vai funcionar

**Listagem:**
1. O usuário acessa `/usuarios/listar`
2. A rota executa um `SELECT` com `JOIN` entre `usuarios` e `funcoes` para trazer o nome da função junto
3. A lista é passada ao template e exibida na tabela linha por linha

**Cadastro:**
1. O usuário acessa `/usuarios/cadastrar` (GET)
2. A rota busca todas as funções do banco e passa ao template para popular o `<select>`
3. O usuário preenche o formulário e clica em Salvar (POST)
4. O Flask valida os dados, gera o hash da senha e executa o `INSERT`
5. Redireciona para a listagem com mensagem de sucesso

---

## 1. Instalando o werkzeug

O `werkzeug` é uma biblioteca que já vem junto com o Flask. Ela fornece funções para transformar a senha em um hash (texto embaralhado e irreversível) antes de salvar no banco, e para verificar se uma senha digitada corresponde ao hash armazenado.

> Nunca salve senhas em texto puro no banco de dados. Se o banco for comprometido, todas as senhas estariam expostas. O hash garante que mesmo o administrador do sistema não consiga ler a senha original.

Verifique se o `werkzeug` já está disponível no ambiente rodando a aplicação normalmente. Ele é instalado automaticamente como dependência do Flask, então nenhum comando extra é necessário.

---

## 2. Atualizando o app.py

### 2.1 Novo import

Localize no topo do `app.py` a linha de imports e adicione o import do `werkzeug` logo abaixo do import do Flask:

```python
# Adicionamos generate_password_hash para transformar a senha em hash antes de salvar,
# e check_password_hash para verificar a senha no login (usado na Etapa 09).
from werkzeug.security import generate_password_hash, check_password_hash
```

> Insira esta linha logo abaixo de `from flask import ...`, antes de `from db import ...`.

### 2.2 Atualizando a rota usuarios_listar

Localize no `app.py` a função `usuarios_listar` e substitua pelo código abaixo:

```python
@app.route('/usuarios/listar')
def usuarios_listar():
    # INNER JOIN traz o nome da função junto com os dados do usuário.
    # Sem o JOIN, teríamos apenas o id da função (ex: 1), não o nome (ex: Administrador).
    sql = '''
        SELECT
            u.id_usuario,
            u.nome,
            u.email,
            u.celular,
            f.nome AS funcao,
            u.status
        FROM usuarios AS u
        INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
        ORDER BY u.id_usuario DESC
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('dashboard/usuarios/listar.html', dados=lista_dados)
```

### 2.3 Atualizando a rota usuarios_cadastrar

Localize no `app.py` a função `usuarios_cadastrar` e substitua pelo código abaixo:

```python
@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
def usuarios_cadastrar():

    if request.method == 'POST':

        # Lê todos os campos do formulário enviado pelo usuário.
        nome            = request.form.get('nome', '').strip()
        cpf             = request.form.get('cpf', '').strip()
        # or None converte string vazia em None para campos opcionais no banco.
        data_nascimento = request.form.get('data_nascimento', '').strip() or None
        email           = request.form.get('email', '').strip()
        celular         = request.form.get('celular', '').strip()
        cep             = request.form.get('cep', '').strip()
        logradouro      = request.form.get('logradouro', '').strip()
        numero          = request.form.get('numero', '').strip()
        complemento     = request.form.get('complemento', '').strip()
        bairro          = request.form.get('bairro', '').strip()
        cidade          = request.form.get('cidade', '').strip()
        estado          = request.form.get('estado', '').strip()
        senha           = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        funcao_id       = request.form.get('funcao_id', '').strip()
        status          = request.form.get('status', '').strip()

        # Validação 1: campos obrigatórios não podem estar vazios.
        # all([...]) retorna True somente se todos os itens da lista forem verdadeiros.
        if not all([nome, cpf, email, celular, estado, senha]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        # Validação 2: as duas senhas digitadas precisam ser iguais.
        if senha != confirmar_senha:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        # Validação 3: a senha deve ter pelo menos 8 caracteres.
        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        # Validação 4: verifica se o e-mail ou CPF já existem no banco.
        # Usamos OR para pegar qualquer um dos dois que já esteja cadastrado.
        existente = execute_one(
            'SELECT nome FROM usuarios WHERE email = %s OR cpf = %s',
            (email, cpf)
        )
        if existente:
            flash('E-mail ou CPF já cadastrados.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        # Gera o hash da senha antes de salvar no banco.
        # generate_password_hash transforma ex: "minhasenha" em algo como
        # "scrypt:32768:8:1$abc...xyz" — irreversível e seguro.
        senha_hash = generate_password_hash(senha)

        try:
            sql = '''
                INSERT INTO usuarios
                    (nome, cpf, data_nascimento, email, celular,
                     cep, logradouro, numero, complemento, bairro,
                     cidade, estado, senha, status, funcao_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            dados = (
                nome, cpf, data_nascimento, email, celular,
                cep, logradouro, numero, complemento, bairro,
                cidade, estado, senha_hash, status, funcao_id
            )
            execute_query(sql, dados)
            flash(f'Usuário <b>{nome}</b> cadastrado com sucesso!', 'success')
            return redirect(url_for('usuarios_listar'))

        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

    # Se for GET: busca as funções disponíveis para popular o <select> do formulário.
    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('dashboard/usuarios/form.html',
                           titulo='Cadastrar Usuário',
                           modo='cadastrar',
                           item=None,
                           lista_funcoes=lista_funcoes)
```

### Arquivo app.py completo para conferência

```python
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import iniciar_bd, execute_query, execute_one

app = Flask(__name__)
app.secret_key = '123456'

iniciar_bd()


@app.context_processor
def injetar_usuario():
    return dict(usuario_logado=None)


# ── Rotas públicas ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    return redirect(url_for('login'))


@app.route('/cadastro')
def cadastro():
    return render_template('auth/register.html')


@app.route('/recuperar-senha')
def recuperar_senha():
    return render_template('auth/forgot_password.html')


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/home')
def home():
    return render_template('dashboard/home.html')


# ── Rotas de Funções ──────────────────────────────────────────────────────────

@app.route('/funcoes/listar')
def funcoes_listar():
    sql = '''
        SELECT
            id_funcao,
            nome,
            status,
            descricao,
            gerenciar_funcoes,
            gerenciar_usuarios,
            gerenciar_tarefas,
            criado_em,
            alterado_em
        FROM funcoes
        ORDER BY id_funcao DESC
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('dashboard/funcoes/listar.html', dados=lista_dados)


@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
def funcoes_cadastrar():
    if request.method == 'POST':
        nome               = request.form.get('nome', '').strip()
        status             = request.form.get('status', 'Ativo')
        descricao          = request.form.get('descricao', '').strip()
        gerenciar_funcoes  = 1 if request.form.get('gerenciar_funcoes')  else 0
        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_tarefas  = 1 if request.form.get('gerenciar_tarefas')  else 0

        if not nome:
            flash('O campo <b>Nome</b> é obrigatório.', 'danger')
            return redirect(url_for('funcoes_cadastrar'))

        try:
            sql = '''
                INSERT INTO funcoes
                    (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)
                VALUES
                    (%s, %s, %s, %s, %s, %s)
            '''
            dados = (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)
            execute_query(sql, dados)
            flash(f'Função <b>{nome}</b> cadastrada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar função: {e}', 'danger')
            return redirect(url_for('funcoes_cadastrar'))

    return render_template('dashboard/funcoes/form.html',
                           titulo='Cadastrar Função', modo='cadastrar', item=None)


@app.route('/funcoes/alterar/<int:id>', methods=['GET', 'POST'])
def funcoes_alterar(id):
    if request.method == 'POST':
        nome               = request.form.get('nome', '').strip()
        status             = request.form.get('status', 'Ativo')
        descricao          = request.form.get('descricao', '').strip()
        gerenciar_funcoes  = 1 if request.form.get('gerenciar_funcoes')  else 0
        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_tarefas  = 1 if request.form.get('gerenciar_tarefas')  else 0

        if not nome:
            flash('O campo <b>Nome</b> é obrigatório.', 'danger')
            return redirect(url_for('funcoes_alterar', id=id))

        try:
            sql = '''
                UPDATE funcoes SET
                    nome               = %s,
                    status             = %s,
                    descricao          = %s,
                    gerenciar_funcoes  = %s,
                    gerenciar_usuarios = %s,
                    gerenciar_tarefas  = %s
                WHERE id_funcao = %s
            '''
            dados = (nome, status, descricao,
                     gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas, id)
            execute_query(sql, dados)
            flash(f'Função <b>{nome}</b> alterada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))
        except Exception as e:
            flash(f'Erro ao alterar função: {e}', 'danger')
            return redirect(url_for('funcoes_alterar', id=id))

    item = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))
    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))

    return render_template('dashboard/funcoes/form.html',
                           titulo='Alterar Função', modo='alterar', item=item)


@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
def funcoes_excluir(id):
    try:
        execute_query('DELETE FROM funcoes WHERE id_funcao = %s', (id,))
        flash('Função excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir função: {e}', 'danger')
    return redirect(url_for('funcoes_listar'))


@app.route('/funcoes/visualizar/<int:id>')
def funcoes_visualizar(id):
    item = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))
    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))
    return render_template('dashboard/funcoes/visualizar.html', item=item)


@app.route('/funcoes/relatorio')
def funcoes_relatorio():
    return render_template('dashboard/funcoes/relatorio.html')


# ── Rotas de Usuários ─────────────────────────────────────────────────────────

@app.route('/usuarios/listar')
def usuarios_listar():
    sql = '''
        SELECT
            u.id_usuario,
            u.nome,
            u.email,
            u.celular,
            f.nome AS funcao,
            u.status
        FROM usuarios AS u
        INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
        ORDER BY u.id_usuario DESC
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('dashboard/usuarios/listar.html', dados=lista_dados)


@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
def usuarios_cadastrar():
    if request.method == 'POST':
        nome            = request.form.get('nome', '').strip()
        cpf             = request.form.get('cpf', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip() or None
        email           = request.form.get('email', '').strip()
        celular         = request.form.get('celular', '').strip()
        cep             = request.form.get('cep', '').strip()
        logradouro      = request.form.get('logradouro', '').strip()
        numero          = request.form.get('numero', '').strip()
        complemento     = request.form.get('complemento', '').strip()
        bairro          = request.form.get('bairro', '').strip()
        cidade          = request.form.get('cidade', '').strip()
        estado          = request.form.get('estado', '').strip()
        senha           = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        funcao_id       = request.form.get('funcao_id', '').strip()
        status          = request.form.get('status', '').strip()

        if not all([nome, cpf, email, celular, estado, senha]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        if senha != confirmar_senha:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        existente = execute_one(
            'SELECT nome FROM usuarios WHERE email = %s OR cpf = %s',
            (email, cpf)
        )
        if existente:
            flash('E-mail ou CPF já cadastrados.', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        senha_hash = generate_password_hash(senha)

        try:
            sql = '''
                INSERT INTO usuarios
                    (nome, cpf, data_nascimento, email, celular,
                     cep, logradouro, numero, complemento, bairro,
                     cidade, estado, senha, status, funcao_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            dados = (
                nome, cpf, data_nascimento, email, celular,
                cep, logradouro, numero, complemento, bairro,
                cidade, estado, senha_hash, status, funcao_id
            )
            execute_query(sql, dados)
            flash(f'Usuário <b>{nome}</b> cadastrado com sucesso!', 'success')
            return redirect(url_for('usuarios_listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('dashboard/usuarios/form.html',
                           titulo='Cadastrar Usuário',
                           modo='cadastrar',
                           item=None,
                           lista_funcoes=lista_funcoes)


@app.route('/usuarios/alterar/<int:id>', methods=['GET', 'POST'])
def usuarios_alterar(id):
    return render_template('dashboard/usuarios/form.html',
                           titulo='Alterar Usuário', modo='alterar', item=None,
                           lista_funcoes=[])


@app.route('/usuarios/visualizar/<int:id>')
def usuarios_visualizar(id):
    return render_template('dashboard/usuarios/visualizar.html')


@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def usuarios_excluir(id):
    return redirect(url_for('usuarios_listar'))


@app.route('/usuarios/relatorio')
def usuarios_relatorio():
    return render_template('dashboard/usuarios/relatorio.html')


# ── Rotas de Tarefas ──────────────────────────────────────────────────────────

@app.route('/tarefas/listar')
def tarefas_listar():
    return '<h1>Tarefas — em breve</h1>'


@app.route('/tarefas/cadastrar')
def tarefas_cadastrar():
    return '<h1>Cadastrar Tarefa — em breve</h1>'


@app.route('/tarefas/alterar/<int:id>')
def tarefas_alterar(id):
    return '<h1>Alterar Tarefa — em breve</h1>'


@app.route('/tarefas/visualizar/<int:id>')
def tarefas_visualizar(id):
    return '<h1>Visualizar Tarefa — em breve</h1>'


@app.route('/tarefas/relatorio')
def tarefas_relatorio():
    return '<h1>Relatório de Tarefas — em breve</h1>'


if __name__ == '__main__':
    app.run(debug=True)
```

---

## 3. Atualizando o template usuarios/listar.html

Abra o arquivo `templates/dashboard/usuarios/listar.html` e substitua todo o conteúdo pelo código abaixo:

```html
{% extends "base_dashboard.html" %}

{% block title %}Usuários — CasaGestor{% endblock %}
{% block page_title %}Usuários{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item active">Usuários</li>
        </ol>
    </nav>
    <a href="{{ url_for('usuarios_cadastrar') }}" class="btn btn-primary">
        <i class="bi bi-person-plus me-2"></i>Cadastrar Usuário
    </a>
</div>

<div class="card border-0 shadow-sm">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th>#</th>
                        <th>Nome</th>
                        <th>E-mail / Celular</th>
                        <th>Função</th>
                        <th>Status</th>
                        <th class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <!--
                        'dados' é a lista de dicionários retornada pelo SELECT com JOIN.
                        Cada 'item' tem: id_usuario, nome, email, celular, funcao, status.
                        O campo 'funcao' vem do JOIN com a tabela funcoes (aliás f.nome AS funcao).
                    -->
                    {% for item in dados %}
                    <tr>
                        <td>{{ item.id_usuario }}</td>
                        <td class="fw-semibold">{{ item.nome }}</td>
                        <td>
                            {{ item.email }}
                            <br>
                            <small class="text-muted">{{ item.celular }}</small>
                        </td>
                        <td>{{ item.funcao }}</td>
                        <td>
                            {% if item.status == 'Ativo' %}
                            <span class="badge bg-success">{{ item.status }}</span>
                            {% else %}
                            <span class="badge bg-secondary">{{ item.status }}</span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            <a href="{{ url_for('usuarios_visualizar', id=item.id_usuario) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('usuarios_alterar', id=item.id_usuario) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <!--
                                Mesmo padrão do modal de funções:
                                data-id e data-nome alimentam o modal via JavaScript.
                            -->
                            <button type="button" class="btn btn-sm btn-outline-danger"
                                    title="Excluir"
                                    data-bs-toggle="modal"
                                    data-bs-target="#modalExcluir"
                                    data-id="{{ item.id_usuario }}"
                                    data-nome="{{ item.nome }}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}

                    {% if not dados %}
                    <tr>
                        <td colspan="6" class="text-center text-muted py-4">
                            Nenhum usuário cadastrado ainda.
                            <a href="{{ url_for('usuarios_cadastrar') }}">Cadastrar agora</a>
                        </td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Modal de confirmação de exclusão -->
<div class="modal fade" id="modalExcluir" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>
                    Confirmar Exclusão
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                Tem certeza que deseja excluir o usuário
                <strong id="excluirNome"></strong>?
                <br>Esta ação não poderá ser desfeita.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary"
                        data-bs-dismiss="modal">Cancelar</button>
                <form id="formExcluir" method="POST">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-2"></i>Excluir
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script>
    // Preenche o modal com o nome e o id do usuário clicado.
    const modalExcluir = document.getElementById('modalExcluir');
    modalExcluir.addEventListener('show.bs.modal', function (event) {
        const botao = event.relatedTarget;
        const id    = botao.getAttribute('data-id');
        const nome  = botao.getAttribute('data-nome');
        document.getElementById('excluirNome').textContent = nome;
        document.getElementById('formExcluir').action = '/usuarios/excluir/' + id;
    });
</script>
{% endblock %}
```

### Template usuarios/listar.html completo para conferência

```html
{% extends "base_dashboard.html" %}

{% block title %}Usuários — CasaGestor{% endblock %}
{% block page_title %}Usuários{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item active">Usuários</li>
        </ol>
    </nav>
    <a href="{{ url_for('usuarios_cadastrar') }}" class="btn btn-primary">
        <i class="bi bi-person-plus me-2"></i>Cadastrar Usuário
    </a>
</div>

<div class="card border-0 shadow-sm">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th>#</th>
                        <th>Nome</th>
                        <th>E-mail / Celular</th>
                        <th>Função</th>
                        <th>Status</th>
                        <th class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in dados %}
                    <tr>
                        <td>{{ item.id_usuario }}</td>
                        <td class="fw-semibold">{{ item.nome }}</td>
                        <td>
                            {{ item.email }}
                            <br>
                            <small class="text-muted">{{ item.celular }}</small>
                        </td>
                        <td>{{ item.funcao }}</td>
                        <td>
                            {% if item.status == 'Ativo' %}
                            <span class="badge bg-success">{{ item.status }}</span>
                            {% else %}
                            <span class="badge bg-secondary">{{ item.status }}</span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            <a href="{{ url_for('usuarios_visualizar', id=item.id_usuario) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('usuarios_alterar', id=item.id_usuario) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button type="button" class="btn btn-sm btn-outline-danger"
                                    title="Excluir"
                                    data-bs-toggle="modal"
                                    data-bs-target="#modalExcluir"
                                    data-id="{{ item.id_usuario }}"
                                    data-nome="{{ item.nome }}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}

                    {% if not dados %}
                    <tr>
                        <td colspan="6" class="text-center text-muted py-4">
                            Nenhum usuário cadastrado ainda.
                            <a href="{{ url_for('usuarios_cadastrar') }}">Cadastrar agora</a>
                        </td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="modal fade" id="modalExcluir" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>
                    Confirmar Exclusão
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                Tem certeza que deseja excluir o usuário
                <strong id="excluirNome"></strong>?
                <br>Esta ação não poderá ser desfeita.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary"
                        data-bs-dismiss="modal">Cancelar</button>
                <form id="formExcluir" method="POST">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-2"></i>Excluir
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

{% endblock %}

{% block scripts %}
<script>
    const modalExcluir = document.getElementById('modalExcluir');
    modalExcluir.addEventListener('show.bs.modal', function (event) {
        const botao = event.relatedTarget;
        const id    = botao.getAttribute('data-id');
        const nome  = botao.getAttribute('data-nome');
        document.getElementById('excluirNome').textContent = nome;
        document.getElementById('formExcluir').action = '/usuarios/excluir/' + id;
    });
</script>
{% endblock %}
```

---

## 4. Atualizando o template usuarios/form.html

O formulário de usuário precisa ser atualizado para popular o `<select>` de funções com os dados reais do banco, no lugar das opções fixas que escrevemos na Etapa 04.

Abra o arquivo `templates/dashboard/usuarios/form.html`. Localize o bloco do `<select>` de funções (Card 3, campo Função) e substitua apenas este trecho:

**Trecho antigo** (opções fixas):
```html
<select name="funcao_id" class="form-select" required>
    <option value="">Selecione uma função</option>
    <option value="1">Administrador</option>
    <option value="2">Usuário</option>
</select>
```

**Trecho novo** (opções dinâmicas do banco):
```html
<select name="funcao_id" class="form-select" required>
    <option value="">Selecione uma função</option>
    <!--
        lista_funcoes é passada pela rota via render_template.
        O loop percorre cada função e cria uma <option> para ela.
        'selected' marca a opção correta quando estamos no modo alterar.
    -->
    {% for f in lista_funcoes %}
    <option value="{{ f.id_funcao }}"
        {{ 'selected' if item and item.funcao_id == f.id_funcao else '' }}>
        {{ f.nome }}
    </option>
    {% endfor %}
</select>
```

### Template usuarios/form.html completo para conferência

```html
{% extends "base_dashboard.html" %}

{% block title %}{{ titulo }} — CasaGestor{% endblock %}
{% block page_title %}{{ titulo }}{% endblock %}

{% block content %}

<div class="mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('usuarios_listar') }}">Usuários</a></li>
            <li class="breadcrumb-item active">{{ titulo }}</li>
        </ol>
    </nav>
</div>

<form action="{{ url_for('usuarios_alterar', id=item.id_usuario) if modo == 'alterar' else url_for('usuarios_cadastrar') }}" method="POST">
    <div class="row g-4">

        <!-- Card 1: Dados Pessoais -->
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-primary text-white fw-semibold">
                    <i class="bi bi-person-fill me-2"></i>Dados Pessoais
                </div>
                <div class="card-body p-4">
                    <div class="row g-3">
                        <div class="col-12">
                            <label class="form-label fw-semibold">
                                Nome Completo <span class="text-danger">*</span>
                            </label>
                            <input type="text" name="nome" class="form-control"
                                   value="{{ item.nome if item else '' }}"
                                   placeholder="Nome completo" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                CPF <span class="text-danger">*</span>
                            </label>
                            <input type="text" name="cpf" class="form-control"
                                   value="{{ item.cpf if item else '' }}"
                                   placeholder="000.000.000-00" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Data de Nascimento</label>
                            <input type="date" name="data_nascimento" class="form-control"
                                   value="{{ item.data_nascimento if item else '' }}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                E-mail <span class="text-danger">*</span>
                            </label>
                            <input type="email" name="email" class="form-control"
                                   value="{{ item.email if item else '' }}"
                                   placeholder="seu@email.com" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Celular <span class="text-danger">*</span>
                            </label>
                            <input type="text" name="celular" class="form-control"
                                   value="{{ item.celular if item else '' }}"
                                   placeholder="(00) 00000-0000" required>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Card 2: Endereço -->
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-secondary text-white fw-semibold">
                    <i class="bi bi-geo-alt-fill me-2"></i>Endereço
                </div>
                <div class="card-body p-4">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label fw-semibold">CEP</label>
                            <input type="text" name="cep" class="form-control"
                                   value="{{ item.cep if item else '' }}"
                                   placeholder="00000-000">
                        </div>
                        <div class="col-md-8">
                            <label class="form-label fw-semibold">Logradouro</label>
                            <input type="text" name="logradouro" class="form-control"
                                   value="{{ item.logradouro if item else '' }}"
                                   placeholder="Rua, Avenida, Travessa…">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label fw-semibold">Número</label>
                            <input type="text" name="numero" class="form-control"
                                   value="{{ item.numero if item else '' }}"
                                   placeholder="Nº">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold">Complemento</label>
                            <input type="text" name="complemento" class="form-control"
                                   value="{{ item.complemento if item else '' }}"
                                   placeholder="Apto, Bloco…">
                        </div>
                        <div class="col-md-5">
                            <label class="form-label fw-semibold">Bairro</label>
                            <input type="text" name="bairro" class="form-control"
                                   value="{{ item.bairro if item else '' }}"
                                   placeholder="Bairro">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Cidade</label>
                            <input type="text" name="cidade" class="form-control"
                                   value="{{ item.cidade if item else '' }}"
                                   placeholder="Cidade">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label fw-semibold">
                                Estado <span class="text-danger">*</span>
                            </label>
                            <select name="estado" class="form-select" required>
                                <option value="">UF</option>
                                {% for uf in ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA',
                                              'MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN',
                                              'RS','RO','RR','SC','SP','SE','TO'] %}
                                <option value="{{ uf }}"
                                    {{ 'selected' if item and item.estado == uf else '' }}>
                                    {{ uf }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label fw-semibold">País</label>
                            <input type="text" name="pais" class="form-control"
                                   value="Brasil" readonly>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Card 3: Dados de Acesso -->
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-dark text-white fw-semibold">
                    <i class="bi bi-lock-fill me-2"></i>Dados de Acesso
                </div>
                <div class="card-body p-4">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Senha <span class="text-danger">*</span>
                            </label>
                            <!--
                                No modo alterar, a senha não é obrigatória:
                                se deixar em branco, a senha atual é mantida.
                                O atributo required só é adicionado no modo cadastrar.
                            -->
                            <input type="password" name="senha" class="form-control"
                                   placeholder="Mínimo 8 caracteres"
                                   {{ 'required' if not item else '' }}>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Confirmar Senha <span class="text-danger">*</span>
                            </label>
                            <input type="password" name="confirmar_senha" class="form-control"
                                   placeholder="Repita a senha"
                                   {{ 'required' if not item else '' }}>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Função <span class="text-danger">*</span>
                            </label>
                            <select name="funcao_id" class="form-select" required>
                                <option value="">Selecione uma função</option>
                                {% for f in lista_funcoes %}
                                <option value="{{ f.id_funcao }}"
                                    {{ 'selected' if item and item.funcao_id == f.id_funcao else '' }}>
                                    {{ f.nome }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Status</label>
                            <select name="status" class="form-select">
                                <option value="Ativo"
                                    {{ 'selected' if not item or item.status == 'Ativo' else '' }}>
                                    Ativo
                                </option>
                                <option value="Inativo"
                                    {{ 'selected' if item and item.status == 'Inativo' else '' }}>
                                    Inativo
                                </option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Botões de ação -->
        <div class="col-12 d-flex justify-content-between">
            <a href="{{ url_for('usuarios_listar') }}" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-left me-2"></i>Cancelar
            </a>
            <button type="submit" class="btn btn-primary px-4">
                <i class="bi bi-check-lg me-2"></i>Salvar
            </button>
        </div>

    </div>
</form>

{% endblock %}
```

---

## 5. Testando o fluxo completo

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

### Teste 1: Banco vazio

Acesse `/usuarios/listar`. A mensagem "Nenhum usuário cadastrado ainda" deve aparecer.

> Atenção: para cadastrar um usuário é necessário ter pelo menos uma função cadastrada. Se ainda não criou nenhuma, acesse `/funcoes/cadastrar` primeiro e crie a função "Administrador".

### Teste 2: Cadastrar um usuário

1. Acesse `/usuarios/cadastrar`
2. Verifique que o `<select>` de Função exibe as funções reais do banco
3. Preencha todos os campos obrigatórios (marcados com `*`)
4. Clique em **Salvar**
5. Você deve ser redirecionado para `/usuarios/listar` com a mensagem de sucesso
6. O usuário deve aparecer na tabela com o nome da função correto

### Teste 3: Validações

Tente as situações abaixo e confirme que cada uma exibe a mensagem de erro correta:

| Situação | Mensagem esperada |
|---|---|
| Deixar o nome em branco | "Preencha todos os campos obrigatórios." |
| Senhas diferentes | "As senhas não conferem." |
| Senha com menos de 8 caracteres | "A senha deve ter pelo menos 8 caracteres." |
| E-mail ou CPF já cadastrados | "E-mail ou CPF já cadastrados." |

### Teste 4: Verificar o hash da senha no Workbench

Após cadastrar um usuário, execute no MySQL Workbench:

```sql
USE casa_gestor;
SELECT nome, email, senha FROM usuarios;
```

O campo `senha` deve exibir um texto longo e embaralhado (o hash), nunca a senha original. Isso confirma que o armazenamento está seguro.

---

## 6. Enviando as alterações para o GitHub

```
git add .
git commit -m "Etapa 07: listagem e cadastro de usuários com BD"
git push
```

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| Import werkzeug | Adicionado `generate_password_hash` e `check_password_hash` |
| usuarios_listar | Atualizada com SELECT + JOIN para trazer o nome da função |
| usuarios_cadastrar | Atualizada com validações, hash de senha e INSERT |
| usuarios/listar.html | Atualizado com dados dinâmicos, modal de exclusão e JavaScript |
| usuarios/form.html | Atualizado com `<select>` dinâmico de funções e pré-preenchimento |
| Testes | Listagem, cadastro, validações e hash de senha verificados |
| Workbench | Hash da senha conferido na tabela `usuarios` |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

**Próxima etapa:** Implementação da alteração, visualização e exclusão de usuários.
