# Etapa 03 - Criando a Base do Projeto

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Criar a pasta `static` com os arquivos `style.css` e `script.js`
- Criar a pasta `templates` com os arquivos base do projeto
- Criar o `base_public.html` (layout das páginas públicas)
- Criar o `base_dashboard.html` (layout das páginas internas com sidebar)
- Criar o `index.html` (página inicial pública)
- Conectar os templates ao `app.py`
- Enviar as alterações para o GitHub

Ao final desta etapa, ao acessar `http://127.0.0.1:5000` você verá a página inicial do CasaGestor com layout, cores e menu funcionando.

---

## 1. Criando a pasta static e seus arquivos

A pasta `static` guarda arquivos que não mudam durante a execução da aplicação: folhas de estilo (CSS), scripts JavaScript e imagens. O Flask já sabe procurar por essa pasta automaticamente.

No painel esquerdo do VS Code, clique com o botão direito na raiz do projeto e selecione **New Folder**. Nomeie a pasta como `static`.

Dentro de `static`, crie mais duas pastas: `css` e `js`.

A estrutura deve ficar assim:

```
casagestor/
└── static/
    ├── css/
    └── js/
```

### 1.1 Criando o style.css

Dentro da pasta `static/css`, crie um arquivo chamado `style.css` e escreva o seguinte conteúdo:

