# Etapa 04 - Criando as Rotas e os Templates

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Criar os templates de autenticação (login, cadastro, recuperar senha)
- Criar o template da home do dashboard
- Criar todos os templates de funções (listar, form, visualizar, relatório)
- Criar todos os templates de usuários (listar, form, visualizar, relatório)
- Registrar todas as rotas no `app.py`
- Testar a navegação completa do sistema sem banco de dados
- Enviar as alterações para o GitHub

Ao final desta etapa, todas as páginas do sistema estarão funcionando com dados fixos no HTML, prontas para receber dados reais do banco nas próximas etapas.

---

## Estrutura de pastas que vamos criar

Antes de começar, crie as seguintes subpastas dentro de `templates/dashboard`:

- `templates/dashboard/funcoes/`
- `templates/dashboard/usuarios/`

No painel esquerdo do VS Code, clique com o botão direito na pasta `dashboard` e selecione **New Folder** para cada uma.

Ao final desta etapa a estrutura de `templates` ficará assim:

```
templates/
├── auth/
│   ├── login.html
│   ├── register.html
│   └── forgot_password.html
├── dashboard/
│   ├── funcoes/
│   │   ├── form.html
│   │   ├── listar.html
│   │   ├── visualizar.html
│   │   └── relatorio.html
│   ├── usuarios/
│   │   ├── form.html
│   │   ├── listar.html
│   │   ├── visualizar.html
│   │   └── relatorio.html
│   └── home.html
├── base_dashboard.html
├── base_public.html
└── index.html
```

---

## 1. Templates de autenticação

### 1.1 Criando o login.html

Crie o arquivo `login.html` dentro da pasta `templates/auth/`:

```html
{% extends "base_public.html" %}

{% block title %}Entrar — CasaGestor{% endblock %}

{% block content %}
<section class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-5 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body p-4">

                        <div class="text-center mb-4">
                            <i class="bi bi-house-heart-fill text-primary" style="font-size:2.2rem;"></i>
                            <h4 class="fw-bold mt-2 mb-1">Bem-vindo de volta</h4>
                            <p class="text-muted small">Acesse sua conta no CasaGestor</p>
                        </div>

                        <!--
                            Flash messages exibidas dentro do card de login.
                            Usamos o mesmo padrão do base_dashboard.html,
                            mas aqui dentro do card para ficar mais próximo do formulário.
                        -->
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                    {{ message }}
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}

                        <!--
                            action="{{ url_for('login') }}" envia os dados do formulário
                            para a rota 'login' usando o método POST.
                            method="post" envia os dados no corpo da requisição (não na URL),
                            o que é obrigatório para dados sensíveis como senha.
                        -->
                        <form action="{{ url_for('login') }}" method="post">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">E-mail</label>
                                <!--
                                    name="email" define o nome do campo.
                                    No Flask, usamos request.form.get('email') para recuperar este valor.
                                -->
                                <input type="email" name="email" class="form-control"
                                       placeholder="seu@email.com" required>
                            </div>
                            <div class="mb-1">
                                <label class="form-label fw-semibold">Senha</label>
                                <input type="password" name="senha" class="form-control"
                                       placeholder="••••••••" required>
                            </div>
                            <div class="text-end mb-3">
                                <a href="{{ url_for('recuperar_senha') }}" class="text-primary small">
                                    Esqueceu a senha?
                                </a>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">Entrar</button>
                            </div>
                        </form>

                        <hr>
                        <p class="text-center text-muted small mb-0">
                            Não tem conta?
                            <a href="{{ url_for('cadastro') }}" class="text-primary fw-semibold">
                                Cadastre-se
                            </a>
                        </p>

                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}
```

### 1.2 Criando o register.html

Crie o arquivo `register.html` dentro da pasta `templates/auth/`:

