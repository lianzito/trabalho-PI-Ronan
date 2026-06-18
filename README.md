# CasaGestor

Sistema web para gerenciamento de tarefas domésticas, desenvolvido com **Python**, **Flask** e **MySQL**. Permite cadastrar usuários com funções e permissões diferentes, atribuir e acompanhar tarefas do lar, e controlar o acesso ao sistema por meio de login e sessão.

Este repositório é também um **material de aprendizado estruturado em etapas**, pensado para quem está começando no desenvolvimento web com Flask e nunca teve contato com esse tipo de projeto.

---

## Índice

- [Etapas de desenvolvimento](#etapas-de-desenvolvimento)
- [Como baixar e rodar o projeto](#como-baixar-e-rodar-o-projeto)
- [Ordem de aprendizado e o que você vai saber fazer](#ordem-de-aprendizado-e-o-que-você-vai-saber-fazer)
- [Próximo desafio: CRUD de Tarefas](#próximo-desafio-crud-de-tarefas)
- [Recursos avançados prontos para explorar](#recursos-avançados-prontos-para-explorar)

---

## Etapas de desenvolvimento

O projeto foi construído em 9 etapas progressivas. Cada etapa está documentada em um arquivo dentro da pasta `etapas/` e pode ser seguida de forma independente.

| Etapa | Descrição |
|---|---|
| [01 - Criação do Projeto](etapas/etapa_01.md) | Configuração do ambiente do zero: criação da pasta do projeto, ambiente virtual Python, instalação do Flask e do conector MySQL, criação do `app.py` com a primeira rota, configuração do `.gitignore` e envio do projeto para o GitHub. |
| [02 - Conexão com o Banco de Dados](etapas/etapa_02.md) | Criação do `schema.sql` com a estrutura das tabelas `funcoes` e `usuarios`. Criação do `db.py` com pool de conexões e as funções `execute_query` e `execute_one`. Integração do banco de dados com a aplicação Flask na inicialização. |
| [03 - Criando a Base do Projeto](etapas/etapa_03.md) | Criação da pasta `static` com o `style.css` (cores, sidebar, componentes) e o `script.js`. Criação da pasta `templates` com os arquivos base: `base_public.html` (layout das páginas públicas) e `base_dashboard.html` (layout interno com sidebar completa). Criação da página inicial `index.html`. |
| [04 - Criando as Rotas e os Templates](etapas/etapa_04.md) | Criação de todos os templates HTML do sistema com dados estáticos: autenticação (login, cadastro, recuperar senha), home do dashboard, e todas as páginas de funções e usuários (listar, form, visualizar, relatório). Registro de todas as rotas no `app.py` sem integração com banco de dados ainda. |
| [05 - Listagem e Cadastro de Funções](etapas/etapa_05.md) | Primeira integração real com o banco de dados. Implementação do `SELECT` para listar funções dinamicamente no template com `{% for %}`. Implementação do `INSERT` via formulário POST com validação de campos obrigatórios, tratamento de erros e flash messages de sucesso e falha. |
| [06 - Alteração, Visualização e Exclusão de Funções](etapas/etapa_06.md) | CRUD completo de funções. Implementação do `SELECT` por ID para visualizar e pré-preencher o formulário de alteração. Implementação do `UPDATE` com formulário de action dinâmico conforme o modo (cadastrar ou alterar). Implementação do `DELETE` com modal de confirmação em JavaScript e proteção por método POST. |
| [07 - Listagem e Cadastro de Usuários](etapas/etapa_07.md) | Listagem de usuários com `INNER JOIN` para trazer o nome da função. Cadastro com múltiplas validações (campos obrigatórios, senhas conferindo, mínimo de caracteres, e-mail e CPF únicos). Armazenamento seguro de senha com `generate_password_hash` do Werkzeug. Formulário com `<select>` de funções populado dinamicamente do banco. |
| [08 - Alteração, Visualização e Exclusão de Usuários](etapas/etapa_08.md) | CRUD completo de usuários. Visualização com dois cards (dados pessoais e endereço) e tratamento de campos opcionais vazios. Alteração com dois `UPDATE` distintos: um que atualiza a senha e outro que a mantém intacta quando o campo é deixado em branco. Validação de duplicidade de e-mail e CPF excluindo o próprio registro. Exclusão com modal de confirmação. |
| [09 - Login, Logout, Proteção de Rotas e Admin Padrão](etapas/etapa_09.md) | Sistema completo de autenticação. Função `garantir_admin` que cria automaticamente o usuário administrador na primeira execução. Login com `check_password_hash`, verificação de status e armazenamento de dados na sessão do Flask. Decorator `login_required` aplicado em todas as rotas do dashboard. Logout com `session.clear()`. Exibição do usuário logado no avatar e dropdown da navbar. |

---

## Como baixar e rodar o projeto

### Pré-requisitos

Certifique-se de ter instalado na sua máquina:

- **Git** (para clonar o repositório)
- **Python 3.10 ou superior** (com a opção "Add Python to PATH" marcada durante a instalação)
- **XAMPP** com o módulo **MySQL** ativo

> O projeto usa o MySQL do XAMPP. Antes de continuar, abra o **XAMPP Control Panel** e clique em **Start** no módulo MySQL. O servidor precisa estar rodando para a aplicação funcionar.

---

### Passo 1: Clonar o repositório

Abra o **Prompt de Comando** (pressione `Windows + R`, digite `cmd` e pressione Enter) e execute:

```
cd %USERPROFILE%\Desktop
git clone https://github.com/GTI-Fatec-Jahu/pi-01-26.git
cd pi-01-26
```

---

### Passo 2: Criar e ativar o ambiente virtual

```
python -m venv venv
venv\Scripts\activate
```

Quando o ambiente estiver ativo, o terminal vai mostrar `(venv)` no início da linha.

---

### Passo 3: Instalar as dependências

```
pip install -r requirements.txt
pip install mysql-connector-python
```

---

### Passo 4: Configurar a conexão com o banco

Abra o arquivo `db.py` no VS Code e verifique as configurações de conexão:

```python
_DB_PARAMS = {
    'host':     'localhost',
    'user':     'root',
    'password': '',          # deixe vazio se não definiu senha no XAMPP
    'database': 'casa_gestor',
    ...
}
```

Se você definiu uma senha para o MySQL no XAMPP, preencha o campo `password` com ela. Caso contrário, deixe como string vazia.

Faça o mesmo ajuste na função `iniciar_bd()` no final do mesmo arquivo:

```python
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password=''   # ajuste aqui também se necessário
)
```

---

### Passo 5: Rodar a aplicação

```
python app.py
```

Na primeira execução, o terminal vai exibir:

```
Banco e tabelas inicializados com sucesso!
Usuário administrador padrão criado: admin@casagestor.com / admin1234
 * Running on http://127.0.0.1:5000
```

Abra o navegador e acesse `http://127.0.0.1:5000`.

---

### Credenciais de acesso padrão

| Campo | Valor |
|---|---|
| E-mail | admin@casagestor.com |
| Senha | admin1234 |

> Recomendamos alterar a senha padrão após o primeiro login acessando o cadastro do usuário Administrador.

---

## Ordem de aprendizado e o que você vai saber fazer

Seguindo as etapas do projeto na ordem, você aprende os fundamentos do desenvolvimento web com Flask de forma progressiva. Veja o que cada bloco de etapas ensina e como esses conceitos se conectam:

### Fundamentos (Etapas 01 a 03)

Você aprende a montar o ambiente de desenvolvimento do zero: criar um projeto Python isolado com ambiente virtual, instalar dependências, conectar ao banco de dados MySQL com pool de conexões e criar os primeiros templates HTML com herança usando Jinja2. Após este bloco, você entende como o Flask serve páginas, como os templates se comunicam entre si com `extends` e `block`, e como o CSS é organizado para um projeto com múltiplas seções.

### Estrutura de rotas e templates (Etapa 04)

Você aprende a separar as responsabilidades do sistema em rotas e templates, a usar `render_template` para renderizar HTML dinâmico, a passar variáveis do Python para o HTML com Jinja2 e a estruturar URLs com parâmetros como `<int:id>`. Após esta etapa, você entende como o Flask mapeia URLs para funções Python e como as páginas são organizadas em hierarquia de templates.

### CRUD com banco de dados (Etapas 05 a 08)

Este é o núcleo do projeto. Você aprende a executar as quatro operações fundamentais de qualquer sistema web:

- **Listar (SELECT):** buscar dados do banco e exibi-los em uma tabela HTML com `{% for %}`
- **Cadastrar (INSERT):** receber dados de um formulário via POST, validar, tratar erros e salvar no banco
- **Visualizar e Alterar (SELECT + UPDATE):** buscar um registro por ID, pré-preencher o formulário e salvar as alterações
- **Excluir (DELETE):** usar um modal de confirmação com JavaScript para evitar exclusões acidentais

Você também aprende conceitos importantes como: SQL Injection e como evitá-lo com parâmetros separados, hash de senhas com Werkzeug, validações no servidor, flash messages, JOIN entre tabelas e a diferença entre GET e POST.

### Autenticação (Etapa 09)

Você aprende a implementar um sistema de login completo: verificar credenciais com hash de senha, armazenar dados na sessão do Flask, criar um decorator reutilizável para proteger rotas e encerrar a sessão no logout. Após esta etapa, você entende como qualquer sistema web controla quem pode acessar o quê.

---

## Próximo desafio: CRUD de Tarefas

O sistema já tem as rotas de tarefas criadas no `app.py` (retornando mensagens provisórias) e os templates `templates/dashboard/tarefas/` prontos na Etapa 04. O CRUD de tarefas não foi implementado neste projeto para que você possa praticá-lo por conta própria, aplicando tudo o que aprendeu.

Para implementar o CRUD de tarefas, siga exatamente o mesmo raciocínio das etapas de funções e usuários:

**1. Crie a tabela no banco**

Adicione ao `schema.sql` uma tabela `tarefas` com os campos que fazem sentido para o sistema: título, descrição, responsável (com `FOREIGN KEY` para `usuarios`), prioridade, status e prazo. Execute o script no MySQL Workbench.

**2. Implemente a listagem**

Na rota `tarefas_listar`, escreva um `SELECT` com `JOIN` para trazer o nome do responsável junto. Atualize o template `tarefas/listar.html` para usar `{% for %}` com os dados reais, substituindo os dados fixos da Etapa 04.

**3. Implemente o cadastro**

Na rota `tarefas_cadastrar`, trate o POST lendo os campos com `request.form.get`, valide os dados obrigatórios e execute o `INSERT`. No GET, busque a lista de usuários do banco para popular o `<select>` de responsável no formulário.

**4. Implemente a visualização e a alteração**

Siga o mesmo padrão da Etapa 06 e Etapa 08: busque o registro pelo `id` com `execute_one`, pré-preencha o formulário no GET e execute o `UPDATE` no POST. Use a variável `modo` para que o mesmo template `form.html` sirva para cadastro e alteração.

**5. Implemente a exclusão**

Adicione a rota `tarefas_excluir` com método POST e o modal de confirmação no template `listar.html`, seguindo o mesmo padrão do modal de funções e usuários.

Se você conseguir implementar o CRUD de tarefas sem consultar as etapas anteriores, você dominou os conceitos fundamentais do desenvolvimento web com Flask.

---

## Recursos avançados prontos para explorar

O projeto foi construído com a base técnica necessária para suportar recursos mais avançados que não foram implementados neste momento. A principal razão é didática: adicionar mais camadas de lógica durante o aprendizado do CRUD tornaria o código mais difícil de acompanhar e poderia obscurecer os conceitos fundamentais.

### Validação de permissões por função

O sistema já armazena na sessão as permissões do usuário logado (`gerenciar_funcoes`, `gerenciar_usuarios`, `gerenciar_tarefas`). O banco de dados também já tem essas colunas na tabela `funcoes`. A estrutura está completamente pronta.

Para ativar a validação de permissões, bastaria criar decorators específicos por permissão, de forma análoga ao `login_required`:

```python
def requer_permissao(permissao):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            usuario = session.get('usuario')
            if not usuario or not usuario.get(permissao):
                flash('Você não tem permissão para acessar esta área.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return wrapper
    return decorator
```

E aplicá-los nas rotas protegidas:

```python
@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
@login_required
@requer_permissao('gerenciar_funcoes')
def funcoes_cadastrar():
    ...
```

Também seria possível ocultar itens da sidebar e botões de ação nos templates usando as permissões da sessão:

```html
{% if usuario_logado.gerenciar_funcoes %}
<li class="nav-item">
    <a class="nav-link sub-nav-link" href="{{ url_for('funcoes_cadastrar') }}">
        <i class="bi bi-shield-plus me-2"></i>Cadastrar
    </a>
</li>
{% endif %}
```

Esse recurso foi deixado de fora intencionalmente neste material para que você possa se concentrar em entender como os CRUDs funcionam antes de adicionar camadas de controle de acesso sobre eles.