```css
/* ── Variáveis de cor ─────────────────────────────────────────────── */
/*
  :root define variáveis CSS globais que podem ser reutilizadas em todo o arquivo.
  Centralizamos as cores aqui para facilitar mudanças futuras:
  basta alterar o valor aqui e todas as ocorrências serão atualizadas.
*/
:root {
    --bs-primary:       #7B2FBE;        /* Roxo principal do projeto */
    --bs-primary-rgb:   123, 47, 190;
    --bs-secondary:     #F47B20;        /* Laranja secundário */
    --bs-secondary-rgb: 244, 123, 32;
    --bs-link-color:    #7B2FBE;
    --bs-link-hover-color: #6625A0;
}

/* ── Botões ───────────────────────────────────────────────────────── */
/*
  Sobrescrevemos as variáveis internas do Bootstrap para os botões
  usarem as cores do projeto em vez das cores padrão do Bootstrap (azul).
*/
.btn-primary {
    --bs-btn-bg:              #7B2FBE;
    --bs-btn-border-color:    #7B2FBE;
    --bs-btn-hover-bg:        #6625A0;
    --bs-btn-hover-border-color: #6625A0;
    --bs-btn-active-bg:       #5a1d8a;
    --bs-btn-color:           #fff;
    --bs-btn-hover-color:     #fff;
    --bs-btn-disabled-bg:     #7B2FBE;
    --bs-btn-disabled-border-color: #7B2FBE;
}

.btn-outline-primary {
    --bs-btn-color:           #7B2FBE;
    --bs-btn-border-color:    #7B2FBE;
    --bs-btn-hover-bg:        #7B2FBE;
    --bs-btn-hover-border-color: #7B2FBE;
    --bs-btn-hover-color:     #fff;
    --bs-btn-active-bg:       #6625A0;
}

.btn-secondary {
    --bs-btn-bg:              #F47B20;
    --bs-btn-border-color:    #F47B20;
    --bs-btn-hover-bg:        #D96A17;
    --bs-btn-hover-border-color: #D96A17;
    --bs-btn-active-bg:       #c05e14;
    --bs-btn-color:           #fff;
    --bs-btn-hover-color:     #fff;
    --bs-btn-disabled-bg:     #F47B20;
    --bs-btn-disabled-border-color: #F47B20;
}

.btn-outline-secondary {
    --bs-btn-color:        #6c757d;
    --bs-btn-border-color: #6c757d;
    --bs-btn-hover-bg:     #6c757d;
    --bs-btn-hover-color:  #fff;
}

/* ── Cores utilitárias ────────────────────────────────────────────── */
/*
  O Bootstrap tem classes como text-primary e bg-primary, mas elas usam o azul padrão.
  Usamos !important para forçar nossos valores sobre os do Bootstrap.
*/
.text-primary   { color: #7B2FBE !important; }
.text-secondary { color: #F47B20 !important; }
.bg-primary     { background-color: #7B2FBE !important; }
.bg-secondary   { background-color: #F47B20 !important; }
.border-primary { border-color: #7B2FBE !important; }

/* Versão clara do roxo para fundos de ícones nos cards do dashboard. */
.bg-primary-subtle { background-color: rgba(123, 47, 190, 0.12) !important; }

/* ── Navbar pública ───────────────────────────────────────────────── */
.navbar-brand            { color: #7B2FBE !important; }
.nav-link.active         { color: #d4bce9 !important; font-weight: 600; }

/* ── Hero (banner principal da página inicial) ────────────────────── */
/*
  A seção hero usa um gradiente diagonal do roxo ao laranja.
  linear-gradient(135deg, ...) define a direção e as duas cores do gradiente.
*/
.hero-section {
    background: linear-gradient(135deg, #7B2FBE 0%, #F47B20 100%);
    color: white;
    padding: 5.5rem 0;
}

/* ── Ícone de feature (cards da seção de funcionalidades) ─────────── */
.feature-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #7B2FBE, #F47B20);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.6rem;
    margin-bottom: 1rem;
}

/* ── Avatares ─────────────────────────────────────────────────────── */
/* Avatar pequeno usado na navbar do dashboard para mostrar as iniciais do usuário. */
.avatar-circle {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #7B2FBE, #F47B20);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
}

/* Avatar grande usado na página Sobre para exibir a foto/ícone dos desenvolvedores. */
.avatar-large {
    width: 90px;
    height: 90px;
    background: linear-gradient(135deg, #7B2FBE, #F47B20);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

/* ── Sidebar ──────────────────────────────────────────────────────── */
/*
  A sidebar é fixa na lateral esquerda (position: fixed).
  Tem largura de 250px e ocupa toda a altura da tela (min-height: 100vh).
  O z-index: 100 garante que ela fique na frente de outros elementos.
*/
.sidebar {
    width: 250px;
    min-height: 100vh;
    background: #1a1a2e;       /* Azul escuro quase preto */
    position: fixed;
    top: 0;
    left: 0;
    overflow-y: auto;          /* Scroll vertical se o menu for maior que a tela */
    z-index: 100;
    display: flex;
    flex-direction: column;
}

/* Logo/nome do sistema no topo da sidebar. */
.sidebar-brand {
    padding: 1.25rem 1rem;
    color: white;
    font-weight: 700;
    font-size: 1.05rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    text-decoration: none;
    display: block;
}

/* Títulos de seção dentro da sidebar (ex: "Usuários", "Funções"). */
.sidebar .nav-section-title {
    color: rgba(255,255,255,0.35);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 1rem 1rem 0.25rem;
    list-style: none;
}

/* Links de navegação da sidebar. */
.sidebar .nav-link {
    color: rgba(255,255,255,0.7);
    padding: 0.45rem 1rem;
    transition: background 0.15s, color 0.15s;  /* Animação suave ao passar o mouse */
    font-size: 0.9rem;
    border-radius: 0;
}

.sidebar .nav-link:hover {
    color: #fff;
    background: rgba(123, 47, 190, 0.25);
}

/* Classe 'active' marca o link da página atual com destaque. */
.sidebar .nav-link.active {
    color: #fff;
    background: rgba(123, 47, 190, 0.5);
}

/* Links de submenu: têm um recuo maior à esquerda para indicar hierarquia. */
.sub-nav-link {
    padding-left: 2.25rem !important;
}

/* Rodapé da sidebar com o botão de sair. */
.sidebar-footer {
    padding: 1rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin-top: auto;          /* Empurra o rodapé para o final da sidebar */
}

/* ── Conteúdo principal ───────────────────────────────────────────── */
/*
  margin-left: 250px empurra o conteúdo para a direita,
  deixando espaço exatamente para a sidebar fixa de 250px.
*/
.main-content {
    margin-left: 250px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Barra de navegação superior dentro do dashboard. */
.top-navbar {
    background: white;
    border-bottom: 1px solid #e9ecef;
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
}

/* ── Cards de estatísticas da home ───────────────────────────────── */
/* Borda colorida na esquerda dos cards para destaque visual. */
.stat-card           { border-left: 4px solid #7B2FBE; }
.stat-card.secondary { border-left-color: #F47B20; }

/* ── Card headers coloridos ───────────────────────────────────────── */
.card-header.bg-primary   { background-color: #7B2FBE !important; }
.card-header.bg-secondary { background-color: #F47B20 !important; }
```