```html
{% extends "base_public.html" %}

{% block title %}Cadastro — CasaGestor{% endblock %}

{% block content %}
<section class="py-5">
    <div class="container">
        <div class="text-center mb-4">
            <h2 class="fw-bold">Criar sua conta</h2>
            <p class="text-muted">Preencha os dados abaixo para se cadastrar</p>
        </div>

        <!-- O formulário de cadastro está dividido em cards temáticos. -->
        <form action="#" method="post">
            <div class="row justify-content-center g-4">

                <!-- Card 1: Dados Pessoais -->
                <div class="col-lg-8">
                    <div class="card border-0 shadow-sm">
                        <!--
                            bg-primary aqui usa a classe que sobrescrevemos no style.css,
                            aplicando o roxo do projeto em vez do azul padrão do Bootstrap.
                        -->
                        <div class="card-header bg-primary text-white fw-semibold">
                            <i class="bi bi-person-fill me-2"></i>Dados Pessoais
                        </div>
                        <div class="card-body p-4">
                            <div class="row g-3">
                                <div class="col-12">
                                    <label class="form-label fw-semibold">
                                        Nome Completo <span class="text-danger">*</span>
                                    </label>
                                    <input type="text" class="form-control" placeholder="Seu nome completo">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        CPF <span class="text-danger">*</span>
                                    </label>
                                    <input type="text" class="form-control" placeholder="000.000.000-00">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Data de Nascimento <span class="text-danger">*</span>
                                    </label>
                                    <input type="date" class="form-control">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        E-mail <span class="text-danger">*</span>
                                    </label>
                                    <input type="email" class="form-control" placeholder="seu@email.com">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Celular <span class="text-danger">*</span>
                                    </label>
                                    <input type="text" class="form-control" placeholder="(00) 00000-0000">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Card 2: Endereço -->
                <div class="col-lg-8">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-secondary text-white fw-semibold">
                            <i class="bi bi-geo-alt-fill me-2"></i>Endereço
                        </div>
                        <div class="card-body p-4">
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">CEP <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" placeholder="00000-000">
                                </div>
                                <div class="col-md-8">
                                    <label class="form-label fw-semibold">Logradouro <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" placeholder="Rua, Avenida, Travessa…">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label fw-semibold">Número <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" placeholder="Nº">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Complemento</label>
                                    <input type="text" class="form-control" placeholder="Apto, Bloco…">
                                </div>
                                <div class="col-md-5">
                                    <label class="form-label fw-semibold">Bairro <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" placeholder="Bairro">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Cidade <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" placeholder="Cidade">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label fw-semibold">Estado <span class="text-danger">*</span></label>
                                    <select class="form-select">
                                        <option value="">UF</option>
                                        <option>AC</option><option>AL</option><option>AP</option>
                                        <option>AM</option><option>BA</option><option>CE</option>
                                        <option>DF</option><option>ES</option><option>GO</option>
                                        <option>MA</option><option>MT</option><option>MS</option>
                                        <option>MG</option><option>PA</option><option>PB</option>
                                        <option>PR</option><option>PE</option><option>PI</option>
                                        <option>RJ</option><option>RN</option><option>RS</option>
                                        <option>RO</option><option>RR</option><option>SC</option>
                                        <option>SP</option><option>SE</option><option>TO</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label fw-semibold">País</label>
                                    <!-- readonly impede que o usuário altere o valor do campo. -->
                                    <input type="text" class="form-control" value="Brasil" readonly>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Card 3: Dados de Acesso -->
                <div class="col-lg-8">
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
                                    <input type="password" class="form-control" placeholder="Mínimo 8 caracteres">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Confirmar Senha <span class="text-danger">*</span>
                                    </label>
                                    <input type="password" class="form-control" placeholder="Repita a senha">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Botões de ação -->
                <div class="col-lg-8 d-flex justify-content-between">
                    <a href="{{ url_for('login') }}" class="btn btn-outline-secondary">
                        Já tenho conta
                    </a>
                    <button type="submit" class="btn btn-primary px-5">Cadastrar</button>
                </div>

            </div>
        </form>
    </div>
</section>
{% endblock %}
```

### 1.3 Criando o forgot_password.html

Crie o arquivo `forgot_password.html` dentro da pasta `templates/auth/`:

```html
{% extends "base_public.html" %}

{% block title %}Recuperar Senha — CasaGestor{% endblock %}

{% block content %}
<section class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-5 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body p-4">

                        <div class="text-center mb-4">
                            <i class="bi bi-shield-lock-fill text-primary" style="font-size:2.2rem;"></i>
                            <h4 class="fw-bold mt-2 mb-1">Recuperar Senha</h4>
                            <p class="text-muted small">
                                Informe seu e-mail e enviaremos um link para redefinir sua senha.
                            </p>
                        </div>

                        <form action="#" method="post">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">E-mail</label>
                                <input type="email" class="form-control" placeholder="seu@email.com">
                            </div>
                            <div class="d-grid mt-4">
                                <button type="submit" class="btn btn-primary">
                                    Enviar link de recuperação
                                </button>
                            </div>
                        </form>

                        <hr>
                        <p class="text-center text-muted small mb-0">
                            Lembrou a senha?
                            <a href="{{ url_for('login') }}" class="text-primary fw-semibold">
                                Voltar ao login
                            </a>
                        </p>

                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}
```

---

## 2. Template da home do dashboard

Crie o arquivo `home.html` dentro da pasta `templates/dashboard/`:

