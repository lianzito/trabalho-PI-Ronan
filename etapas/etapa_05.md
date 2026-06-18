# Etapa 05 - Listagem e Cadastro de Funções

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Atualizar a rota `funcoes_listar` para buscar os dados reais do banco
- Atualizar o template `funcoes/listar.html` para exibir os dados dinâmicos
- Atualizar a rota `funcoes_cadastrar` para processar o formulário e gravar no banco
- Testar o fluxo completo de listagem e cadastro de funções
- Enviar as alterações para o GitHub

Ao final desta etapa, será possível cadastrar novas funções pelo formulário e vê-las aparecer na tabela de listagem, tudo integrado com o banco de dados.

---

## Como o fluxo vai funcionar

Antes de escrever o código, entenda o fluxo de cada operação:

**Listagem:**
1. O usuário acessa `/funcoes/listar`
2. O Flask chama a função `funcoes_listar()`
3. A função executa um `SELECT` no banco e recebe uma lista de dicionários
4. Essa lista é passada para o template via `render_template`
5. O Jinja2 percorre a lista com `{% for %}` e exibe uma linha por registro

**Cadastro:**
1. O usuário acessa `/funcoes/cadastrar` (GET) e vê o formulário vazio
2. Preenche os dados e clica em Salvar (POST)
3. O Flask lê os dados do formulário via `request.form`
4. Valida os dados (campo obrigatório, etc.)
5. Executa um `INSERT` no banco
6. Redireciona para a listagem com uma mensagem de sucesso

---

## 1. Atualizando o app.py

### 1.1 Novos imports

Abra o `app.py`. Localize a primeira linha do arquivo, onde estão os imports, e substitua pelo bloco abaixo. Estamos adicionando `request` e `flash` ao import do Flask:

```python
# Adicionamos 'request' para ler os dados enviados pelo formulário (POST),
# e 'flash' para exibir mensagens temporárias de sucesso ou erro ao usuário.
from flask import Flask, render_template, redirect, url_for, request, flash

from db import iniciar_bd, execute_query, execute_one

app = Flask(__name__)

# secret_key é obrigatória para o Flask conseguir usar flash messages e sessões.
# Ela serve para assinar os cookies de forma segura.
# Em produção, use uma chave longa e aleatória. Nunca compartilhe este valor.
app.secret_key = '123456'

iniciar_bd()
```

> **Atenção:** insira o código acima substituindo apenas o bloco de imports e a criação do `app` no início do arquivo. O restante do `app.py` permanece igual por enquanto.

### 1.2 Atualizando a rota funcoes_listar

Localize no `app.py` a função `funcoes_listar` (que atualmente só chama `render_template`) e substitua ela pelo código abaixo:

```python
@app.route('/funcoes/listar')
def funcoes_listar():
    # SQL que busca todos os campos relevantes da tabela funcoes,
    # ordenando pelo id mais recente primeiro (ORDER BY id_funcao DESC).
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

    # execute_query com fetch=True retorna uma lista de dicionários.
    # Cada dicionário representa uma linha da tabela, ex:
    # {'id_funcao': 1, 'nome': 'Administrador', 'status': 'Ativo', ...}
    lista_dados = execute_query(sql, fetch=True)

    # Passa a lista para o template como a variável 'dados'.
    # No template, usaremos {% for d in dados %} para percorrer os registros.
    return render_template('dashboard/funcoes/listar.html', dados=lista_dados)
```

### 1.3 Atualizando a rota funcoes_cadastrar

Localize no `app.py` a função `funcoes_cadastrar` e substitua ela pelo código abaixo:

