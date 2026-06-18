# Etapa 06 - Alteração, Visualização e Exclusão de Funções

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Atualizar a rota `funcoes_visualizar` para buscar e exibir um registro real do banco
- Atualizar o template `funcoes/visualizar.html` para exibir dados dinâmicos
- Atualizar a rota `funcoes_alterar` para carregar os dados atuais e processar o formulário de edição
- Atualizar o template `funcoes/form.html` para pré-preencher os campos com os dados existentes
- Criar a rota `funcoes_excluir` para deletar um registro do banco
- Adicionar o modal de confirmação de exclusão no template `funcoes/listar.html`
- Testar o fluxo completo de visualização, alteração e exclusão
- Enviar as alterações para o GitHub

---

## Como o fluxo vai funcionar

**Visualização:**
1. O usuário clica no ícone de olho em um registro da listagem
2. O Flask recebe o `id` pela URL (ex: `/funcoes/visualizar/2`)
3. A rota executa um `SELECT` buscando apenas aquele registro pelo `id`
4. Os dados são passados ao template como a variável `item`
5. O template exibe os campos de `item` diretamente

**Alteração:**
1. O usuário clica no ícone de lápis (GET): o Flask busca o registro pelo `id` e pré-preenche o formulário
2. O usuário edita os campos e clica em Salvar (POST): o Flask lê os novos valores, valida e executa um `UPDATE`
3. Redireciona para a listagem com mensagem de sucesso

**Exclusão:**
1. O usuário clica no ícone de lixeira: um modal de confirmação aparece
2. O usuário confirma: um formulário oculto envia um POST para `/funcoes/excluir/<id>`
3. O Flask executa um `DELETE` e redireciona para a listagem

---

## 1. Atualizando o app.py

### 1.1 Atualizando a rota funcoes_visualizar

Localize no `app.py` a função `funcoes_visualizar` e substitua pelo código abaixo:

```python
@app.route('/funcoes/visualizar/<int:id>')
def funcoes_visualizar(id):
    # execute_one retorna apenas a primeira linha encontrada, ou None.
    # Passamos o id como parâmetro seguro para evitar SQL Injection.
    item = execute_one(
        'SELECT * FROM funcoes WHERE id_funcao = %s', (id,)
    )

    # Se nenhum registro for encontrado com aquele id,
    # exibe uma mensagem de erro e volta para a listagem.
    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))

    # Passa o dicionário 'item' para o template.
    # No template, acessamos os campos com item.nome, item.status, etc.
    return render_template('dashboard/funcoes/visualizar.html', item=item)
```

### 1.2 Atualizando a rota funcoes_alterar

Localize no `app.py` a função `funcoes_alterar` e substitua pelo código abaixo:

```python
@app.route('/funcoes/alterar/<int:id>', methods=['GET', 'POST'])
def funcoes_alterar(id):

    if request.method == 'POST':
        # Lê os novos valores enviados pelo formulário.
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
            # A tupla de dados deve terminar com o 'id',
            # pois ele corresponde ao último %s do WHERE.
            dados = (nome, status, descricao,
                     gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas,
                     id)

            execute_query(sql, dados)
            flash(f'Função <b>{nome}</b> alterada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))

        except Exception as e:
            flash(f'Erro ao alterar função: {e}', 'danger')
            return redirect(url_for('funcoes_alterar', id=id))

    # Se for GET: busca o registro atual para pré-preencher o formulário.
    item = execute_one(
        'SELECT * FROM funcoes WHERE id_funcao = %s', (id,)
    )

    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))

    return render_template('dashboard/funcoes/form.html',
                           titulo='Alterar Função', modo='alterar', item=item)
```

### 1.3 Adicionando a rota funcoes_excluir

A rota de exclusão ainda não existe no `app.py`. Insira o código abaixo logo após a função `funcoes_alterar`:

```python
@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
def funcoes_excluir(id):
    # Usamos apenas POST para exclusão. Isso evita que alguém exclua
    # um registro acidentalmente ao acessar uma URL diretamente no navegador.
    try:
        execute_query('DELETE FROM funcoes WHERE id_funcao = %s', (id,))
        flash('Função excluída com sucesso.', 'success')
    except Exception as e:
        # O banco pode rejeitar a exclusão se houver usuários vinculados a esta função
        # (por causa da FOREIGN KEY). Nesse caso, exibimos o erro ao usuário.
        flash(f'Erro ao excluir função: {e}', 'danger')

    return redirect(url_for('funcoes_listar'))
```

