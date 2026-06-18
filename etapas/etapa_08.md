# Etapa 08 - Alteração, Visualização e Exclusão de Usuários

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Atualizar a rota `usuarios_visualizar` para buscar e exibir um registro real do banco
- Atualizar o template `usuarios/visualizar.html` para exibir dados dinâmicos
- Atualizar a rota `usuarios_alterar` para carregar os dados atuais e processar o formulário de edição
- Implementar a lógica de senha opcional na alteração (só atualiza se o campo for preenchido)
- Atualizar a rota `usuarios_excluir` para deletar o registro do banco
- Testar o fluxo completo de visualização, alteração e exclusão de usuários
- Enviar as alterações para o GitHub

---

## Como o fluxo vai funcionar

**Visualização:**
1. O usuário clica no ícone de olho na listagem
2. O Flask recebe o `id` pela URL e executa um `SELECT` com `JOIN` para trazer também o nome da função
3. Os dados são passados ao template como `item` e exibidos na página

**Alteração:**
1. GET: o Flask busca o registro pelo `id`, busca as funções disponíveis e pré-preenche o formulário
2. POST: o Flask lê os novos valores e decide se atualiza a senha ou não
3. Se a senha foi preenchida, valida e gera novo hash antes de salvar
4. Se a senha foi deixada em branco, executa o `UPDATE` sem tocar na coluna de senha
5. Redireciona para a listagem com mensagem de sucesso

**Exclusão:**
1. O formulário oculto do modal envia POST para `/usuarios/excluir/<id>`
2. O Flask executa o `DELETE` e redireciona para a listagem

---

## 1. Atualizando o app.py

### 1.1 Atualizando a rota usuarios_visualizar

Localize no `app.py` a função `usuarios_visualizar` e substitua pelo código abaixo:

```python
@app.route('/usuarios/visualizar/<int:id>')
def usuarios_visualizar(id):
    # O JOIN traz o nome da função junto, para não exibir apenas o id.
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
```

### 1.2 Atualizando a rota usuarios_alterar

Localize no `app.py` a função `usuarios_alterar` e substitua pelo código abaixo:

```python
@app.route('/usuarios/alterar/<int:id>', methods=['GET', 'POST'])
def usuarios_alterar(id):

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

        # Validação dos campos obrigatórios (sem senha, pois ela é opcional na edição).
        if not all([nome, cpf, email, celular, estado]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

        # Verifica se o e-mail ou CPF já pertencem a OUTRO usuário.
        # O AND id_usuario <> %s exclui o próprio registro da verificação,
        # pois um usuário pode manter seu próprio e-mail e CPF ao editar.
        existente = execute_one(
            '''SELECT id_usuario FROM usuarios
               WHERE (email = %s OR cpf = %s) AND id_usuario <> %s''',
            (email, cpf, id)
        )
        if existente:
            flash('E-mail ou CPF já cadastrados em outro usuário.', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

        # Validação da senha: só executa se o campo foi preenchido.
        # Se deixar em branco, a senha atual do banco é mantida.
        if senha:
            if senha != confirmar_senha:
                flash('As senhas não conferem.', 'danger')
                return redirect(url_for('usuarios_alterar', id=id))
            if len(senha) < 8:
                flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
                return redirect(url_for('usuarios_alterar', id=id))

        try:
            if senha:
                # Se uma nova senha foi informada, inclui a coluna senha no UPDATE
                # e salva o hash gerado.
                sql = '''
                    UPDATE usuarios SET
                        nome            = %s,
                        cpf             = %s,
                        data_nascimento = %s,
                        email           = %s,
                        celular         = %s,
                        cep             = %s,
                        logradouro      = %s,
                        numero          = %s,
                        complemento     = %s,
                        bairro          = %s,
                        cidade          = %s,
                        estado          = %s,
                        senha           = %s,
                        status          = %s,
                        funcao_id       = %s
                    WHERE id_usuario = %s
                '''
                dados = (
                    nome, cpf, data_nascimento, email, celular,
                    cep, logradouro, numero, complemento, bairro,
                    cidade, estado,
                    generate_password_hash(senha),
                    status, funcao_id, id
                )
            else:
                # Se a senha ficou em branco, executa o UPDATE sem a coluna senha.
                # A senha antiga permanece intacta no banco.
                sql = '''
                    UPDATE usuarios SET
                        nome            = %s,
                        cpf             = %s,
                        data_nascimento = %s,
                        email           = %s,
                        celular         = %s,
                        cep             = %s,
                        logradouro      = %s,
                        numero          = %s,
                        complemento     = %s,
                        bairro          = %s,
                        cidade          = %s,
                        estado          = %s,
                        status          = %s,
                        funcao_id       = %s
                    WHERE id_usuario = %s
                '''
                dados = (
                    nome, cpf, data_nascimento, email, celular,
                    cep, logradouro, numero, complemento, bairro,
                    cidade, estado,
                    status, funcao_id, id
                )

            execute_query(sql, dados)
            flash(f'Usuário <b>{nome}</b> alterado com sucesso!', 'success')
            return redirect(url_for('usuarios_listar'))

        except Exception as e:
            flash(f'Erro ao alterar usuário: {e}', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

    # Se for GET: busca o registro e a lista de funções para montar o formulário.
    item = execute_one('SELECT * FROM usuarios WHERE id_usuario = %s', (id,))
    if not item:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('usuarios_listar'))

    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('dashboard/usuarios/form.html',
                           titulo='Alterar Usuário',
                           modo='alterar',
                           item=item,
                           lista_funcoes=lista_funcoes)
```