```html
{% extends "base_dashboard.html" %}

{% block title %}Dashboard — CasaGestor{% endblock %}
{% block page_title %}Dashboard{% endblock %}

{% block content %}

<!-- Cards de estatísticas: números fixos por enquanto, virão do BD nas próximas etapas. -->
<div class="row g-4 mb-4">

    <div class="col-sm-6 col-xl-3">
        <!--
            stat-card é a classe do style.css que adiciona a borda roxa à esquerda.
            border-0 remove a borda padrão do Bootstrap.
            shadow-sm adiciona uma sombra suave ao card.
        -->
        <div class="card border-0 shadow-sm stat-card">
            <div class="card-body d-flex align-items-center gap-3">
                <div class="bg-primary-subtle rounded p-3">
                    <i class="bi bi-hourglass-split text-primary fs-4"></i>
                </div>
                <div>
                    <p class="text-muted mb-0 small">Tarefas Pendentes</p>
                    <h3 class="fw-bold mb-0">8</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="col-sm-6 col-xl-3">
        <!-- stat-card secondary usa border-left-color laranja (definido no style.css). -->
        <div class="card border-0 shadow-sm stat-card secondary">
            <div class="card-body d-flex align-items-center gap-3">
                <div class="bg-success-subtle rounded p-3">
                    <i class="bi bi-check-circle-fill text-success fs-4"></i>
                </div>
                <div>
                    <p class="text-muted mb-0 small">Tarefas Concluídas</p>
                    <h3 class="fw-bold mb-0">24</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm">
            <div class="card-body d-flex align-items-center gap-3">
                <div class="bg-info-subtle rounded p-3">
                    <i class="bi bi-arrow-repeat text-info fs-4"></i>
                </div>
                <div>
                    <p class="text-muted mb-0 small">Em Andamento</p>
                    <h3 class="fw-bold mb-0">5</h3>
                </div>
            </div>
        </div>
    </div>

    <div class="col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm">
            <div class="card-body d-flex align-items-center gap-3">
                <div class="bg-warning-subtle rounded p-3">
                    <i class="bi bi-people-fill text-warning fs-4"></i>
                </div>
                <div>
                    <p class="text-muted mb-0 small">Usuários Ativos</p>
                    <h3 class="fw-bold mb-0">4</h3>
                </div>
            </div>
        </div>
    </div>

</div>

<!-- Tabela de tarefas recentes com dados fixos para visualização do layout. -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
        <h6 class="mb-0 fw-bold">
            <i class="bi bi-list-task me-2 text-primary"></i>Tarefas Recentes
        </h6>
        <a href="{{ url_for('tarefas_listar') }}" class="btn btn-sm btn-outline-primary">Ver todas</a>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Tarefa</th>
                        <th>Responsável</th>
                        <th>Prioridade</th>
                        <th>Status</th>
                        <th>Prazo</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Dados fixos para visualização do layout. Virão do BD nas próximas etapas. -->
                    <tr>
                        <td class="fw-semibold">Limpar a cozinha</td>
                        <td>João Silva</td>
                        <td><span class="badge bg-danger">Alta</span></td>
                        <td><span class="badge bg-warning text-dark">Pendente</span></td>
                        <td>30/04/2026</td>
                    </tr>
                    <tr>
                        <td class="fw-semibold">Organizar a sala</td>
                        <td>Maria Souza</td>
                        <td><span class="badge bg-warning text-dark">Média</span></td>
                        <td><span class="badge bg-info text-dark">Em Andamento</span></td>
                        <td>01/05/2026</td>
                    </tr>
                    <tr>
                        <td class="fw-semibold">Compras do mês</td>
                        <td>Carlos Santos</td>
                        <td><span class="badge bg-danger">Alta</span></td>
                        <td><span class="badge bg-warning text-dark">Pendente</span></td>
                        <td>02/05/2026</td>
                    </tr>
                    <tr>
                        <td class="fw-semibold">Pagar contas</td>
                        <td>Ana Lima</td>
                        <td><span class="badge bg-danger">Alta</span></td>
                        <td><span class="badge bg-success">Concluído</span></td>
                        <td>28/04/2026</td>
                    </tr>
                    <tr>
                        <td class="fw-semibold">Cuidar do jardim</td>
                        <td>João Silva</td>
                        <td><span class="badge bg-success">Baixa</span></td>
                        <td><span class="badge bg-warning text-dark">Pendente</span></td>
                        <td>05/05/2026</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

{% endblock %}
```

---

## 3. Templates de funções

### 3.1 Criando o listar.html de funções