### Arquivo app.py completo para conferência

```python
from flask import Flask, render_template, redirect, url_for, request, flash
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
                     gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas,
                     id)
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
    return render_template('dashboard/usuarios/listar.html')


@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
def usuarios_cadastrar():
    return render_template('dashboard/usuarios/form.html',
                           titulo='Cadastrar Usuário', modo='cadastrar', item=None)


@app.route('/usuarios/alterar/<int:id>', methods=['GET', 'POST'])
def usuarios_alterar(id):
    return render_template('dashboard/usuarios/form.html',
                           titulo='Alterar Usuário', modo='alterar', item=None)


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

## 2. Atualizando o template funcoes/visualizar.html

Abra o arquivo `templates/dashboard/funcoes/visualizar.html` e substitua todo o conteúdo pelo código abaixo:

```html
{% extends "base_dashboard.html" %}

{% block title %}Visualizar Função — CasaGestor{% endblock %}
{% block page_title %}Visualizar Função{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('funcoes_listar') }}">Funções</a></li>
            <li class="breadcrumb-item active">Visualizar</li>
        </ol>
    </nav>
    <!--
        item.id_funcao é o ID do registro buscado no banco.
        Passamos ele para a rota de alteração para que o formulário
        de edição já saiba qual registro deve ser carregado.
    -->
    <a href="{{ url_for('funcoes_alterar', id=item.id_funcao) }}" class="btn btn-warning">
        <i class="bi bi-pencil me-2"></i>Editar
    </a>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-shield-fill me-2 text-primary"></i>Dados da Função
    </div>
    <div class="card-body p-4">
        <div class="row g-4">
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Nome da Função</p>
                <!-- {{ item.nome }} exibe o valor do campo 'nome' do dicionário retornado pelo banco. -->
                <p class="fw-semibold mb-0">{{ item.nome }}</p>
            </div>
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Status</p>
                {% if item.status == 'Ativo' %}
                <span class="badge bg-success">{{ item.status }}</span>
                {% else %}
                <span class="badge bg-secondary">{{ item.status }}</span>
                {% endif %}
            </div>
            <div class="col-12">
                <p class="text-muted mb-1 small">Descrição</p>
                <p class="mb-0">{{ item.descricao }}</p>
            </div>
        </div>
    </div>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-toggles me-2 text-primary"></i>Permissões
    </div>
    <div class="card-body p-4">
        <div class="row g-2">
            <!--
                item.gerenciar_usuarios, item.gerenciar_funcoes e item.gerenciar_tarefas
                são valores BOOLEAN do banco: 1 (verdadeiro) ou 0 (falso).
                No Jinja2, valores numéricos não-zero são tratados como True,
                então podemos usar diretamente no {% if %}.
                Badge verde = permissão ativa (1), badge cinza = inativa (0).
            -->
            <div class="col-md-4">
                {% if item.gerenciar_usuarios %}
                <span class="badge bg-success me-1">
                    <i class="bi bi-check me-1"></i>Gerenciar Usuários
                </span>
                {% else %}
                <span class="badge bg-secondary me-1">
                    <i class="bi bi-x me-1"></i>Gerenciar Usuários
                </span>
                {% endif %}
            </div>
            <div class="col-md-4">
                {% if item.gerenciar_funcoes %}
                <span class="badge bg-success me-1">
                    <i class="bi bi-check me-1"></i>Gerenciar Funções
                </span>
                {% else %}
                <span class="badge bg-secondary me-1">
                    <i class="bi bi-x me-1"></i>Gerenciar Funções
                </span>
                {% endif %}
            </div>
            <div class="col-md-4">
                {% if item.gerenciar_tarefas %}
                <span class="badge bg-success me-1">
                    <i class="bi bi-check me-1"></i>Gerenciar Tarefas
                </span>
                {% else %}
                <span class="badge bg-secondary me-1">
                    <i class="bi bi-x me-1"></i>Gerenciar Tarefas
                </span>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<a href="{{ url_for('funcoes_listar') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-2"></i>Voltar
</a>

{% endblock %}
```

### Template funcoes/visualizar.html completo para conferência

```html
{% extends "base_dashboard.html" %}

