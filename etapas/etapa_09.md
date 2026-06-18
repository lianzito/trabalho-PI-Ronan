# Etapa 09 - Login, Logout, Proteção de Rotas e Administrador Padrão

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Implementar a função `garantir_admin` que cria um administrador padrão automaticamente
- Implementar o login com verificação de e-mail, senha e status do usuário
- Armazenar os dados do usuário logado na sessão do Flask
- Implementar o logout que encerra a sessão
- Criar o decorator `login_required` que protege todas as rotas do dashboard
- Atualizar o `context_processor` para injetar o usuário real da sessão nos templates
- Testar o sistema completo de autenticação
- Enviar as alterações para o GitHub

---

## Como o fluxo vai funcionar

**Login:**
1. O usuário acessa `/login` (GET) e vê o formulário
2. Preenche e-mail e senha e clica em Entrar (POST)
3. O Flask busca o usuário no banco pelo e-mail
4. Verifica se a senha digitada corresponde ao hash armazenado com `check_password_hash`
5. Verifica se o status do usuário é "Ativo"
6. Armazena os dados do usuário em `session` e redireciona para o dashboard

**Proteção de rotas:**
1. O decorator `@login_required` é adicionado em todas as rotas do dashboard
2. A cada requisição, ele verifica se `session['usuario']` existe
3. Se não existir, redireciona para o login com mensagem de aviso

**Logout:**
1. O usuário clica em Sair
2. O Flask limpa a sessão com `session.clear()`
3. Redireciona para a página de login

**Administrador padrão:**
1. Ao iniciar a aplicação, `garantir_admin` verifica se há algum usuário no banco
2. Se o banco estiver vazio (primeira execução), cria a função "Administrador" e o usuário `admin@casagestor.com` automaticamente
3. Isso evita o problema de ter um sistema sem nenhum usuário para fazer o primeiro login

---

## 1. Atualizando o app.py

Esta é a etapa com mais mudanças no `app.py`. Vamos implementar todas as peças na ordem certa para que o aluno entenda a dependência entre elas.

### 1.1 Novos imports

Localize o bloco de imports no topo do `app.py` e substitua pela versão abaixo. Estamos adicionando `session` ao import do Flask:

```python
# session permite armazenar dados entre requisições do mesmo usuário,
# como as informações de quem está logado.
# wraps é necessário para criar o decorator login_required corretamente.
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import iniciar_bd, execute_query, execute_one

app = Flask(__name__)
app.secret_key = '123456'

iniciar_bd()
```

### 1.2 Adicionando a função garantir_admin

Insira o código abaixo logo após a chamada de `iniciar_bd()`:

```python
def garantir_admin():
    """
    Verifica se existe algum usuário no banco.
    Se não existir, cria a função 'Administrador' e o usuário padrão.
    Isso garante que sempre haverá um acesso inicial ao sistema,
    evitando o problema de ficar bloqueado sem nenhuma conta para logar.
    """
    try:
        # Conta quantos usuários existem no banco.
        total = execute_one('SELECT COUNT(*) AS total FROM usuarios')

        # Se o banco já tiver pelo menos um usuário, não faz nada.
        if total and total['total'] > 0:
            return

        # Verifica se a função 'Administrador' já existe.
        funcao = execute_one(
            "SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',)
        )

        # Se a função não existir, cria com todas as permissões ativas.
        if not funcao:
            execute_query(
                """INSERT INTO funcoes
                       (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)
                   VALUES (%s, 'Ativo', %s, 1, 1, 1)""",
                ('Administrador', 'Acesso total ao sistema')
            )
            # Busca o id da função recém-criada para usá-lo no INSERT do usuário.
            funcao = execute_one(
                "SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',)
            )

        # Cria o usuário administrador padrão com senha hasheada.
        execute_query(
            """INSERT INTO usuarios
                   (nome, cpf, email, celular, estado, senha, status, funcao_id)
               VALUES (%s, %s, %s, %s, %s, %s, 'Ativo', %s)""",
            (
                'Administrador',
                '000.000.000-00',
                'admin@casagestor.com',
                '(00) 00000-0000',
                'SP',
                generate_password_hash('admin1234'),
                funcao['id_funcao']
            )
        )
        print('Usuário administrador padrão criado: admin@casagestor.com / admin1234')

    except Exception as e:
        print(f'Erro ao garantir admin: {e}')


# Chama a função logo após inicializar o banco.
garantir_admin()
```