```python
@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
def funcoes_cadastrar():

    # request.method indica como a rota foi acessada.
    # GET: o usuário abriu a página do formulário (exibe o formulário vazio).
    # POST: o usuário preencheu o formulário e clicou em Salvar.
    if request.method == 'POST':

        # request.form.get('campo') lê o valor enviado pelo formulário.
        # .strip() remove espaços em branco do início e do fim.
        nome     = request.form.get('nome', '').strip()
        status   = request.form.get('status', 'Ativo')
        descricao = request.form.get('descricao', '').strip()

        # Checkboxes: se o checkbox estiver marcado, o campo aparece no request.form.
        # Se não estiver marcado, request.form.get() retorna None.
        # Por isso usamos: 1 se o campo existir, 0 se não existir.
        gerenciar_funcoes  = 1 if request.form.get('gerenciar_funcoes')  else 0
        gerenciar_usuarios = 1 if request.form.get('gerenciar_usuarios') else 0
        gerenciar_tarefas  = 1 if request.form.get('gerenciar_tarefas')  else 0

        # Validação: o campo nome é obrigatório.
        # flash() envia uma mensagem temporária que será exibida na próxima página.
        # O segundo argumento ('danger') define a categoria Bootstrap do alerta.
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
            # Os valores são passados como uma tupla separada do SQL.
            # O mysql.connector substitui cada %s pelo valor correspondente,
            # protegendo contra SQL Injection.
            dados = (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)

            execute_query(sql, dados)

            # Mensagem de sucesso exibida após o redirecionamento.
            flash(f'Função <b>{nome}</b> cadastrada com sucesso!', 'success')
            return redirect(url_for('funcoes_listar'))

        except Exception as e:
            # Se ocorrer qualquer erro no banco (ex: nome duplicado),
            # exibe a mensagem de erro e mantém o usuário no formulário.
            flash(f'Erro ao cadastrar função: {e}', 'danger')
            return redirect(url_for('funcoes_cadastrar'))

    # Se for GET, apenas exibe o formulário vazio.
    return render_template('dashboard/funcoes/form.html',
                           titulo='Cadastrar Função', modo='cadastrar', item=None)
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


@app.route('/funcoes/alterar/<int:id>')
def funcoes_alterar(id):
    return render_template('dashboard/funcoes/form.html',
                           titulo='Alterar Função', modo='alterar', item=None)


@app.route('/funcoes/visualizar/<int:id>')
def funcoes_visualizar(id):
    return render_template('dashboard/funcoes/visualizar.html')


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

## 2. Atualizando o template funcoes/listar.html

O template de listagem precisa ser atualizado para usar a variável `dados` que agora vem do banco, no lugar dos dados fixos que escrevemos na Etapa 04.

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
                    <!--
                        {% for d in dados %} percorre a lista de dicionários
                        retornada pelo banco de dados na rota funcoes_listar.
                        Cada 'd' é um dicionário com as colunas da tabela funcoes,
                        ex: d.id_funcao, d.nome, d.status, d.descricao.
                    -->
                    {% for d in dados %}
                    <tr>
                        <td>{{ d.id_funcao }}</td>
                        <td class="fw-semibold">{{ d.nome }}</td>
                        <td>{{ d.descricao }}</td>
                        <td>
                            <!--
                                Exibe badges coloridos conforme o status do registro.
                                bg-success (verde) para Ativo, bg-secondary (cinza) para Inativo.
                            -->
                            {% if d.status == 'Ativo' %}
                            <span class="badge bg-success">{{ d.status }}</span>
                            {% else %}
                            <span class="badge bg-secondary">{{ d.status }}</span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            <!--
                                Passamos d.id_funcao como parâmetro 'id' para as rotas
                                de visualizar e alterar, para que o Flask saiba qual
                                registro deve ser buscado ou editado.
                            -->
                            <a href="{{ url_for('funcoes_visualizar', id=d.id_funcao) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('funcoes_alterar', id=d.id_funcao) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}

                    <!--
                        {% if not dados %} exibe uma mensagem amigável
                        caso a tabela esteja vazia (nenhuma função cadastrada ainda).
                    -->
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
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
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

{% endblock %}
```

---

## 3. Testando o fluxo completo

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

### Teste 1: Banco vazio

Acesse `http://127.0.0.1:5000/funcoes/listar`. Como o banco está vazio, a mensagem "Nenhuma função cadastrada ainda" deve aparecer na tabela.

### Teste 2: Cadastrar uma função

1. Acesse `/funcoes/cadastrar` (ou clique no botão "Cadastrar Função")
2. Preencha:
   - Nome: `Administrador`
   - Status: `Ativo`
   - Descrição: `Acesso total ao sistema`
   - Marque todas as permissões
3. Clique em **Salvar**
4. Você deve ser redirecionado para `/funcoes/listar` com a mensagem verde "Função Administrador cadastrada com sucesso!"
5. A função deve aparecer na tabela

### Teste 3: Nome em branco

1. Acesse `/funcoes/cadastrar`
2. Deixe o campo Nome vazio
3. Clique em **Salvar**
4. A mensagem "O campo Nome é obrigatório." deve aparecer em vermelho

### Teste 4: Nome duplicado

1. Tente cadastrar uma função com o nome `Administrador` novamente
2. O banco vai recusar por causa da constraint `UNIQUE`
3. A mensagem de erro do banco deve aparecer em vermelho

### Verificando no Workbench

Abra o MySQL Workbench e execute o comando abaixo para confirmar que os registros foram inseridos corretamente:

```sql
USE casa_gestor;
SELECT * FROM funcoes;
```

---

## 4. Enviando as alterações para o GitHub

```
git add .
git commit -m "Etapa 05: listagem e cadastro de funções com BD"
git push
```

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| app.py | Adicionados `request`, `flash`, `secret_key` e `execute_query` |
| funcoes_listar | Atualizada para buscar dados reais do banco com SELECT |
| funcoes_cadastrar | Atualizada para processar o POST, validar e executar INSERT |
| funcoes/listar.html | Atualizado para exibir dados dinâmicos com `{% for %}` e mensagem de tabela vazia |
| Testes | Fluxo de listagem, cadastro, validação e duplicidade verificados |
| Workbench | Dados conferidos na tabela `funcoes` |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

**Próxima etapa:** Implementação da alteração, visualização e exclusão de funções.