Crie o arquivo `listar.html` dentro da pasta `templates/dashboard/funcoes/`:

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
                    <!-- Dados fixos para visualização do layout. Virão do BD na Etapa 05. -->
                    <tr>
                        <td>1</td>
                        <td class="fw-semibold">Administrador</td>
                        <td>Acesso total ao sistema</td>
                        <td><span class="badge bg-success">Ativo</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('funcoes_visualizar', id=1) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('funcoes_alterar', id=1) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td class="fw-semibold">Usuário</td>
                        <td>Acesso básico ao sistema</td>
                        <td><span class="badge bg-success">Ativo</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('funcoes_visualizar', id=2) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('funcoes_alterar', id=2) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td class="fw-semibold">Gerente</td>
                        <td>Acesso intermediário</td>
                        <td><span class="badge bg-secondary">Inativo</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('funcoes_visualizar', id=3) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('funcoes_alterar', id=3) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

{% endblock %}
```

### 3.2 Criando o form.html de funções

Crie o arquivo `form.html` dentro da pasta `templates/dashboard/funcoes/`:

```html
{% extends "base_dashboard.html" %}

<!--
    titulo é uma variável passada pela rota do app.py.
    Dependendo da ação, ela terá o valor "Cadastrar Função" ou "Alterar Função".
-->
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
    O formulário aponta para a rota 'funcoes_cadastrar'.
    Nas etapas 05 e 06 vamos ajustar o action para diferenciar
    o cadastro da alteração usando a variável 'modo'.
-->
<form action="{{ url_for('funcoes_cadastrar') }}" method="POST">
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold py-3">
            <i class="bi bi-shield-fill me-2 text-primary"></i>Dados da Função
        </div>
        <div class="card-body p-4">
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label fw-semibold">Nome da Função</label>
                    <!--
                        name="nome" define o nome do campo que o Flask receberá via request.form.
                        O valor atual do campo (para edição) virá da variável 'item' nas próximas etapas.
                    -->
                    <input type="text" class="form-control" name="nome"
                           placeholder="Ex.: Administrador">
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-semibold">Status</label>
                    <select class="form-select" name="status">
                        <option value="Ativo">Ativo</option>
                        <option value="Inativo">Inativo</option>
                    </select>
                </div>
                <div class="col-12">
                    <label class="form-label fw-semibold">Descrição</label>
                    <textarea class="form-control" rows="3" name="descricao"
                        placeholder="Descreva as responsabilidades desta função"></textarea>
                </div>
            </div>
        </div>
    </div>

    <!-- Card de permissões com checkboxes -->
    <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold py-3">
            <i class="bi bi-toggles me-2 text-primary"></i>Permissões
        </div>
        <div class="card-body p-4">
            <div class="row g-3">
                <div class="col-md-4">
                    <div class="form-check">
                        <!--
                            name="gerenciar_usuarios" é o nome enviado via POST.
                            Se o checkbox estiver marcado, o Flask recebe o valor;
                            se não estiver, o campo simplesmente não aparece no request.form.
                            Por isso usamos: 1 if request.form.get('gerenciar_usuarios') else 0
                        -->
                        <input name="gerenciar_usuarios" class="form-check-input"
                               type="checkbox" id="perm_usuarios">
                        <label class="form-check-label" for="perm_usuarios">
                            Gerenciar Usuários
                        </label>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-check">
                        <input name="gerenciar_funcoes" class="form-check-input"
                               type="checkbox" id="perm_funcoes">
                        <label class="form-check-label" for="perm_funcoes">
                            Gerenciar Funções
                        </label>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-check">
                        <!--
                            checked deixa o checkbox marcado por padrão.
                            Nas etapas 05 e 06, o estado dos checkboxes virá do banco de dados.
                        -->
                        <input name="gerenciar_tarefas" class="form-check-input"
                               type="checkbox" id="perm_tarefas" checked>
                        <label class="form-check-label" for="perm_tarefas">
                            Gerenciar Tarefas
                        </label>
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

### 3.3 Criando o visualizar.html de funções

Crie o arquivo `visualizar.html` dentro da pasta `templates/dashboard/funcoes/`:

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
        id=1 é um valor fixo por enquanto.
        Nas etapas 05 e 06, usaremos item.id para passar o ID real do registro.
    -->
    <a href="{{ url_for('funcoes_alterar', id=1) }}" class="btn btn-warning">
        <i class="bi bi-pencil me-2"></i>Editar
    </a>
</div>