{% block title %}Visualizar Função — CasaGestor{% endblock %}
{% block page_title %}Visualizar Função{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('funcoes_listar') }}">Funções</a></li>
            <li class="breadcrumb-item active">Visualizar</li>
        </ol>
    </nav>
    <a href="{{ url_for('funcoes_alterar', id=item.id_funcao) }}" class="btn btn-warning">
        <i class="bi bi-pencil me-2"></i>Editar
    </a>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-shield-fill me-2 text-primary"></i>Dados da Função
    </div>
    <div class="card-body p-4">
        <div class="row g-4">
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Nome da Função</p>
                <p class="fw-semibold mb-0">{{ item.nome }}</p>
            </div>
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Status</p>
                {% if item.status == 'Ativo' %}
                <span class="badge bg-success">{{ item.status }}</span>
                {% else %}
                <span class="badge bg-secondary">{{ item.status }}</span>
                {% endif %}
            </div>
            <div class="col-12">
                <p class="text-muted mb-1 small">Descrição</p>
                <p class="mb-0">{{ item.descricao }}</p>
            </div>
        </div>
    </div>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-toggles me-2 text-primary"></i>Permissões
    </div>
    <div class="card-body p-4">
        <div class="row g-2">
            <div class="col-md-4">
                {% if item.gerenciar_usuarios %}
                <span class="badge bg-success me-1"><i class="bi bi-check me-1"></i>Gerenciar Usuários</span>
                {% else %}
                <span class="badge bg-secondary me-1"><i class="bi bi-x me-1"></i>Gerenciar Usuários</span>
                {% endif %}
            </div>
            <div class="col-md-4">
                {% if item.gerenciar_funcoes %}
                <span class="badge bg-success me-1"><i class="bi bi-check me-1"></i>Gerenciar Funções</span>
                {% else %}
                <span class="badge bg-secondary me-1"><i class="bi bi-x me-1"></i>Gerenciar Funções</span>
                {% endif %}
            </div>
            <div class="col-md-4">
                {% if item.gerenciar_tarefas %}
                <span class="badge bg-success me-1"><i class="bi bi-check me-1"></i>Gerenciar Tarefas</span>
                {% else %}
                <span class="badge bg-secondary me-1"><i class="bi bi-x me-1"></i>Gerenciar Tarefas</span>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<a href="{{ url_for('funcoes_listar') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-2"></i>Voltar
</a>

{% endblock %}
```

---

## 3. Atualizando o template funcoes/form.html

O formulário precisa ser atualizado para pré-preencher os campos quando estiver no modo de alteração, usando os dados do `item` recebido da rota.

Abra o arquivo `templates/dashboard/funcoes/form.html` e substitua todo o conteúdo pelo código abaixo:

```html
{% extends "base_dashboard.html" %}

{% block title %}{{ titulo }} — CasaGestor{% endblock %}
{% block page_title %}{{ titulo }}{% endblock %}

{% block content %}

<div class="mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('funcoes_listar') }}">Funções</a></li>
            <li class="breadcrumb-item active">{{ titulo }}</li>
        </ol>
    </nav>
</div>

<!--
    O action do formulário muda conforme o modo:
    - modo 'alterar': envia o POST para funcoes_alterar passando o id do registro.
    - modo 'cadastrar': envia o POST para funcoes_cadastrar.
    Isso permite reutilizar o mesmo template para as duas operações.