### 1.3 Adicionando o decorator login_required

Insira o código abaixo logo após a chamada de `garantir_admin()`:

```python
def login_required(f):
    """
    Decorator que protege as rotas do dashboard.
    Um decorator é uma função que envolve outra função para adicionar comportamento extra.
    Ao adicionar @login_required em uma rota, o Flask vai executar esta função
    ANTES de executar a rota. Se o usuário não estiver logado, ele é redirecionado.

    Como usar: adicione @login_required logo abaixo de @app.route(...) nas rotas protegidas.
    """
    # @wraps(f) preserva o nome e a documentação da função original.
    # Sem isso, todas as rotas decoradas teriam o mesmo nome internamente,
    # o que causaria erros no Flask.
    @wraps(f)
    def wrapper(*args, **kwargs):
        # session.get('usuario') retorna None se a chave não existir na sessão,
        # ou seja, se nenhum usuário estiver logado.
        if not session.get('usuario'):
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        # Se o usuário estiver logado, executa a rota normalmente.
        return f(*args, **kwargs)
    return wrapper
```

### 1.4 Atualizando o context_processor

Localize no `app.py` a função `injetar_usuario` e substitua pelo código abaixo:

```python
@app.context_processor
def injetar_usuario():
    """
    Disponibiliza o usuário logado em todos os templates automaticamente.
    Agora retorna os dados reais da sessão em vez de None fixo.
    O template acessa com: usuario_logado.nome, usuario_logado.iniciais, etc.
    """
    return dict(usuario_logado=session.get('usuario'))
```

### 1.5 Atualizando a rota login

Localize no `app.py` a função `login` e substitua pelo código abaixo:

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        # Busca o usuário pelo e-mail fazendo JOIN com funcoes
        # para trazer também as permissões da função.
        usuario = execute_one(
            '''SELECT u.id_usuario, u.nome, u.email, u.senha, u.status,
                      f.nome AS funcao,
                      f.gerenciar_funcoes,
                      f.gerenciar_usuarios,
                      f.gerenciar_tarefas
               FROM usuarios AS u
               INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
               WHERE u.email = %s''',
            (email,)
        )

        # Verificação 1: o e-mail existe no banco?
        # Verificação 2: a senha digitada corresponde ao hash armazenado?
        # Usamos 'or' para não revelar se foi o e-mail ou a senha que falhou,
        # o que seria uma brecha de segurança.
        if not usuario or not check_password_hash(usuario['senha'], senha):
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('login'))

        # Verificação 3: o usuário está ativo?
        if usuario['status'] != 'Ativo':
            flash('Usuário inativo. Contate o administrador.', 'warning')
            return redirect(url_for('login'))

        # Gera as iniciais do nome para exibir no avatar do dashboard.
        # Ex: "João Silva" vira "JS". Se tiver apenas um nome, usa as duas primeiras letras.
        partes = usuario['nome'].split()
        if len(partes) > 1:
            iniciais = (partes[0][0] + partes[-1][0]).upper()
        else:
            iniciais = partes[0][:2].upper()

        # Armazena os dados do usuário na sessão do Flask.
        # session funciona como um dicionário que persiste entre requisições
        # do mesmo navegador, usando um cookie assinado pelo secret_key.
        session['usuario'] = {
            'id':                  usuario['id_usuario'],
            'nome':                usuario['nome'],
            'email':               usuario['email'],
            'funcao':              usuario['funcao'],
            'iniciais':            iniciais,
            'gerenciar_funcoes':   usuario['gerenciar_funcoes'],
            'gerenciar_usuarios':  usuario['gerenciar_usuarios'],
            'gerenciar_tarefas':   usuario['gerenciar_tarefas'],
        }

        flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
        return redirect(url_for('home'))

    return render_template('auth/login.html')