### 1.2 Criando o script.js

Dentro da pasta `static/js`, crie um arquivo chamado `script.js`. Por enquanto ele ficará vazio, mas já deixamos o arquivo criado para uso nas próximas etapas:

```javascript
// script.js — Arquivo de scripts JavaScript do CasaGestor.
// Funcionalidades de interação com o usuário serão adicionadas aqui nas próximas etapas.
```

---

## 2. Criando a pasta templates

A pasta `templates` guarda todos os arquivos HTML do projeto. O Flask procura por essa pasta automaticamente quando você chama `render_template()`.

No painel esquerdo do VS Code, crie uma nova pasta na raiz do projeto chamada `templates`.

Dentro de `templates`, crie mais duas pastas: `auth` e `dashboard`.

A estrutura deve ficar assim:

```
casagestor/
└── templates/
    ├── auth/
    └── dashboard/
```

---

## 3. Criando o base_public.html

O `base_public.html` é o layout base de todas as páginas públicas do sistema, ou seja, as páginas que qualquer visitante pode ver sem precisar fazer login (início, login, cadastro).

Ele define a estrutura HTML completa com o `<head>`, o menu de navegação superior e o rodapé. As páginas que herdarem este template só precisam preencher o conteúdo do meio.

Crie o arquivo `base_public.html` diretamente dentro da pasta `templates`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!--
        {% block title %} é um bloco Jinja2.
        Os templates filhos podem substituir este conteúdo colocando
        {% block title %}Título da Página{% endblock %} no próprio arquivo.
        Se o filho não definir o bloco, o valor padrão "CasaGestor" é usado.
    -->
    <title>{% block title %}CasaGestor{% endblock %}</title>

    <!-- Bootstrap CSS: framework de estilos carregado via CDN (internet). -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">

    <!-- Bootstrap Icons: biblioteca de ícones usada nos menus e botões. -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

    <!--
        url_for('static', filename='css/style.css') gera o caminho correto
        até o arquivo style.css dentro da pasta static do projeto.
        Usar url_for em vez de um caminho fixo evita erros quando o projeto
        é publicado em um servidor com estrutura de pastas diferente.
    -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

<!-- Barra de navegação superior das páginas públicas -->
<nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top">
    <div class="container">

        <!-- Logo e nome do sistema. Clicando, volta para a página inicial. -->
        <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
            <i class="bi bi-house-heart-fill me-2"></i>CasaGestor
        </a>

        <!-- Botão hamburguer: aparece em telas pequenas (celular/tablet). -->
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarMain">
            <ul class="navbar-nav ms-auto align-items-center gap-1">

                <!--
                    request.endpoint retorna o nome da rota atual.
                    Se o endpoint for 'index', a classe 'active' é adicionada ao link,
                    destacando visualmente qual página o usuário está visitando.
                -->
                <li class="nav-item">
                    <a class="nav-link {% if request.endpoint == 'index' %}active{% endif %}"
                       href="{{ url_for('index') }}">Início</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {% if request.endpoint == 'sobre' %}active{% endif %}"
                       href="{{ url_for('sobre') }}">Sobre</a>
                </li>

                <!-- Botões de acesso ao sistema -->
                <li class="nav-item ms-2">
                    <a class="btn btn-outline-primary btn-sm px-3"
                       href="{{ url_for('login') }}">Entrar</a>
                </li>
                <li class="nav-item">
                    <a class="btn btn-primary btn-sm px-3"
                       href="{{ url_for('cadastro') }}">Cadastrar</a>
                </li>
            </ul>
        </div>
    </div>