<!-- Dados fixos para visualização do layout. Virão do BD nas próximas etapas. -->
<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-shield-fill me-2 text-primary"></i>Dados da Função
    </div>
    <div class="card-body p-4">
        <div class="row g-4">
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Nome da Função</p>
                <p class="fw-semibold mb-0">Administrador</p>
            </div>
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Status</p>
                <span class="badge bg-success">Ativo</span>
            </div>
            <div class="col-12">
                <p class="text-muted mb-1 small">Descrição</p>
                <p class="mb-0">Acesso total ao sistema</p>
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
                Permissões exibidas como badges coloridos.
                Verde (bg-success) = permissão ativa.
                Cinza (bg-secondary) = permissão inativa.
                Nas próximas etapas, esses valores virão do banco de dados.
            -->
            <div class="col-md-4">
                <span class="badge bg-success me-1">
                    <i class="bi bi-check me-1"></i>Gerenciar Usuários
                </span>
            </div>
            <div class="col-md-4">
                <span class="badge bg-success me-1">
                    <i class="bi bi-check me-1"></i>Gerenciar Funções
                </span>
            </div>
            <div class="col-md-4">
                <span class="badge bg-success me-1">
                    <i class="bi bi-check me-1"></i>Gerenciar Tarefas
                </span>
            </div>
        </div>
    </div>
</div>

<a href="{{ url_for('funcoes_listar') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-2"></i>Voltar
</a>

{% endblock %}
```

### 3.4 Criando o relatorio.html de funções

Crie o arquivo `relatorio.html` dentro da pasta `templates/dashboard/funcoes/`:

```html
{% extends "base_dashboard.html" %}

{% block title %}Relatório de Funções — CasaGestor{% endblock %}
{% block page_title %}Relatório de Funções{% endblock %}

{% block content %}

<div class="mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('funcoes_listar') }}">Funções</a></li>
            <li class="breadcrumb-item active">Relatório</li>
        </ol>
    </nav>
</div>

<!-- Formulário de filtros. A action será implementada nas próximas etapas. -->
<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-funnel-fill me-2 text-primary"></i>Filtros do Relatório
    </div>
    <div class="card-body p-4">
        <form action="#" method="get">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label fw-semibold">Data Início</label>
                    <input type="date" class="form-control">
                </div>
                <div class="col-md-4">
                    <label class="form-label fw-semibold">Data Fim</label>
                    <input type="date" class="form-control">
                </div>
                <div class="col-md-4">
                    <label class="form-label fw-semibold">Status</label>
                    <select class="form-select">
                        <option value="">Todos</option>
                        <option>Ativo</option>
                        <option>Inativo</option>
                    </select>
                </div>
                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-search me-2"></i>Gerar Relatório
                    </button>
                    <button type="reset" class="btn btn-outline-secondary">
                        <i class="bi bi-x-lg me-2"></i>Limpar
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- Área de resultados: exibe uma mensagem enquanto nenhum filtro foi aplicado. -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
        <span class="fw-semibold">
            <i class="bi bi-table me-2 text-primary"></i>Resultados
        </span>
        <button class="btn btn-sm btn-outline-secondary" disabled>
            <i class="bi bi-download me-1"></i>Exportar
        </button>
    </div>
    <div class="card-body text-center text-muted py-5">
        <i class="bi bi-file-earmark-bar-graph" style="font-size:3rem;opacity:.4;"></i>
        <p class="mt-3 mb-0">
            Aplique os filtros acima e clique em <strong>Gerar Relatório</strong> para visualizar os dados.
        </p>
    </div>
</div>

{% endblock %}
```

---

## 4. Templates de usuários

### 4.1 Criando o listar.html de usuários

Crie o arquivo `listar.html` dentro da pasta `templates/dashboard/usuarios/`:

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
                    <!-- Dados fixos para visualização do layout. Virão do BD na Etapa 07. -->
                    <tr>
                        <td>1</td>
                        <td class="fw-semibold">João Silva</td>
                        <td>joao@email.com <br> (11) 99999-0001</td>
                        <td>Administrador</td>
                        <td><span class="badge bg-success">Ativo</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('usuarios_visualizar', id=1) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('usuarios_alterar', id=1) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td class="fw-semibold">Maria Souza</td>
                        <td>maria@email.com <br> (11) 99999-0002</td>
                        <td>Usuário</td>
                        <td><span class="badge bg-success">Ativo</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('usuarios_visualizar', id=2) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('usuarios_alterar', id=2) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td class="fw-semibold">Carlos Santos</td>
                        <td>carlos@email.com <br> (11) 99999-0003</td>
                        <td>Gerente</td>
                        <td><span class="badge bg-secondary">Inativo</span></td>
                        <td class="text-center">
                            <a href="{{ url_for('usuarios_visualizar', id=3) }}"
                               class="btn btn-sm btn-outline-info" title="Visualizar">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ url_for('usuarios_alterar', id=3) }}"
                               class="btn btn-sm btn-outline-warning" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

{% endblock %}
```

### 4.2 Criando o form.html de usuários

Crie o arquivo `form.html` dentro da pasta `templates/dashboard/usuarios/`:

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