### 1.3 Atualizando a rota usuarios_excluir

Localize no `app.py` a função `usuarios_excluir` e substitua pelo código abaixo:

```python
@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def usuarios_excluir(id):
    try:
        execute_query('DELETE FROM usuarios WHERE id_usuario = %s', (id,))
        flash('Usuário excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {e}', 'danger')
    return redirect(url_for('usuarios_listar'))
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

        if not all([nome, cpf, email, celular, estado]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

        existente = execute_one(
            '''SELECT id_usuario FROM usuarios
               WHERE (email = %s OR cpf = %s) AND id_usuario <> %s''',
            (email, cpf, id)
        )
        if existente:
            flash('E-mail ou CPF já cadastrados em outro usuário.', 'danger')
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
                sql = '''
                    UPDATE usuarios SET
                        nome            = %s,
                        cpf             = %s,
                        data_nascimento = %s,
                        email           = %s,
                        celular         = %s,
                        cep             = %s,
                        logradouro      = %s,
                        numero          = %s,
                        complemento     = %s,
                        bairro          = %s,
                        cidade          = %s,
                        estado          = %s,
                        senha           = %s,
                        status          = %s,
                        funcao_id       = %s
                    WHERE id_usuario = %s
                '''
                dados = (
                    nome, cpf, data_nascimento, email, celular,
                    cep, logradouro, numero, complemento, bairro,
                    cidade, estado,
                    generate_password_hash(senha),
                    status, funcao_id, id
                )
            else:
                sql = '''
                    UPDATE usuarios SET
                        nome            = %s,
                        cpf             = %s,
                        data_nascimento = %s,
                        email           = %s,
                        celular         = %s,
                        cep             = %s,
                        logradouro      = %s,
                        numero          = %s,
                        complemento     = %s,
                        bairro          = %s,
                        cidade          = %s,
                        estado          = %s,
                        status          = %s,
                        funcao_id       = %s
                    WHERE id_usuario = %s
                '''
                dados = (
                    nome, cpf, data_nascimento, email, celular,
                    cep, logradouro, numero, complemento, bairro,
                    cidade, estado,
                    status, funcao_id, id
                )

            execute_query(sql, dados)
            flash(f'Usuário <b>{nome}</b> alterado com sucesso!', 'success')
            return redirect(url_for('usuarios_listar'))

        except Exception as e:
            flash(f'Erro ao alterar usuário: {e}', 'danger')
            return redirect(url_for('usuarios_alterar', id=id))

    item = execute_one('SELECT * FROM usuarios WHERE id_usuario = %s', (id,))
    if not item:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('usuarios_listar'))

    lista_funcoes = execute_query('SELECT id_funcao, nome FROM funcoes', fetch=True)
    return render_template('dashboard/usuarios/form.html',
                           titulo='Alterar Usuário',
                           modo='alterar',
                           item=item,
                           lista_funcoes=lista_funcoes)


@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def usuarios_excluir(id):
    try:
        execute_query('DELETE FROM usuarios WHERE id_usuario = %s', (id,))
        flash('Usuário excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {e}', 'danger')
    return redirect(url_for('usuarios_listar'))


@app.route('/usuarios/visualizar/<int:id>')
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

## 2. Atualizando o template usuarios/visualizar.html

Abra o arquivo `templates/dashboard/usuarios/visualizar.html` e substitua todo o conteúdo pelo código abaixo:

```html
{% extends "base_dashboard.html" %}