</nav>

<!--
    {% block content %}{% endblock %} é o bloco principal de conteúdo.
    Cada página filha vai preencher este espaço com seu próprio HTML.
-->
{% block content %}{% endblock %}

<!-- Rodapé do site -->
<footer class="bg-dark text-white py-4 mt-auto">
    <div class="container text-center">
        <p class="mb-1 fw-semibold">
            <i class="bi bi-house-heart-fill me-2 text-primary"></i>CasaGestor
        </p>
        <p class="mb-0 text-white-50 small">&copy; 2026 CasaGestor. Todos os direitos reservados.</p>
    </div>
</footer>

<!-- Bootstrap JS: necessário para o menu hamburguer e outros componentes interativos. -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 4. Criando o base_dashboard.html

O `base_dashboard.html` é o layout base de todas as páginas internas do sistema, acessíveis apenas após o login. Ele inclui a sidebar com o menu de navegação, a barra superior com o nome do usuário logado e o espaço para o conteúdo de cada página.

Crie o arquivo `base_dashboard.html` diretamente dentro da pasta `templates`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CasaGestor{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>

<!--
    bg-light aplica um fundo cinza claro em toda a página,
    diferenciando visualmente o dashboard das páginas públicas (fundo branco).
-->
<body class="bg-light">

<!-- ═══════════════════════════════════════════════════════════════
     SIDEBAR - Menu lateral fixo do dashboard
     ═══════════════════════════════════════════════════════════════ -->
<nav class="sidebar">

    <!-- Logo no topo da sidebar. Clicando, vai para o dashboard. -->
    <a class="sidebar-brand" href="{{ url_for('home') }}">
        <i class="bi bi-house-heart-fill me-2"></i>CasaGestor
    </a>

    <ul class="nav flex-column mt-1">

        <!-- ── Dashboard ── -->
        <li class="nav-item">
            <!--
                request.endpoint == 'home' verifica se a página atual é o dashboard.
                Se for, adiciona a classe 'active' para destacar o link na sidebar.
            -->
            <a class="nav-link {% if request.endpoint == 'home' %}active{% endif %}"
               href="{{ url_for('home') }}">
                <i class="bi bi-speedometer2 me-2"></i>Dashboard
            </a>
        </li>

        <!-- ── Seção Usuários ── -->
        <!--
            nav-section-title é uma classe do style.css que estiliza
            o texto de título de seção dentro da sidebar.
        -->
        <li class="nav-section-title">Usuários</li>
        <li class="nav-item">
            <!--
                sub-nav-link adiciona um recuo à esquerda para indicar
                que este link pertence à seção acima.
            -->
            <a class="nav-link sub-nav-link {% if request.endpoint == 'usuarios_cadastrar' %}active{% endif %}"
               href="{{ url_for('usuarios_cadastrar') }}">
                <i class="bi bi-person-plus me-2"></i>Cadastrar
            </a>
        </li>
        <li class="nav-item">
            <!--
                O 'in' verifica se o endpoint atual é um dos três listados.
                Assim, o link "Listar" fica ativo tanto na listagem
                quanto nas páginas de visualizar e alterar.
            -->
            <a class="nav-link sub-nav-link {% if request.endpoint in ['usuarios_listar','usuarios_visualizar','usuarios_alterar'] %}active{% endif %}"
               href="{{ url_for('usuarios_listar') }}">
                <i class="bi bi-people me-2"></i>Listar
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint == 'usuarios_relatorio' %}active{% endif %}"
               href="{{ url_for('usuarios_relatorio') }}">
                <i class="bi bi-file-earmark-bar-graph me-2"></i>Relatório
            </a>
        </li>

        <!-- ── Seção Funções ── -->
        <li class="nav-section-title">Funções</li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint == 'funcoes_cadastrar' %}active{% endif %}"
               href="{{ url_for('funcoes_cadastrar') }}">
                <i class="bi bi-shield-plus me-2"></i>Cadastrar
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint in ['funcoes_listar','funcoes_visualizar','funcoes_alterar'] %}active{% endif %}"
               href="{{ url_for('funcoes_listar') }}">
                <i class="bi bi-shield-check me-2"></i>Listar
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint == 'funcoes_relatorio' %}active{% endif %}"
               href="{{ url_for('funcoes_relatorio') }}">
                <i class="bi bi-file-earmark-bar-graph me-2"></i>Relatório
            </a>
        </li>

        <!-- ── Seção Tarefas ── -->
        <li class="nav-section-title">Tarefas</li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint == 'tarefas_cadastrar' %}active{% endif %}"
               href="{{ url_for('tarefas_cadastrar') }}">
                <i class="bi bi-plus-circle me-2"></i>Cadastrar
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint in ['tarefas_listar','tarefas_visualizar','tarefas_alterar'] %}active{% endif %}"
               href="{{ url_for('tarefas_listar') }}">
                <i class="bi bi-list-task me-2"></i>Listar
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link sub-nav-link {% if request.endpoint == 'tarefas_relatorio' %}active{% endif %}"
               href="{{ url_for('tarefas_relatorio') }}">
                <i class="bi bi-file-earmark-bar-graph me-2"></i>Relatório
            </a>
        </li>

    </ul>

    <!-- Rodapé da sidebar com o botão de logout -->
    <div class="sidebar-footer">
        <a class="nav-link text-white-50" href="{{ url_for('logout') }}">
            <i class="bi bi-box-arrow-left me-2"></i>Sair
        </a>
    </div>