<!-- O formulário está dividido em três cards temáticos. -->
<form action="#" method="POST">
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
                                   placeholder="Nome completo" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                CPF <span class="text-danger">*</span>
                            </label>
                            <input type="text" name="cpf" class="form-control"
                                   placeholder="000.000.000-00" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Data de Nascimento</label>
                            <input type="date" name="data_nascimento" class="form-control">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                E-mail <span class="text-danger">*</span>
                            </label>
                            <input type="email" name="email" class="form-control"
                                   placeholder="seu@email.com" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Celular <span class="text-danger">*</span>
                            </label>
                            <input type="text" name="celular" class="form-control"
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
                            <input type="text" name="cep" class="form-control" placeholder="00000-000">
                        </div>
                        <div class="col-md-8">
                            <label class="form-label fw-semibold">Logradouro</label>
                            <input type="text" name="logradouro" class="form-control"
                                   placeholder="Rua, Avenida, Travessa…">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label fw-semibold">Número</label>
                            <input type="text" name="numero" class="form-control" placeholder="Nº">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold">Complemento</label>
                            <input type="text" name="complemento" class="form-control"
                                   placeholder="Apto, Bloco…">
                        </div>
                        <div class="col-md-5">
                            <label class="form-label fw-semibold">Bairro</label>
                            <input type="text" name="bairro" class="form-control" placeholder="Bairro">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Cidade</label>
                            <input type="text" name="cidade" class="form-control" placeholder="Cidade">
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
                                <option value="{{ uf }}">{{ uf }}</option>
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
                            <input type="password" name="senha" class="form-control"
                                   placeholder="Mínimo 8 caracteres" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Confirmar Senha <span class="text-danger">*</span>
                            </label>
                            <input type="password" name="confirmar_senha" class="form-control"
                                   placeholder="Repita a senha" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">
                                Função <span class="text-danger">*</span>
                            </label>
                            <!--
                                Por enquanto a lista de funções está fixa.
                                Nas etapas 07 e 08, virá do banco de dados
                                através de um loop Jinja2 sobre a variável lista_funcoes.
                            -->
                            <select name="funcao_id" class="form-select" required>
                                <option value="">Selecione uma função</option>
                                <option value="1">Administrador</option>
                                <option value="2">Usuário</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Status</label>
                            <select name="status" class="form-select">
                                <option value="Ativo">Ativo</option>
                                <option value="Inativo">Inativo</option>
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

### 4.3 Criando o visualizar.html de usuários

Crie o arquivo `visualizar.html` dentro da pasta `templates/dashboard/usuarios/`:

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
    <a href="{{ url_for('usuarios_alterar', id=1) }}" class="btn btn-warning">
        <i class="bi bi-pencil me-2"></i>Editar
    </a>
</div>

<!-- Dados fixos para visualização do layout. Virão do BD nas próximas etapas. -->
<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-person-fill me-2 text-primary"></i>Dados do Usuário
    </div>
    <div class="card-body p-4">
        <div class="row g-4">
            <div class="col-md-6">
                <p class="text-muted mb-1 small">Nome Completo</p>
                <p class="fw-semibold mb-0">João Silva</p>
            </div>
            <div class="col-md-6">
                <p class="text-muted mb-1 small">E-mail</p>
                <p class="fw-semibold mb-0">joao@email.com</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">CPF</p>
                <p class="fw-semibold mb-0">000.000.000-00</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Celular</p>
                <p class="fw-semibold mb-0">(11) 99999-0001</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Função</p>
                <p class="fw-semibold mb-0">Administrador</p>
            </div>
            <div class="col-md-4">
                <p class="text-muted mb-1 small">Status</p>
                <span class="badge bg-success">Ativo</span>
            </div>
        </div>
    </div>
</div>

<a href="{{ url_for('usuarios_listar') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-2"></i>Voltar
</a>

{% endblock %}
```

### 4.4 Criando o relatorio.html de usuários

Crie o arquivo `relatorio.html` dentro da pasta `templates/dashboard/usuarios/`:

```html
{% extends "base_dashboard.html" %}

{% block title %}Relatório de Usuários — CasaGestor{% endblock %}
{% block page_title %}Relatório de Usuários{% endblock %}

{% block content %}