```

### 1.6 Atualizando a rota logout

Localize no `app.py` a função `logout` e substitua pelo código abaixo:

```python
@app.route('/logout')
def logout():
    # session.clear() remove todos os dados da sessão,
    # efetivamente deslogando o usuário.
    session.clear()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('login'))
```

### 1.7 Adicionando @login_required nas rotas do dashboard

Agora precisamos proteger todas as rotas do dashboard adicionando o decorator `@login_required`. Localize cada rota abaixo no `app.py` e adicione `@login_required` logo abaixo do `@app.route(...)`:

**Dashboard:**
```python
@app.route('/home')
@login_required          # <- adicionar esta linha
def home():
    ...
```

**Funções (todas as cinco rotas):**
```python
@app.route('/funcoes/listar')
@login_required
def funcoes_listar():
    ...

@app.route('/funcoes/cadastrar', methods=['GET', 'POST'])
@login_required
def funcoes_cadastrar():
    ...

@app.route('/funcoes/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def funcoes_alterar(id):
    ...

@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
@login_required
def funcoes_excluir(id):
    ...

@app.route('/funcoes/visualizar/<int:id>')
@login_required
def funcoes_visualizar(id):
    ...

@app.route('/funcoes/relatorio')
@login_required
def funcoes_relatorio():
    ...
```

**Usuários (todas as seis rotas):**
```python
@app.route('/usuarios/listar')
@login_required
def usuarios_listar():
    ...

@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
@login_required
def usuarios_cadastrar():
    ...

@app.route('/usuarios/alterar/<int:id>', methods=['GET', 'POST'])
@login_required
def usuarios_alterar(id):
    ...

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def usuarios_excluir(id):
    ...

@app.route('/usuarios/visualizar/<int:id>')
@login_required
def usuarios_visualizar(id):
    ...

@app.route('/usuarios/relatorio')
@login_required
def usuarios_relatorio():
    ...
```

**Tarefas (todas as cinco rotas):**
```python
@app.route('/tarefas/listar')
@login_required
def tarefas_listar():
    ...

@app.route('/tarefas/cadastrar')
@login_required
def tarefas_cadastrar():
    ...

@app.route('/tarefas/alterar/<int:id>')
@login_required
def tarefas_alterar(id):
    ...

@app.route('/tarefas/visualizar/<int:id>')
@login_required
def tarefas_visualizar(id):
    ...

@app.route('/tarefas/relatorio')
@login_required
def tarefas_relatorio():
    ...
```

### Arquivo app.py completo para conferência

```python
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import iniciar_bd, execute_query, execute_one

app = Flask(__name__)
app.secret_key = '123456'

iniciar_bd()


def garantir_admin():
    """
    Verifica se existe algum usuário no banco.
    Se não existir, cria a função 'Administrador' e o usuário padrão.
    """
    try:
        total = execute_one('SELECT COUNT(*) AS total FROM usuarios')
        if total and total['total'] > 0:
            return

        funcao = execute_one(
            "SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',)
        )
        if not funcao:
            execute_query(
                """INSERT INTO funcoes
                       (nome, status, descricao, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas)
                   VALUES (%s, 'Ativo', %s, 1, 1, 1)""",
                ('Administrador', 'Acesso total ao sistema')
            )
            funcao = execute_one(
                "SELECT id_funcao FROM funcoes WHERE nome = %s", ('Administrador',)
            )

        execute_query(
            """INSERT INTO usuarios
                   (nome, cpf, email, celular, estado, senha, status, funcao_id)
               VALUES (%s, %s, %s, %s, %s, %s, 'Ativo', %s)""",
            (
                'Administrador',
                '000.000.000-00',
                'admin@casagestor.com',
                '(00) 00000-0000',
                'SP',
                generate_password_hash('admin1234'),
                funcao['id_funcao']
            )
        )
        print('Usuário administrador padrão criado: admin@casagestor.com / admin1234')

    except Exception as e:
        print(f'Erro ao garantir admin: {e}')


garantir_admin()


def login_required(f):
    """Decorator que protege as rotas do dashboard."""
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
                      f.gerenciar_funcoes,
                      f.gerenciar_usuarios,
                      f.gerenciar_tarefas
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
        if len(partes) > 1:
            iniciais = (partes[0][0] + partes[-1][0]).upper()
        else:
            iniciais = partes[0][:2].upper()

        session['usuario'] = {
            'id':                 usuario['id_usuario'],
            'nome':               usuario['nome'],
            'email':              usuario['email'],
            'funcao':             usuario['funcao'],
            'iniciais':           iniciais,
            'gerenciar_funcoes':  usuario['gerenciar_funcoes'],
            'gerenciar_usuarios': usuario['gerenciar_usuarios'],
            'gerenciar_tarefas':  usuario['gerenciar_tarefas'],
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
    return render_template('dashboard/home.html')


# ── Rotas de Funções ──────────────────────────────────────────────────────────

@app.route('/funcoes/listar')
@login_required
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
@login_required
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
@login_required
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
@login_required
def funcoes_excluir(id):
    try:
        execute_query('DELETE FROM funcoes WHERE id_funcao = %s', (id,))
        flash('Função excluída com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir função: {e}', 'danger')
    return redirect(url_for('funcoes_listar'))


@app.route('/funcoes/visualizar/<int:id>')
@login_required
def funcoes_visualizar(id):
    item = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))
    if not item:
        flash('Função não encontrada.', 'danger')
        return redirect(url_for('funcoes_listar'))
    return render_template('dashboard/funcoes/visualizar.html', item=item)