</nav>

<!-- ═══════════════════════════════════════════════════════════════
     CONTEÚDO PRINCIPAL - Área à direita da sidebar
     ═══════════════════════════════════════════════════════════════ -->
<div class="main-content">

    <!-- Barra superior do dashboard -->
    <nav class="top-navbar">

        <!-- Título da página atual, preenchido por cada template filho. -->
        <span class="fw-semibold text-dark">{% block page_title %}{% endblock %}</span>

        <div class="ms-auto d-flex align-items-center gap-3">
            <span class="text-muted small d-none d-md-inline">
                <i class="bi bi-bell me-1"></i>Notificações
            </span>

            <!-- Dropdown com informações do usuário logado -->
            <div class="dropdown">
                <a class="d-flex align-items-center text-dark text-decoration-none dropdown-toggle"
                   href="#" data-bs-toggle="dropdown">
                    <!--
                        usuario_logado é uma variável injetada em todos os templates
                        pelo context_processor que vamos criar no app.py.
                        Ela contém os dados do usuário que está na sessão.
                        'iniciais' é uma string com as iniciais do nome (ex: "JS" para João Silva).
                    -->
                    <div class="avatar-circle me-2">
                        {{ usuario_logado.iniciais if usuario_logado else '??' }}
                    </div>
                    <span class="fw-semibold small d-none d-md-inline">
                        {{ usuario_logado.nome if usuario_logado else 'Visitante' }}
                    </span>
                </a>

                <!-- Menu dropdown com dados do usuário -->
                <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                    <li class="px-3 py-2">
                        <div class="fw-semibold">
                            {{ usuario_logado.nome if usuario_logado else '' }}
                        </div>
                        <div class="text-muted small">
                            {{ usuario_logado.email if usuario_logado else '' }}
                        </div>
                        {% if usuario_logado %}
                        <!-- Exibe a função do usuário (ex: Administrador) como badge. -->
                        <span class="badge bg-primary-subtle text-primary mt-1">
                            {{ usuario_logado.funcao }}
                        </span>
                        {% endif %}
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                        <a class="dropdown-item text-danger" href="{{ url_for('logout') }}">
                            <i class="bi bi-box-arrow-left me-2"></i>Sair
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Área de conteúdo da página -->
    <main class="p-4">

        <!--
            Flash messages são mensagens temporárias enviadas pelo Flask
            para informar o usuário sobre o resultado de uma ação
            (ex: "Usuário salvo com sucesso!" ou "Erro ao salvar.").
            get_flashed_messages(with_categories=true) retorna uma lista de
            tuplas (categoria, mensagem), onde a categoria define a cor
            do alerta Bootstrap (success=verde, danger=vermelho, warning=amarelo).
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

        <!-- Conteúdo específico de cada página é inserido aqui. -->
        {% block content %}{% endblock %}
    </main>