<div class="mb-4">
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item"><a href="{{ url_for('home') }}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{{ url_for('usuarios_listar') }}">Usuários</a></li>
            <li class="breadcrumb-item active">Relatório</li>
        </ol>
    </nav>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white fw-semibold py-3">
        <i class="bi bi-funnel-fill me-2 text-primary"></i>Filtros do Relatório
    </div>
    <div class="card-body p-4">
        <form action="#" method="get">
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label fw-semibold">Data Início</label>
                    <input type="date" class="form-control">
                </div>
                <div class="col-md-3">
                    <label class="form-label fw-semibold">Data Fim</label>
                    <input type="date" class="form-control">
                </div>
                <div class="col-md-3">
                    <label class="form-label fw-semibold">Função</label>
                    <select class="form-select">
                        <option value="">Todas</option>
                        <option>Administrador</option>
                        <option>Gerente</option>
                        <option>Usuário</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label fw-semibold">Status</label>
                    <select class="form-select">
                        <option value="">Todos</option>
                        <option>Ativo</option>
                        <option>Inativo</option>
                    </select>
                </div>
                <div class="col-12 d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-search me-2"></i>Gerar Relatório
                    </button>
                    <button type="reset" class="btn btn-outline-secondary">
                        <i class="bi bi-x-lg me-2"></i>Limpar
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>

<div class="card border-0 shadow-sm">
    <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
        <span class="fw-semibold">
            <i class="bi bi-table me-2 text-primary"></i>Resultados
        </span>
        <button class="btn btn-sm btn-outline-secondary" disabled>
            <i class="bi bi-download me-1"></i>Exportar
        </button>
    </div>
    <div class="card-body text-center text-muted py-5">
        <i class="bi bi-file-earmark-bar-graph" style="font-size:3rem;opacity:.4;"></i>
        <p class="mt-3 mb-0">
            Aplique os filtros acima e clique em <strong>Gerar Relatório</strong> para visualizar os dados.
        </p>
    </div>
</div>

{% endblock %}
```

---

## 5. Atualizando o app.py

Agora vamos registrar todas as rotas criadas nesta etapa. Substitua todo o conteúdo do `app.py` pelo seguinte:

```python
# Importa as ferramentas do Flask necessárias para esta etapa.
# render_template: renderiza um arquivo HTML da pasta templates.
# redirect: redireciona o usuário para outra rota.
# url_for: gera a URL de uma rota pelo nome da função.
from flask import Flask, render_template, redirect, url_for

# Importa a função de inicialização do banco de dados.
from db import iniciar_bd

# Cria a instância da aplicação Flask.
app = Flask(__name__)

# Inicializa o banco de dados ao iniciar a aplicação.
iniciar_bd()


@app.context_processor
def injetar_usuario():
    """
    Injeta a variável usuario_logado em todos os templates.
    Por enquanto retorna None. Na Etapa 09 virá da sessão do Flask.
    """
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
    # methods=['GET', 'POST'] permite que esta rota receba tanto
    # o carregamento da página (GET) quanto o envio do formulário (POST).
    # A lógica de autenticação será implementada na Etapa 09.
    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    # Redireciona para a página de login. A lógica de logout virá na Etapa 09.
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
    return render_template('dashboard/funcoes/listar.html')


@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
def funcoes_cadastrar():
    # titulo e modo são passados para o template para personalizar
    # o cabeçalho e o comportamento do formulário.
    return render_template('dashboard/funcoes/form.html',
                           titulo='Cadastrar Função', modo='cadastrar', item=None)


@app.route('/funcoes/alterar/<int:id>')
def funcoes_alterar(id):
    # <int:id> captura o número da URL (ex: /funcoes/alterar/3)
    # e o passa como parâmetro 'id' para a função.
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
    # A rota de exclusão usa apenas POST para evitar exclusões acidentais
    # por simples acesso a uma URL. A lógica de exclusão virá na Etapa 08.
    return redirect(url_for('usuarios_listar'))


@app.route('/usuarios/relatorio')
def usuarios_relatorio():
    return render_template('dashboard/usuarios/relatorio.html')


# ── Rotas de Tarefas (estrutura básica para a sidebar funcionar) ───────────────

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


# Inicia o servidor de desenvolvimento.
if __name__ == '__main__':
    app.run(debug=True)
```

### Arquivo app.py completo para conferência

```python
from flask import Flask, render_template, redirect, url_for
from db import iniciar_bd

app = Flask(__name__)

iniciar_bd()


@app.context_processor
def injetar_usuario():
    return dict(usuario_logado=None)


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


@app.route('/home')
def home():
    return render_template('dashboard/home.html')


@app.route('/funcoes/listar')
def funcoes_listar():
    return render_template('dashboard/funcoes/listar.html')


@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
def funcoes_cadastrar():
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

> **Atenção:** o `sobre.html` ainda não foi criado. Vamos adicioná-lo agora para que a rota `/sobre` funcione corretamente.

Crie o arquivo `sobre.html` diretamente dentro da pasta `templates/`:

```html
{% extends "base_public.html" %}

{% block title %}Sobre — CasaGestor{% endblock %}

{% block content %}
<section class="py-5">
    <div class="container">
        <div class="text-center mb-5">
            <h1 class="fw-bold">Sobre os Desenvolvedores</h1>
            <p class="text-muted lead">Conheça a equipe por trás do CasaGestor</p>
        </div>

        <div class="row justify-content-center g-4">

            <!-- Card do Desenvolvedor 1 -->
            <div class="col-md-5">
                <div class="card border-0 shadow-sm h-100 text-center p-4">
                    <div class="avatar-large mx-auto mb-3">
                        <i class="bi bi-person-fill" style="font-size:2.8rem;"></i>
                    </div>
                    <h4 class="fw-bold mb-1">João da Silva</h4>
                    <p class="text-primary fw-semibold mb-3">Desenvolvedor Full Stack</p>
                    <p class="text-muted">
                        Especialista em desenvolvimento web com experiência em Python, Flask e
                        frameworks modernos de front-end.
                    </p>
                    <div class="d-flex justify-content-center gap-2 mt-3">
                        <a href="#" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-github me-1"></i>GitHub
                        </a>
                        <a href="#" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-linkedin me-1"></i>LinkedIn
                        </a>
                    </div>
                </div>
            </div>

            <!-- Card do Desenvolvedor 2 -->
            <div class="col-md-5">
                <div class="card border-0 shadow-sm h-100 text-center p-4">
                    <div class="avatar-large mx-auto mb-3"
                         style="background:linear-gradient(135deg,#F47B20,#7B2FBE);">
                        <i class="bi bi-person-fill" style="font-size:2.8rem;"></i>
                    </div>
                    <h4 class="fw-bold mb-1">Maria Souza</h4>
                    <p class="text-secondary fw-semibold mb-3">Desenvolvedora Front-end e UX</p>
                    <p class="text-muted">
                        Designer e desenvolvedora com foco em experiência do usuário e interfaces
                        responsivas.
                    </p>
                    <div class="d-flex justify-content-center gap-2 mt-3">
                        <a href="#" class="btn btn-sm" style="border-color:#F47B20;color:#F47B20;">
                            <i class="bi bi-github me-1"></i>GitHub
                        </a>
                        <a href="#" class="btn btn-sm" style="border-color:#F47B20;color:#F47B20;">
                            <i class="bi bi-linkedin me-1"></i>LinkedIn
                        </a>
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>
{% endblock %}
```

---

## 6. Testando a aplicação

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

Acesse `http://127.0.0.1:5000` e navegue por todas as páginas clicando nos links. Verifique:

- Menu superior: **Início**, **Sobre**, **Entrar**, **Cadastrar**
- `/login` exibe o formulário de login
- `/cadastro` exibe o formulário de cadastro com os três cards
- `/home` exibe o dashboard com os cards de estatísticas e a tabela
- Na sidebar do dashboard: todos os links de Funções e Usuários funcionam
- `/funcoes/listar` exibe a tabela com três funções fixas
- `/funcoes/cadastrar` exibe o formulário de cadastro de função
- `/funcoes/visualizar/1` exibe os dados fixos da função Administrador
- `/usuarios/listar` exibe a tabela com três usuários fixos
- `/usuarios/cadastrar` exibe o formulário de cadastro de usuário
- `/usuarios/visualizar/1` exibe os dados fixos do usuário João Silva

Para parar o servidor, pressione `Ctrl + C`.

---

## 7. Enviando as alterações para o GitHub

Com tudo funcionando, salve todos os arquivos no VS Code (`Ctrl + S`) e envie as alterações:

```
git add .
git commit -m "Etapa 04: rotas e templates do dashboard, funcoes e usuarios"
git push
```

---

## Resumo do que foi feito

| Arquivo criado | Localização |
|---|---|
| login.html | templates/auth/ |
| register.html | templates/auth/ |
| forgot_password.html | templates/auth/ |
| sobre.html | templates/ |
| home.html | templates/dashboard/ |
| funcoes/listar.html | templates/dashboard/funcoes/ |
| funcoes/form.html | templates/dashboard/funcoes/ |
| funcoes/visualizar.html | templates/dashboard/funcoes/ |
| funcoes/relatorio.html | templates/dashboard/funcoes/ |
| usuarios/listar.html | templates/dashboard/usuarios/ |
| usuarios/form.html | templates/dashboard/usuarios/ |
| usuarios/visualizar.html | templates/dashboard/usuarios/ |
| usuarios/relatorio.html | templates/dashboard/usuarios/ |
| app.py | raiz do projeto (atualizado com todas as rotas) |

---

**Próxima etapa:** Implementação da listagem e do cadastro de funções com dados reais do banco de dados.