-->
<form action="{{ url_for('funcoes_alterar', id=item.id_funcao) if modo == 'alterar' else url_for('funcoes_cadastrar') }}" method="POST">

    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold py-3">
            <i class="bi bi-shield-fill me-2 text-primary"></i>Dados da Função
        </div>
        <div class="card-body p-4">
            <div class="row g-3">

                <div class="col-md-6">
                    <label class="form-label fw-semibold">Nome da Função</label>
                    <!--
                        'item.nome if item else ''' pré-preenche o campo no modo alterar.
                        Se item for None (modo cadastrar), o campo fica vazio.
                    -->
                    <input type="text" class="form-control" name="nome"
                           value="{{ item.nome if item else '' }}"
                           placeholder="Ex.: Administrador">
                </div>

                <div class="col-md-6">
                    <label class="form-label fw-semibold">Status</label>
                    <select class="form-select" name="status">
                        <!--
                            'selected' marca a opção correta conforme o valor atual do registro.
                            Se item existir e o status for 'Ativo', a opção Ativo fica selecionada.
                            Se não houver item (cadastro), a opção padrão também é Ativo.
                        -->
                        <option value="Ativo"   {{ 'selected' if not item or item.status == 'Ativo'   else '' }}>Ativo</option>
                        <option value="Inativo" {{ 'selected' if item and item.status == 'Inativo' else '' }}>Inativo</option>
                    </select>
                </div>

                <div class="col-12">
                    <label class="form-label fw-semibold">Descrição</label>
                    <textarea class="form-control" rows="3" name="descricao"
                        placeholder="Descreva as responsabilidades desta função">{{ item.descricao if item else '' }}</textarea>
                </div>

            </div>
        </div>
    </div>

    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold py-3">
            <i class="bi bi-toggles me-2 text-primary"></i>Permissões
        </div>
        <div class="card-body p-4">
            <div class="row g-3">

                <div class="col-md-4">
                    <div class="form-check">
                        <!--
                            'checked' marca o checkbox se a permissão estiver ativa no banco (valor 1).
                            No modo cadastrar, item é None, então os checkboxes ficam desmarcados por padrão.
                        -->
                        <input name="gerenciar_usuarios" class="form-check-input" type="checkbox"
                               id="perm_usuarios"
                               {{ 'checked' if item and item.gerenciar_usuarios else '' }}>
                        <label class="form-check-label" for="perm_usuarios">Gerenciar Usuários</label>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="form-check">
                        <input name="gerenciar_funcoes" class="form-check-input" type="checkbox"
                               id="perm_funcoes"
                               {{ 'checked' if item and item.gerenciar_funcoes else '' }}>
                        <label class="form-check-label" for="perm_funcoes">Gerenciar Funções</label>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="form-check">
                        <input name="gerenciar_tarefas" class="form-check-input" type="checkbox"
                               id="perm_tarefas"
                               {{ 'checked' if item and item.gerenciar_tarefas else '' }}>
                        <label class="form-check-label" for="perm_tarefas">Gerenciar Tarefas</label>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <div class="d-flex justify-content-between">
        <a href="{{ url_for('funcoes_listar') }}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-2"></i>Cancelar
        </a>
        <button type="submit" class="btn btn-primary px-4">
            <i class="bi bi-check-lg me-2"></i>Salvar
        </button>
    </div>

</form>

{% endblock %}
```

### Template funcoes/form.html completo para conferência

```html
{% extends "base_dashboard.html" %}

{% block title %}{{ titulo }} — CasaGestor{% endblock %}
{% block page_title %}{{ titulo }}{% endblock %}

{% block content %}

<div class="mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('funcoes_listar') }}">Funções</a></li>
            <li class="breadcrumb-item active">{{ titulo }}</li>
        </ol>
    </nav>
</div>

<form action="{{ url_for('funcoes_alterar', id=item.id_funcao) if modo == 'alterar' else url_for('funcoes_cadastrar') }}" method="POST">

    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold py-3">
            <i class="bi bi-shield-fill me-2 text-primary"></i>Dados da Função
        </div>
        <div class="card-body p-4">
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label fw-semibold">Nome da Função</label>
                    <input type="text" class="form-control" name="nome"
                           value="{{ item.nome if item else '' }}"
                           placeholder="Ex.: Administrador">
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-semibold">Status</label>
                    <select class="form-select" name="status">
                        <option value="Ativo"   {{ 'selected' if not item or item.status == 'Ativo'   else '' }}>Ativo</option>
                        <option value="Inativo" {{ 'selected' if item and item.status == 'Inativo' else '' }}>Inativo</option>
                    </select>
                </div>
                <div class="col-12">
                    <label class="form-label fw-semibold">Descrição</label>
                    <textarea class="form-control" rows="3" name="descricao"
                        placeholder="Descreva as responsabilidades desta função">{{ item.descricao if item else '' }}</textarea>
                </div>
            </div>
        </div>
    </div>

    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold py-3">
            <i class="bi bi-toggles me-2 text-primary"></i>Permissões
        </div>
        <div class="card-body p-4">
            <div class="row g-3">
                <div class="col-md-4">
                    <div class="form-check">
                        <input name="gerenciar_usuarios" class="form-check-input" type="checkbox"
                               id="perm_usuarios"
                               {{ 'checked' if item and item.gerenciar_usuarios else '' }}>
                        <label class="form-check-label" for="perm_usuarios">Gerenciar Usuários</label>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-check">
                        <input name="gerenciar_funcoes" class="form-check-input" type="checkbox"
                               id="perm_funcoes"
                               {{ 'checked' if item and item.gerenciar_funcoes else '' }}>
                        <label class="form-check-label" for="perm_funcoes">Gerenciar Funções</label>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-check">
                        <input name="gerenciar_tarefas" class="form-check-input" type="checkbox"
                               id="perm_tarefas"
                               {{ 'checked' if item and item.gerenciar_tarefas else '' }}>
                        <label class="form-check-label" for="perm_tarefas">Gerenciar Tarefas</label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="d-flex justify-content-between">
        <a href="{{ url_for('funcoes_listar') }}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-2"></i>Cancelar
        </a>
        <button type="submit" class="btn btn-primary px-4">
            <i class="bi bi-check-lg me-2"></i>Salvar
        </button>
    </div>