</div>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

<!--
    {% block scripts %}{% endblock %} permite que páginas filhas
    adicionem seus próprios scripts JavaScript ao final do HTML.
-->
{% block scripts %}{% endblock %}
</body>
</html>
```

---

## 5. Criando o index.html

O `index.html` é a página inicial pública do CasaGestor, a primeira que o visitante vê ao acessar o sistema. Ela herda o layout do `base_public.html` e preenche apenas o bloco de conteúdo.

Crie o arquivo `index.html` diretamente dentro da pasta `templates`:

```html
<!--
    extends "base_public.html" diz ao Jinja2 que este arquivo
    herda toda a estrutura do base_public.html.
    Só precisamos definir os blocos que queremos preencher.
-->
{% extends "base_public.html" %}

<!-- Define o título que aparece na aba do navegador. -->
{% block title %}CasaGestor — Gestão de Tarefas Domésticas{% endblock %}

{% block content %}

<!-- ── Seção Hero (banner principal) ──────────────────────────────── -->
<!--
    A classe hero-section está definida no style.css e aplica
    o gradiente roxo-laranja como fundo desta seção.
-->
<section class="hero-section">
    <div class="container text-center">
        <h1 class="display-4 fw-bold mb-3">Organize sua casa com facilidade</h1>
        <p class="lead mb-4" style="opacity:.9;">
            CasaGestor é a plataforma completa para gerenciar tarefas domésticas, distribuir
            responsabilidades e manter todos os moradores na mesma página.
        </p>
        <div class="d-flex justify-content-center gap-3 flex-wrap">
            <a href="{{ url_for('cadastro') }}" class="btn btn-warning btn-lg fw-semibold px-4">
                Começar Agora
            </a>
            <a href="{{ url_for('login') }}" class="btn btn-outline-light btn-lg px-4">
                Já tenho conta
            </a>
        </div>
    </div>
</section>