{% block title %}Visualizar Usuário — CasaGestor{% endblock %}
{% block page_title %}Visualizar Usuário{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('usuarios_listar') }}">Usuários</a></li>
            <li class="breadcrumb-item active">Visualizar</li>
        </ol>
    </nav>
    <!--
        item.id_usuario é o ID do registro buscado no banco.
        Passamos ele para a rota de alteração para que o formulário
        saiba qual registro carregar.
    -->
    <a href="{{ url_for('usuarios_alterar', id=item.id_usuario) }}" class="btn btn-warning">
        <i class="bi bi-pencil me-2"></i>Editar
    </a>
</div>

<!-- Card com os dados principais do usuário -->
<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-person-fill me-2 text-primary"></i>Dados do Usuário
    </div>
    <div class="card-body p-4">
        <div class="row g-4">

            <div class="col-md-6">
                <p class="text-muted mb-1 small">Nome Completo</p>
                <!-- {{ item.nome }} exibe o valor do campo retornado pelo banco. -->
                <p class="fw-semibold mb-0">{{ item.nome }}</p>
            </div>

            <div class="col-md-6">
                <p class="text-muted mb-1 small">E-mail</p>
                <p class="fw-semibold mb-0">{{ item.email }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">CPF</p>
                <p class="fw-semibold mb-0">{{ item.cpf }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Celular</p>
                <p class="fw-semibold mb-0">{{ item.celular }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Data de Nascimento</p>
                <!--
                    item.data_nascimento pode ser None se o campo foi deixado em branco.
                    O 'or' exibe um traço neste caso para não deixar o campo vazio.
                -->
                <p class="fw-semibold mb-0">{{ item.data_nascimento or '—' }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Função</p>
                <!--
                    item.funcao vem do JOIN com a tabela funcoes (f.nome AS funcao).
                -->
                <p class="fw-semibold mb-0">{{ item.funcao }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Status</p>
                {% if item.status == 'Ativo' %}
                <span class="badge bg-success">{{ item.status }}</span>
                {% else %}
                <span class="badge bg-secondary">{{ item.status }}</span>
                {% endif %}
            </div>

        </div>
    </div>
</div>

<!-- Card com o endereço do usuário -->
<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-geo-alt-fill me-2 text-primary"></i>Endereço
    </div>
    <div class="card-body p-4">
        <div class="row g-4">

            <div class="col-md-3">
                <p class="text-muted mb-1 small">CEP</p>
                <p class="fw-semibold mb-0">{{ item.cep or '—' }}</p>
            </div>

            <div class="col-md-6">
                <p class="text-muted mb-1 small">Logradouro</p>
                <p class="fw-semibold mb-0">{{ item.logradouro or '—' }}</p>
            </div>

            <div class="col-md-3">
                <p class="text-muted mb-1 small">Número</p>
                <p class="fw-semibold mb-0">{{ item.numero or '—' }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Complemento</p>
                <p class="fw-semibold mb-0">{{ item.complemento or '—' }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Bairro</p>
                <p class="fw-semibold mb-0">{{ item.bairro or '—' }}</p>
            </div>

            <div class="col-md-4">
                <p class="text-muted mb-1 small">Cidade / Estado</p>
                <p class="fw-semibold mb-0">
                    {{ item.cidade or '—' }} / {{ item.estado }}
                </p>
            </div>

        </div>
    </div>
</div>

<a href="{{ url_for('usuarios_listar') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-2"></i>Voltar
</a>

{% endblock %}
```

### Template usuarios/visualizar.html completo para conferência

```html
{% extends "base_dashboard.html" %}

{% block title %}Visualizar Usuário — CasaGestor{% endblock %}
{% block page_title %}Visualizar Usuário{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('usuarios_listar') }}">Usuários</a></li>
            <li class="breadcrumb-item active">Visualizar</li>
        </ol>
    </nav>
    <a href="{{ url_for('usuarios_alterar', id=item.id_usuario) }}" class="btn btn-warning">
        <i class="bi bi-pencil me-2"></i>Editar
    </a>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-person-fill me-2 text-primary"></i>Dados do Usuário
    </div>
    <div class="card-body p-4">
        <div class="row g-4">
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Nome Completo</p>
                <p class="fw-semibold mb-0">{{ item.nome }}</p>
            </div>
            <div class="col-md-6">
                <p class="text-muted mb-1 small">E-mail</p>
                <p class="fw-semibold mb-0">{{ item.email }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">CPF</p>
                <p class="fw-semibold mb-0">{{ item.cpf }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Celular</p>
                <p class="fw-semibold mb-0">{{ item.celular }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Data de Nascimento</p>
                <p class="fw-semibold mb-0">{{ item.data_nascimento or '—' }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Função</p>
                <p class="fw-semibold mb-0">{{ item.funcao }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Status</p>
                {% if item.status == 'Ativo' %}
                <span class="badge bg-success">{{ item.status }}</span>
                {% else %}
                <span class="badge bg-secondary">{{ item.status }}</span>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-geo-alt-fill me-2 text-primary"></i>Endereço
    </div>
    <div class="card-body p-4">
        <div class="row g-4">
            <div class="col-md-3">
                <p class="text-muted mb-1 small">CEP</p>
                <p class="fw-semibold mb-0">{{ item.cep or '—' }}</p>
            </div>
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Logradouro</p>
                <p class="fw-semibold mb-0">{{ item.logradouro or '—' }}</p>
            </div>
            <div class="col-md-3">
                <p class="text-muted mb-1 small">Número</p>
                <p class="fw-semibold mb-0">{{ item.numero or '—' }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Complemento</p>
                <p class="fw-semibold mb-0">{{ item.complemento or '—' }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Bairro</p>
                <p class="fw-semibold mb-0">{{ item.bairro or '—' }}</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Cidade / Estado</p>
                <p class="fw-semibold mb-0">{{ item.cidade or '—' }} / {{ item.estado }}</p>
            </div>
        </div>
    </div>
</div>

<a href="{{ url_for('usuarios_listar') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-2"></i>Voltar
</a>

{% endblock %}
```

---

## 3. Testando o fluxo completo

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

### Teste 1: Visualizar

1. Acesse `/usuarios/listar` e clique no ícone de olho de qualquer usuário
2. A página deve exibir todos os dados reais do banco, incluindo o nome da função (não o id)
3. Campos opcionais vazios (ex: CEP, bairro) devem exibir um traço no lugar de ficar em branco
4. Clique em **Editar** e confirme que vai para o formulário de alteração

### Teste 2: Alterar sem trocar a senha

1. Na listagem, clique no ícone de lápis de qualquer usuário
2. O formulário deve abrir com todos os campos pré-preenchidos
3. O `<select>` de Função deve mostrar a função atual selecionada
4. Altere o celular, deixe os campos de senha em branco e clique em **Salvar**
5. Confirme a mensagem de sucesso e veja o celular atualizado na listagem
6. No MySQL Workbench execute `SELECT nome, senha FROM usuarios` e confirme que o hash da senha não mudou

### Teste 3: Alterar trocando a senha

1. Abra o formulário de alteração de qualquer usuário
2. Preencha os campos de nova senha com uma senha diferente
3. Clique em **Salvar**
4. No MySQL Workbench execute `SELECT nome, senha FROM usuarios` e confirme que o hash da senha é diferente do anterior

### Teste 4: Validação de e-mail ou CPF duplicado

1. Abra o formulário de alteração de um usuário
2. Troque o e-mail pelo e-mail de outro usuário já cadastrado
3. Clique em **Salvar**
4. A mensagem "E-mail ou CPF já cadastrados em outro usuário." deve aparecer

### Teste 5: Excluir

1. Crie um usuário temporário (ex: nome "Teste", qualquer e-mail e CPF válidos)
2. Na listagem, clique no ícone de lixeira desse usuário
3. Confirme que o modal mostra o nome correto
4. Clique em **Excluir** e confirme que o usuário sumiu da listagem

### Verificando no Workbench

```sql
USE casa_gestor;
SELECT id_usuario, nome, email, funcao_id, status FROM usuarios;
```

---

## 4. Enviando as alterações para o GitHub

```
git add .
git commit -m "Etapa 08: visualizar, alterar e excluir usuários"
git push
```

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| usuarios_visualizar | Atualizada com SELECT + JOIN para trazer o nome da função |
| usuarios_alterar | Atualizada com dois UPDATE distintos (com e sem senha) e validação de duplicidade excluindo o próprio registro |
| usuarios_excluir | Atualizada com DELETE real no banco |
| usuarios/visualizar.html | Atualizado com dados dinâmicos, dois cards e tratamento de campos vazios com `or '—'` |
| Testes | Visualização, alteração com e sem senha, duplicidade e exclusão verificados |
| Workbench | Dados e hash de senha conferidos na tabela `usuarios` |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

**Próxima etapa:** Implementação do login, logout, proteção de rotas e criação automática do administrador padrão.