</form>

{% endblock %}
```

---

## 4. Atualizando o template funcoes/listar.html

O template de listagem precisa receber o botão de excluir funcional com um modal de confirmação, no lugar do botão simples da Etapa 04.

Abra o arquivo `templates/dashboard/funcoes/listar.html` e substitua todo o conteúdo pelo código abaixo:

```html
{% extends "base_dashboard.html" %}

{% block title %}Funções — CasaGestor{% endblock %}
{% block page_title %}Funções de Usuário{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item active">Funções</li>
        </ol>
    </nav>
    <a href="{{ url_for('funcoes_cadastrar') }}" class="btn btn-primary">
        <i class="bi bi-shield-plus me-2"></i>Cadastrar Função
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
                        <th>Descrição</th>
                        <th>Status</th>
                        <th class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for d in dados %}
                    <tr>
                        <td>{{ d.id_funcao }}</td>
                        <td class="fw-semibold">{{ d.nome }}</td>
                        <td>{{ d.descricao }}</td>
                        <td>
                            {% if d.status == 'Ativo' %}
                            <span class="badge bg-success">{{ d.status }}</span>
                            {% else %}
                            <span class="badge bg-secondary">{{ d.status }}</span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            <a href="{{ url_for('funcoes_visualizar', id=d.id_funcao) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('funcoes_alterar', id=d.id_funcao) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <!--
                                data-bs-toggle="modal" abre o modal de confirmação ao clicar.
                                data-id e data-nome passam os dados da linha para o modal
                                via JavaScript, para que o modal mostre o nome correto
                                e envie o formulário para o id correto.
                            -->
                            <button type="button" class="btn btn-sm btn-outline-danger"
                                    title="Excluir"
                                    data-bs-toggle="modal"
                                    data-bs-target="#modalExcluir"
                                    data-id="{{ d.id_funcao }}"
                                    data-nome="{{ d.nome }}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}

                    {% if not dados %}
                    <tr>
                        <td colspan="5" class="text-center text-muted py-4">
                            Nenhuma função cadastrada ainda.
                            <a href="{{ url_for('funcoes_cadastrar') }}">Cadastrar agora</a>
                        </td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!--
    Modal de confirmação de exclusão.
    É um único modal compartilhado por todas as linhas da tabela.
    O JavaScript abaixo preenche os campos corretos conforme o botão clicado.
-->
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
                Tem certeza que deseja excluir a função
                <!-- id="excluirNome" é preenchido pelo JavaScript com o nome da função. -->
                <strong id="excluirNome"></strong>?
                <br>Esta ação não poderá ser desfeita.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary"
                        data-bs-dismiss="modal">Cancelar</button>
                <!--
                    O action deste formulário é preenchido pelo JavaScript
                    com a URL correta de exclusão, incluindo o id da função.
                    method="POST" garante que a exclusão só ocorre por envio de formulário,
                    nunca por acesso direto à URL.
                -->
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
    // Quando o modal de exclusão for aberto, este evento dispara.
    const modalExcluir = document.getElementById('modalExcluir');
    modalExcluir.addEventListener('show.bs.modal', function (event) {

        // 'event.relatedTarget' é o botão que foi clicado para abrir o modal.
        const botao = event.relatedTarget;

        // Lemos os atributos data-id e data-nome do botão clicado.
        const id   = botao.getAttribute('data-id');
        const nome = botao.getAttribute('data-nome');

        // Preenchemos o nome da função no texto do modal.
        document.getElementById('excluirNome').textContent = nome;

        // Definimos o action do formulário com a URL correta de exclusão.
        document.getElementById('formExcluir').action = '/funcoes/excluir/' + id;
    });