@app.route('/funcoes/relatorio')
@login_required
def funcoes_relatorio():
    return render_template('dashboard/funcoes/relatorio.html')


# ── Rotas de Usuários ─────────────────────────────────────────────────────────

@app.route('/usuarios/listar')
@login_required
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
@login_required
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
@login_required
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
                        nome = %s, cpf = %s, data_nascimento = %s, email = %s,
                        celular = %s, cep = %s, logradouro = %s, numero = %s,
                        complemento = %s, bairro = %s, cidade = %s, estado = %s,
                        senha = %s, status = %s, funcao_id = %s
                    WHERE id_usuario = %s
                '''
                dados = (
                    nome, cpf, data_nascimento, email, celular,
                    cep, logradouro, numero, complemento, bairro,
                    cidade, estado, generate_password_hash(senha),
                    status, funcao_id, id
                )
            else:
                sql = '''
                    UPDATE usuarios SET
                        nome = %s, cpf = %s, data_nascimento = %s, email = %s,
                        celular = %s, cep = %s, logradouro = %s, numero = %s,
                        complemento = %s, bairro = %s, cidade = %s, estado = %s,
                        status = %s, funcao_id = %s
                    WHERE id_usuario = %s
                '''
                dados = (
                    nome, cpf, data_nascimento, email, celular,
                    cep, logradouro, numero, complemento, bairro,
                    cidade, estado, status, funcao_id, id
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
@login_required
def usuarios_excluir(id):
    try:
        execute_query('DELETE FROM usuarios WHERE id_usuario = %s', (id,))
        flash('Usuário excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {e}', 'danger')
    return redirect(url_for('usuarios_listar'))


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


@app.route('/usuarios/relatorio')
@login_required
def usuarios_relatorio():
    return render_template('dashboard/usuarios/relatorio.html')


# ── Rotas de Tarefas ──────────────────────────────────────────────────────────

@app.route('/tarefas/listar')
@login_required
def tarefas_listar():
    return '<h1>Tarefas — em breve</h1>'


@app.route('/tarefas/cadastrar')
@login_required
def tarefas_cadastrar():
    return '<h1>Cadastrar Tarefa — em breve</h1>'


@app.route('/tarefas/alterar/<int:id>')
@login_required
def tarefas_alterar(id):
    return '<h1>Alterar Tarefa — em breve</h1>'


@app.route('/tarefas/visualizar/<int:id>')
@login_required
def tarefas_visualizar(id):
    return '<h1>Visualizar Tarefa — em breve</h1>'


@app.route('/tarefas/relatorio')
@login_required
def tarefas_relatorio():
    return '<h1>Relatório de Tarefas — em breve</h1>'


if __name__ == '__main__':
    app.run(debug=True)
```

---

## 2. Testando o sistema completo

No terminal do VS Code, com o ambiente virtual ativo, rode a aplicação:

```
python app.py
```

### Teste 1: Administrador padrão criado automaticamente

Se o banco estiver vazio (ou se você apagou os registros anteriores), o terminal deve exibir na inicialização:

```
Banco e tabelas inicializados com sucesso!
Usuário administrador padrão criado: admin@casagestor.com / admin1234
```

Confirme no MySQL Workbench:

```sql
USE casa_gestor;
SELECT nome, email, status FROM usuarios;
SELECT nome, gerenciar_funcoes, gerenciar_usuarios, gerenciar_tarefas FROM funcoes;
```

### Teste 2: Proteção de rotas sem login

1. Sem estar logado, tente acessar diretamente `http://127.0.0.1:5000/home`
2. O sistema deve redirecionar para `/login` com a mensagem amarela "Faça login para acessar o sistema."
3. Tente também `/funcoes/listar` e `/usuarios/listar` e confirme o mesmo comportamento

### Teste 3: Login com credenciais inválidas

1. Acesse `/login`
2. Digite um e-mail que não existe e qualquer senha
3. A mensagem "E-mail ou senha inválidos." deve aparecer em vermelho
4. Digite o e-mail correto mas uma senha errada
5. A mesma mensagem deve aparecer (o sistema não revela qual dos dois campos está errado)

### Teste 4: Login com usuário inativo

1. No Workbench, atualize temporariamente o status de um usuário para Inativo:
   ```sql
   UPDATE usuarios SET status = 'Inativo' WHERE email = 'admin@casagestor.com';
   ```
2. Tente fazer login com esse usuário
3. A mensagem "Usuário inativo. Contate o administrador." deve aparecer em amarelo
4. Restaure o status:
   ```sql
   UPDATE usuarios SET status = 'Ativo' WHERE email = 'admin@casagestor.com';
   ```

### Teste 5: Login com sucesso

1. Acesse `/login`
2. Digite `admin@casagestor.com` e `admin1234`
3. Você deve ser redirecionado para `/home` com a mensagem "Bem-vindo, Administrador!"
4. A sidebar deve aparecer corretamente
5. O avatar no canto superior direito deve mostrar as iniciais "AD" e o nome "Administrador"
6. O dropdown deve mostrar o e-mail `admin@casagestor.com` e o badge com a função "Administrador"

### Teste 6: Navegação completa logado

Com o login feito, navegue por todas as seções e confirme que tudo funciona:

- Listagem de funções com dados reais do banco
- Cadastrar, visualizar, alterar e excluir uma função
- Listagem de usuários com dados reais do banco
- Cadastrar, visualizar, alterar e excluir um usuário

### Teste 7: Logout

1. Clique em **Sair** na sidebar ou no dropdown do avatar
2. Você deve ser redirecionado para `/login` com a mensagem "Sessão encerrada com sucesso."
3. Tente acessar `/home` novamente
4. Confirme que o sistema redireciona para o login, pois a sessão foi encerrada

---

## 3. Enviando as alterações para o GitHub

```
git add .
git commit -m "Etapa 09: login, logout, login_required e garantir_admin"
git push
```

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| Imports | Adicionados `wraps` e `session` |
| garantir_admin | Cria função e usuário admin automaticamente se o banco estiver vazio |
| login_required | Decorator que protege rotas verificando a sessão |
| context_processor | Atualizado para retornar o usuário real da sessão |
| login | Implementado com verificação de senha (hash), status e geração de iniciais |
| logout | Implementado com `session.clear()` |
| Rotas protegidas | `@login_required` adicionado em todas as rotas do dashboard, funções, usuários e tarefas |
| Testes | Proteção de rotas, login válido e inválido, usuário inativo, logout verificados |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

## Parabéns, o projeto está completo!

O CasaGestor agora tem todas as funcionalidades implementadas:

- Sistema de autenticação com login e logout seguros
- Proteção de todas as rotas internas com `@login_required`
- CRUD completo de funções com controle de permissões
- CRUD completo de usuários com hash de senha
- Criação automática do administrador padrão na primeira execução
- Interface responsiva com sidebar, flash messages e modais de confirmação

O próximo passo natural seria implementar o CRUD de tarefas seguindo exatamente o mesmo padrão aprendido nas etapas anteriores.