<!-- ── Seção de Funcionalidades ───────────────────────────────────── -->
<section class="py-5">
    <div class="container">
        <div class="text-center mb-5">
            <h2 class="fw-bold">Tudo que você precisa para organizar seu lar</h2>
            <p class="text-muted">Funcionalidades pensadas para o dia a dia de cada família</p>
        </div>
        <div class="row g-4">

            <!-- Cada card descreve uma funcionalidade do sistema. -->
            <!-- feature-icon é a classe do style.css que cria o ícone com gradiente. -->
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="feature-icon mx-auto">
                        <i class="bi bi-list-check"></i>
                    </div>
                    <h5 class="fw-bold">Gestão de Tarefas</h5>
                    <p class="text-muted mb-0">Crie, atribua e acompanhe tarefas com prioridades e prazos definidos para cada morador.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="feature-icon mx-auto">
                        <i class="bi bi-people-fill"></i>
                    </div>
                    <h5 class="fw-bold">Múltiplos Usuários</h5>
                    <p class="text-muted mb-0">Adicione todos os moradores e distribua as responsabilidades de forma justa e transparente.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="feature-icon mx-auto">
                        <i class="bi bi-graph-up-arrow"></i>
                    </div>
                    <h5 class="fw-bold">Relatórios Detalhados</h5>
                    <p class="text-muted mb-0">Visualize o progresso das tarefas com relatórios completos e filtros personalizados.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="feature-icon mx-auto">
                        <i class="bi bi-shield-check"></i>
                    </div>
                    <h5 class="fw-bold">Controle de Acesso</h5>
                    <p class="text-muted mb-0">Defina funções e permissões para cada membro, garantindo a segurança das informações.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="feature-icon mx-auto">
                        <i class="bi bi-bell-fill"></i>
                    </div>
                    <h5 class="fw-bold">Notificações</h5>
                    <p class="text-muted mb-0">Receba alertas sobre tarefas próximas do prazo e acompanhe atualizações em tempo real.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm text-center p-4">
                    <div class="feature-icon mx-auto">
                        <i class="bi bi-phone-fill"></i>
                    </div>
                    <h5 class="fw-bold">Acesso em Qualquer Lugar</h5>
                    <p class="text-muted mb-0">Interface responsiva acessível de qualquer dispositivo — computador, tablet ou celular.</p>
                </div>
            </div>

        </div>
    </div>
</section>

<!-- ── Seção Como Funciona ─────────────────────────────────────────── -->
<section class="bg-light py-5">
    <div class="container">
        <div class="text-center mb-5">
            <h2 class="fw-bold">Como funciona?</h2>
            <p class="text-muted">Três passos simples para transformar a organização da sua casa</p>
        </div>
        <div class="row g-4 justify-content-center">
            <div class="col-md-3 text-center">
                <!-- Círculo numerado indicando a ordem dos passos. -->
                <div class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-3"
                     style="width:56px;height:56px;font-size:1.4rem;font-weight:700;">1</div>
                <h6 class="fw-bold">Cadastre-se</h6>
                <p class="text-muted small mb-0">Crie sua conta gratuitamente em poucos minutos.</p>
            </div>
            <div class="col-md-3 text-center">
                <div class="rounded-circle bg-secondary text-white d-inline-flex align-items-center justify-content-center mb-3"
                     style="width:56px;height:56px;font-size:1.4rem;font-weight:700;">2</div>
                <h6 class="fw-bold">Adicione Membros</h6>
                <p class="text-muted small mb-0">Convide os moradores e defina a função de cada um.</p>
            </div>
            <div class="col-md-3 text-center">
                <div class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-3"
                     style="width:56px;height:56px;font-size:1.4rem;font-weight:700;">3</div>
                <h6 class="fw-bold">Gerencie Tarefas</h6>
                <p class="text-muted small mb-0">Crie tarefas, atribua responsáveis e acompanhe o progresso.</p>
            </div>
        </div>
    </div>
</section>

<!-- ── CTA Final (chamada para ação) ──────────────────────────────── -->
<section class="py-5 text-center" style="background:linear-gradient(135deg,#7B2FBE,#F47B20);">
    <div class="container text-white">
        <h2 class="fw-bold mb-3">Pronto para organizar sua casa?</h2>
        <p class="lead mb-4" style="opacity:.9;">Comece hoje mesmo e veja a diferença na organização do seu lar.</p>
        <a href="{{ url_for('cadastro') }}" class="btn btn-light btn-lg fw-semibold px-5">
            Criar minha conta
        </a>
    </div>
</section>

{% endblock %}
```

---

## 6. Atualizando o app.py

O `app.py` precisa ser atualizado para importar `render_template` e usar os templates HTML nas rotas `index` e `sobre`. As demais rotas serão adicionadas nas próximas etapas.

Substitua todo o conteúdo do `app.py` pelo seguinte:

```python
# Importa as ferramentas do Flask que vamos usar nesta etapa.
# render_template: renderiza um arquivo HTML da pasta templates.
from flask import Flask, render_template