</script>
{% endblock %}
```

### Template funcoes/listar.html completo para conferência

```html
{% extends "base_dashboard.html" %}

{% block title %}Funções — CasaGestor{% endblock %}
{% block page_title %}Funções de Usuário{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item active">Funções</li>
        </ol>
    </nav>
    <a href="{{ url_for('funcoes_cadastrar') }}" class="btn btn-primary">
        <i class="bi bi-shield-plus me-2"></i>Cadastrar Função
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
                        <th>Descrição</th>
                        <th>Status</th>
                        <th class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for d in dados %}
                    <tr>
                        <td>{{ d.id_funcao }}</td>
                        <td class="fw-semibold">{{ d.nome }}</td>
                        <td>{{ d.descricao }}</td>
                        <td>
                            {% if d.status == 'Ativo' %}
                            <span class="badge bg-success">{{ d.status }}</span>
                            {% else %}
                            <span class="badge bg-secondary">{{ d.status }}</span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            <a href="{{ url_for('funcoes_visualizar', id=d.id_funcao) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('funcoes_alterar', id=d.id_funcao) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button type="button" class="btn btn-sm btn-outline-danger"
                                    title="Excluir"
                                    data-bs-toggle="modal"
                                    data-bs-target="#modalExcluir"
                                    data-id="{{ d.id_funcao }}"
                                    data-nome="{{ d.nome }}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}

                    {% if not dados %}
                    <tr>
                        <td colspan="5" class="text-center text-muted py-4">
                            Nenhuma função cadastrada ainda.
                            <a href="{{ url_for('funcoes_cadastrar') }}">Cadastrar agora</a>
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
                Tem certeza que deseja excluir a função
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
        document.getElementById('formExcluir').action = '/funcoes/excluir/' + id;
    });
</script>
{% endblock %}
```

---

## 5. Testando o fluxo completo

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

### Teste 1: Visualizar

1. Acesse `/funcoes/listar`
2. Clique no ícone de olho de qualquer função cadastrada
3. A página deve exibir os dados reais do banco, com os badges de permissão corretos (verde = ativo, cinza = inativo)
4. Clique em **Editar** e confirme que vai para o formulário de alteração

### Teste 2: Alterar

1. Na listagem, clique no ícone de lápis de qualquer função
2. O formulário deve abrir com os campos já preenchidos com os dados atuais
3. Os checkboxes de permissão devem refletir o estado salvo no banco
4. Altere algum campo e clique em **Salvar**
5. Você deve ser redirecionado para a listagem com a mensagem de sucesso
6. Confirme que a alteração aparece na tabela

### Teste 3: Excluir

1. Crie uma função temporária (ex: `Teste`) pelo formulário de cadastro
2. Na listagem, clique no ícone de lixeira desta função
3. O modal de confirmação deve aparecer com o nome correto
4. Clique em **Cancelar** e confirme que o modal fecha sem excluir
5. Clique novamente na lixeira e desta vez clique em **Excluir**
6. A função deve sumir da listagem e a mensagem de sucesso deve aparecer

### Teste 4: Exclusão bloqueada por vínculo

Se tentar excluir uma função que já tem usuários vinculados a ela (após a Etapa 07), o banco vai bloquear a operação pela `FOREIGN KEY`. A mensagem de erro do banco será exibida em vermelho ao usuário.

### Verificando no Workbench

```sql
USE casa_gestor;
SELECT * FROM funcoes;
```

---

## 6. Enviando as alterações para o GitHub

```
git add .
git commit -m "Etapa 06: visualizar, alterar e excluir funções"
git push
```

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| funcoes_visualizar | Atualizada para buscar o registro pelo id e passar ao template |
| funcoes_alterar | Atualizada para carregar dados no GET e executar UPDATE no POST |
| funcoes_excluir | Criada com DELETE protegido por método POST |
| funcoes/visualizar.html | Atualizado para exibir dados dinâmicos e badges de permissão |
| funcoes/form.html | Atualizado com pré-preenchimento de campos e action dinâmico |
| funcoes/listar.html | Atualizado com modal de confirmação de exclusão e JavaScript |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

**Próxima etapa:** Implementação da listagem e cadastro de usuários com dados reais do banco.