# Importa a função de inicialização do banco de dados.
from db import iniciar_bd

# Cria a instância da aplicação Flask.
app = Flask(__name__)

# Inicializa o banco de dados ao iniciar a aplicação.
iniciar_bd()


@app.context_processor
def injetar_usuario():
    """
    context_processor injeta variáveis automaticamente em todos os templates.
    Aqui retornamos 'usuario_logado' como None por enquanto.
    Nas próximas etapas, quando implementarmos o login, este valor
    virá da sessão do Flask com os dados reais do usuário logado.
    """
    return dict(usuario_logado=None)


# ── Rotas públicas ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    # render_template busca o arquivo dentro da pasta templates/
    # e retorna o HTML completo para o navegador.
    return render_template('index.html')


@app.route('/sobre')
def sobre():
    # A página 'sobre' ainda não existe, vamos criá-la nas próximas etapas.
    # Por enquanto retornamos um texto simples para não dar erro.
    return '<h1>Página Sobre — em breve</h1>'


@app.route('/login')
def login():
    return '<h1>Página de Login — em breve</h1>'


@app.route('/cadastro')
def cadastro():
    return '<h1>Página de Cadastro — em breve</h1>'


# Inicia o servidor de desenvolvimento.
if __name__ == '__main__':
    app.run(debug=True)
```

### Arquivo app.py completo para conferência

```python
from flask import Flask, render_template
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
    return '<h1>Página Sobre — em breve</h1>'


@app.route('/login')
def login():
    return '<h1>Página de Login — em breve</h1>'


@app.route('/cadastro')
def cadastro():
    return '<h1>Página de Cadastro — em breve</h1>'


if __name__ == '__main__':
    app.run(debug=True)
```

---

## 7. Estrutura do projeto até aqui

```
casagestor/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/
│   ├── auth/               (pasta criada, arquivos virão na Etapa 04)
│   ├── dashboard/          (pasta criada, arquivos virão na Etapa 04)
│   └── index.html
│   └── base_public.html
│   └── base_dashboard.html
├── venv/
├── app.py
├── db.py
├── schema.sql
├── requirements.txt
└── .gitignore
```

---

## 8. Testando a aplicação

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

Abra o navegador e acesse `http://127.0.0.1:5000`. Você deve ver a página inicial do CasaGestor com o banner roxo-laranja, os cards de funcionalidades e o menu superior com os botões **Entrar** e **Cadastrar**.

Verifique também:

- Clicar em **Entrar** deve levar para `/login` com a mensagem "Página de Login — em breve"
- Clicar em **Cadastrar** deve levar para `/cadastro` com a mensagem "Página de Cadastro — em breve"
- Clicar no logo **CasaGestor** no menu deve voltar para a página inicial

Para parar o servidor, pressione `Ctrl + C`.

---

## 9. Enviando as alterações para o GitHub

Com tudo funcionando, salve todos os arquivos no VS Code (`Ctrl + S`) e envie as alterações:

```
git add .
git commit -m "Etapa 03: templates base, static e página inicial"
git push
```

Acesse seu repositório no GitHub e confirme que as pastas `static` e `templates` aparecem na listagem com seus arquivos.

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| static/css/style.css | Criado com todas as cores, sidebar e componentes do projeto |
| static/js/script.js | Criado vazio, pronto para uso nas próximas etapas |
| templates/base_public.html | Layout base das páginas públicas com navbar e rodapé |
| templates/base_dashboard.html | Layout base do dashboard com sidebar completa |
| templates/index.html | Página inicial com hero, funcionalidades e CTA |
| app.py | Atualizado com render_template e context_processor |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

**Próxima etapa:** Criação de todas as rotas e templates do dashboard, funções e usuários.
