# Etapa 02 - Conexão com o Banco de Dados

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Entender o que é e para que serve o banco de dados no projeto
- Criar o arquivo `schema.sql` com a estrutura das tabelas
- Criar o arquivo `db.py` com as funções de conexão e consulta
- Conectar a aplicação Flask ao banco de dados na inicialização
- Testar se tudo funciona corretamente
- Enviar as alterações para o GitHub

---

## Pré-requisitos desta etapa

Antes de continuar, você precisa ter o **MySQL** e o **MySQL Workbench** instalados e rodando na sua máquina.

Para verificar, abra o **MySQL Workbench** e tente se conectar ao servidor local. Se a conexão abrir sem erro, está tudo certo.

Se ainda não tiver instalado, faça o download do **MySQL Installer** em [dev.mysql.com/downloads/installer](https://dev.mysql.com/downloads/installer) e instale o pacote completo, que já inclui o MySQL Server e o Workbench juntos.

> Durante a instalação, o MySQL pede para você definir uma senha para o usuário `root`. No projeto, o `db.py` usa senha vazia (`''`). Se você definiu uma senha durante a instalação, precisará ajustar essa linha no `db.py` quando chegarmos lá.

---

## 1. Entendendo a estrutura do banco de dados

O CasaGestor usa duas tabelas principais nesta etapa:

- `funcoes` - armazena os tipos de perfil de acesso (ex: Administrador, Usuário)
- `usuarios` - armazena os dados das pessoas que acessam o sistema

A tabela `usuarios` se relaciona com `funcoes` pelo campo `funcao_id`. Isso significa que todo usuário precisa ter uma função cadastrada antes de ser criado.

---

## 2. Criando o arquivo schema.sql

O `schema.sql` é um script SQL que cria o banco de dados e todas as tabelas automaticamente. Assim, qualquer pessoa que baixar o projeto consegue montar o banco de dados rodando apenas este arquivo, sem precisar configurar nada manualmente.

Crie um novo arquivo na raiz do projeto chamado `schema.sql` e escreva o seguinte conteúdo:

```sql
-- As linhas que começam com "--" são comentários no SQL e são ignoradas na execução.

-- O comando abaixo está comentado propositalmente.
-- Se precisar apagar e recriar o banco do zero durante o desenvolvimento,
-- remova o "--" da linha abaixo e execute o script novamente.
-- DROP DATABASE IF EXISTS casa_gestor;

-- Cria o banco de dados chamado "casa_gestor".
-- IF NOT EXISTS garante que o comando não vai dar erro se o banco já existir.
-- utf8mb4 é a codificação que suporta acentos e caracteres especiais do português.
CREATE DATABASE IF NOT EXISTS casa_gestor
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Diz ao MySQL para usar este banco de dados nas próximas instruções.
USE casa_gestor;

-- O DROP TABLE abaixo também está comentado. Use-o para resetar apenas esta tabela.
-- DROP TABLE IF EXISTS funcoes;

-- Cria a tabela de funções (perfis de acesso dos usuários).
CREATE TABLE IF NOT EXISTS funcoes(

    -- Chave primária: número único gerado automaticamente para cada registro (1, 2, 3...).
    id_funcao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Nome da função (ex: Administrador). UNIQUE garante que não haverá duplicatas.
    nome VARCHAR(20) NOT NULL UNIQUE,

    -- Status só aceita os valores 'Ativo' ou 'Inativo'. O padrão é 'Ativo'.
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',

    -- Descrição opcional da função.
    descricao VARCHAR(255),

    -- Permissões da função. BOOLEAN aceita 0 (falso) ou 1 (verdadeiro).
    -- O padrão 0 significa que a permissão começa desativada.
    gerenciar_funcoes  BOOLEAN DEFAULT 0,
    gerenciar_usuarios BOOLEAN DEFAULT 0,
    gerenciar_tarefas  BOOLEAN DEFAULT 0,

    -- Campos de log: preenchidos automaticamente pelo MySQL.
    -- criado_em registra quando o registro foi inserido.
    criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- alterado_em é atualizado automaticamente toda vez que o registro for editado.
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- DROP TABLE IF EXISTS usuarios;

-- Cria a tabela de usuários do sistema.
CREATE TABLE IF NOT EXISTS usuarios(

    -- Chave primária com geração automática.
    id_usuario BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Dados pessoais do usuário. NOT NULL significa que o campo é obrigatório.
    nome            VARCHAR(255) NOT NULL,

    -- UNIQUE no CPF garante que não haverá dois usuários com o mesmo CPF.
    cpf             VARCHAR(14)  NOT NULL UNIQUE,

    -- Data de nascimento é opcional (NULL permite que o campo fique vazio).
    data_nascimento DATE NULL,

    -- UNIQUE no e-mail garante que cada e-mail pertence a um único usuário.
    email    VARCHAR(255) NOT NULL UNIQUE,
    celular  VARCHAR(20)  NOT NULL,

    -- Campos de endereço, todos opcionais.
    cep         VARCHAR(9),
    logradouro  VARCHAR(255),
    numero      VARCHAR(20),
    complemento VARCHAR(100),
    bairro      VARCHAR(100),
    cidade      VARCHAR(100),

    -- Estado é obrigatório (NOT NULL).
    estado CHAR(2)      NOT NULL,
    pais   VARCHAR(50)  DEFAULT 'Brasil',

    -- Senha armazenada como hash (texto embaralhado), nunca em texto puro.
    senha  VARCHAR(255) NOT NULL,

    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',

    -- Chave estrangeira: vincula o usuário a uma função existente na tabela "funcoes".
    -- NOT NULL garante que todo usuário precisa ter uma função.
    funcao_id BIGINT UNSIGNED NOT NULL,

    -- Campos de log, iguais aos da tabela funcoes.
    criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    -- CONSTRAINT cria uma regra com nome "fk_usuario_funcao".
    -- FOREIGN KEY diz que "funcao_id" nesta tabela...
    -- REFERENCES aponta para "id_funcao" na tabela "funcoes".
    -- Isso impede cadastrar um usuário com uma funcao_id que não existe.
    CONSTRAINT fk_usuario_funcao
    FOREIGN KEY (funcao_id) REFERENCES funcoes (id_funcao)
);
```

---

## 3. Criando o arquivo db.py

O `db.py` é o módulo central de acesso ao banco de dados. Todo arquivo do projeto que precisar consultar ou gravar dados vai importar apenas este módulo.

Crie um novo arquivo na raiz do projeto chamado `db.py`.

### 3.1 Importações e configurações

Escreva o seguinte bloco no início do arquivo:

```python
# db.py — Módulo central de acesso ao banco de dados.
# Qualquer arquivo que precise do banco importa apenas este módulo.

# mysql.connector é a biblioteca que permite o Python conversar com o MySQL.
import mysql.connector
from mysql.connector import Error, pooling

# os permite trabalhar com caminhos de arquivos de forma independente do sistema operacional.
import os

# Dicionário com todos os parâmetros de conexão com o banco de dados.
# Centralizamos aqui para que qualquer mudança (ex: senha) seja feita em um único lugar.
_DB_PARAMS = {
    # Endereço do servidor MySQL. 'localhost' significa que está na própria máquina.
    'host': 'localhost',

    # Usuário do MySQL criado durante a instalação.
    'user': 'root',

    # Senha do usuário root. Deixe vazio ('') se não definiu senha na instalação.
    'password': '',

    # Nome do banco de dados que será usado pela aplicação.
    'database': 'casa_gestor',

    # Codificação de caracteres. Necessária para acentos funcionarem corretamente.
    'charset': 'utf8mb4',

    # Conjunto de regras do MySQL para validação de dados.
    'sql_mode': (
        'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
        'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
    ),

    # use_pure=True usa a implementação em Python puro, compatível com todos os ambientes.
    'use_pure': True,

    # Tempo máximo em segundos para tentar se conectar antes de desistir.
    'connection_timeout': 10,

    # autocommit=False significa que alterações no banco (INSERT, UPDATE, DELETE)
    # só são confirmadas quando o código chamar commit() explicitamente.
    # Isso evita dados corrompidos caso ocorra um erro no meio de uma operação.
    'autocommit': False,
}

# Variável que vai guardar o pool de conexões.
# Começa como None e é preenchida na primeira chamada de criar_pool().
_pool = None
```

### 3.2 Funções de pool e conexão

Insira o código abaixo depois do bloco de configurações (`_pool = None`):

```python
def criar_pool():
    # 'global' permite que esta função modifique a variável _pool
    # que foi definida fora dela (no escopo do módulo).
    global _pool

    # Só cria o pool se ele ainda não existir.
    # Isso garante que apenas um pool seja criado durante toda a execução da aplicação.
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            # Nome interno do pool, usado para identificação.
            pool_name='webapp_pool',

            # Número de conexões abertas permanentemente.
            # Para um projeto pequeno, 5 conexões é mais que suficiente.
            pool_size=5,

            # Limpa o estado da sessão ao devolver a conexão ao pool.
            pool_reset_session=True,

            # O ** "desempacota" o dicionário _DB_PARAMS,
            # passando cada chave como um argumento separado para a função.
            **_DB_PARAMS
        )


def get_connection():
    """Retorna uma conexão do pool. Levanta Exception em caso de falha."""
    try:
        # Garante que o pool foi criado antes de tentar pegar uma conexão.
        if _pool is None:
            criar_pool()

        # Pega uma conexão disponível do pool e a retorna para o chamador.
        return _pool.get_connection()

    except Error as e:
        # Se algo der errado, lança uma exceção com uma mensagem clara.
        raise Exception(f'Não foi possível obter conexão do pool: {e}')
```

### 3.3 Funções de consulta ao banco

Insira o código abaixo depois da função `get_connection`:

```python
def execute_query(sql, params=None, fetch=False):
    """
    Executa qualquer comando SQL de forma segura.

    Como usar:
        sql    -> string SQL com %s como marcadores de posição para os valores.
        params -> tupla com os valores que substituirão os %s no SQL.
        fetch  -> True para SELECT (retorna lista); False para INSERT/UPDATE/DELETE.

    Retorna:
        fetch=True  -> lista de dicionários, onde cada item é uma linha do resultado.
        fetch=False -> número inteiro com a quantidade de linhas afetadas.
    """
    # Pega uma conexão disponível do pool.
    conn = get_connection()

    try:
        # dictionary=True faz cada linha retornar como dicionário.
        # Assim acessamos usuario['nome'] em vez de usuario[0], muito mais legível.
        cursor = conn.cursor(dictionary=True)

        # Executa o SQL passando os parâmetros separados da string SQL.
        # Isso evita SQL Injection: o MySQL trata os valores como dados,
        # nunca como parte do comando SQL, mesmo que contenham caracteres especiais.
        # 'params or ()' usa uma tupla vazia se nenhum parâmetro for informado.
        cursor.execute(sql, params or ())

        if fetch:
            # Para SELECT: retorna todas as linhas como uma lista de dicionários.
            return cursor.fetchall()
        else:
            # Para INSERT/UPDATE/DELETE: confirma a alteração no banco de dados.
            conn.commit()
            # Retorna quantas linhas foram afetadas pelo comando.
            return cursor.rowcount

    except Error as e:
        # Em caso de erro, desfaz qualquer alteração parcial.
        # Isso garante que os dados não fiquem em estado inconsistente.
        conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')

    finally:
        # O bloco 'finally' sempre é executado, mesmo que ocorra um erro.
        # Garante que o cursor e a conexão sejam sempre fechados corretamente.
        cursor.close()
        # conn.close() não encerra a conexão fisicamente.
        # Ele apenas a devolve ao pool para ser reutilizada pela próxima requisição.
        conn.close()


def execute_one(sql, params=None):
    """
    Executa um SELECT e retorna apenas a primeira linha encontrada (ou None).
    Útil para buscar um único registro, como: SELECT * FROM usuarios WHERE id = 5.
    """
    # Reutiliza execute_query com fetch=True para obter a lista de resultados.
    resultados = execute_query(sql, params, fetch=True)

    # Se encontrou resultados, retorna apenas o primeiro item da lista.
    # Se não encontrou nada, retorna None.
    return resultados[0] if resultados else None
```

### 3.4 Função de inicialização do banco

Insira o código abaixo depois da função `execute_one`:

```python
def iniciar_bd():
    """
    Lê o arquivo schema.sql e executa cada comando para criar
    o banco de dados e as tabelas caso ainda não existam.
    Esta função é chamada uma vez ao iniciar a aplicação.
    """
    try:
        # Conecta ao MySQL SEM especificar o banco de dados.
        # Fazemos isso porque o banco 'casa_gestor' pode ainda não existir,
        # e o CREATE DATABASE no schema.sql vai criá-lo.
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )
        cursor = conn.cursor()

        # Monta o caminho completo até o arquivo schema.sql.
        # os.path.dirname(__file__) retorna a pasta onde o db.py está salvo.
        # os.path.join junta esse caminho com o nome do arquivo 'schema.sql'.
        arquivo_sql = os.path.join(os.path.dirname(__file__), 'schema.sql')

        # Abre e lê todo o conteúdo do schema.sql como texto.
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()

        # Divide o script inteiro em comandos individuais usando o ';' como separador.
        # O mysql.connector não consegue executar múltiplos comandos de uma vez,
        # então precisamos executar um por um.
        for stmt in script_sql.split(';'):
            # Remove espaços e quebras de linha desnecessários.
            stmt = stmt.strip()
            # Ignora partes vazias que surgem após o último ';'.
            if stmt:
                cursor.execute(stmt)

        # Confirma todas as operações executadas.
        conn.commit()
        cursor.close()
        conn.close()
        print('Banco e tabelas inicializados com sucesso!')

    except Exception as e:
        print(f'Erro ao inicializar o banco de dados: {e}')
```

---

## 4. Arquivo db.py completo para conferência

Antes de continuar, verifique se o seu `db.py` está exatamente assim:

```python
# db.py — Módulo central de acesso ao banco de dados.
# Qualquer arquivo que precise do banco importa apenas este módulo.

import mysql.connector
from mysql.connector import Error, pooling
import os

_DB_PARAMS = {
    'host':               'localhost',
    'user':               'root',
    'password':           '',
    'database':           'casa_gestor',
    'charset':            'utf8mb4',
    'sql_mode':           (
        'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
        'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
    ),
    'use_pure':           True,
    'connection_timeout': 10,
    'autocommit':         False,
}

_pool = None


def criar_pool():
    global _pool

    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name='webapp_pool',
            pool_size=5,
            pool_reset_session=True,
            **_DB_PARAMS
        )


def get_connection():
    """Retorna uma conexão do pool. Levanta Exception em caso de falha."""
    try:
        if _pool is None:
            criar_pool()
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')


def execute_query(sql, params=None, fetch=False):
    """
    Executa qualquer comando SQL de forma segura.

    Como usar:
        sql    -> string SQL com %s como marcadores de posição para os valores.
        params -> tupla com os valores que substituirão os %s no SQL.
        fetch  -> True para SELECT (retorna lista); False para INSERT/UPDATE/DELETE.

    Retorna:
        fetch=True  -> lista de dicionários, onde cada item é uma linha do resultado.
        fetch=False -> número inteiro com a quantidade de linhas afetadas.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount

    except Error as e:
        conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        cursor.close()
        conn.close()


def execute_one(sql, params=None):
    """
    Executa um SELECT e retorna apenas a primeira linha encontrada (ou None).
    Útil para buscar um único registro, como: SELECT * FROM usuarios WHERE id = 5.
    """
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None


def iniciar_bd():
    """
    Lê o arquivo schema.sql e executa cada comando para criar
    o banco de dados e as tabelas caso ainda não existam.
    Esta função é chamada uma vez ao iniciar a aplicação.
    """
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )
        cursor = conn.cursor()

        arquivo_sql = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()

        for stmt in script_sql.split(';'):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)

        conn.commit()
        cursor.close()
        conn.close()
        print('Banco e tabelas inicializados com sucesso!')

    except Exception as e:
        print(f'Erro ao inicializar o banco de dados: {e}')
```

---

## 5. Atualizando o app.py

O `app.py` já existe desde a Etapa 01. Vamos atualizá-lo para importar e chamar a função `iniciar_bd` do `db.py`.

Substitua todo o conteúdo do `app.py` pelo seguinte:

```python
# Importa a classe Flask da biblioteca instalada.
from flask import Flask

# Importa a função iniciar_bd do nosso módulo db.py.
from db import iniciar_bd

# Cria a instância da aplicação Flask.
# __name__ diz ao Flask qual é o arquivo principal do projeto.
app = Flask(__name__)

# Chama iniciar_bd() uma vez ao iniciar a aplicação.
# Ela lê o schema.sql e cria o banco e as tabelas se ainda não existirem.
iniciar_bd()


# Define a rota raiz '/'. Quando alguém acessar http://127.0.0.1:5000/,
# o Flask vai chamar a função index() e retornar o HTML abaixo.
@app.route('/')
def index():
    return '<h1>CasaGestor funcionando!</h1>'


# Inicia o servidor de desenvolvimento.
# debug=True reinicia o servidor automaticamente ao salvar qualquer arquivo.
if __name__ == '__main__':
    app.run(debug=True)
```

### Arquivo app.py completo para conferência

```python
from flask import Flask
from db import iniciar_bd

app = Flask(__name__)

iniciar_bd()


@app.route('/')
def index():
    return '<h1>CasaGestor funcionando!</h1>'


if __name__ == '__main__':
    app.run(debug=True)
```

---

## 6. Testando a conexão

No terminal do VS Code, certifique-se de que o ambiente virtual está ativo (deve aparecer `(venv)` no início da linha). Se não estiver, ative com:

```
venv\Scripts\activate
```

Em seguida, rode a aplicação:

```
python app.py
```

Se a conexão com o banco funcionar, você verá no terminal:

```
Banco e tabelas inicializados com sucesso!
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Se aparecer `Erro ao inicializar o banco de dados`, as causas mais comuns são:

- O MySQL não está rodando. Abra o **MySQL Workbench** e tente conectar ao servidor. Se não conseguir, vá ao **Gerenciador de Serviços** do Windows (pressione `Windows + R`, digite `services.msc`) e verifique se o serviço `MySQL80` está iniciado.
- A senha do `root` está incorreta no `db.py`. Ajuste o valor de `password` para a senha que você definiu durante a instalação.

Para parar o servidor, pressione `Ctrl + C`.

---

## 7. Verificando as tabelas no MySQL Workbench

Para confirmar que as tabelas foram criadas corretamente, abra o **MySQL Workbench**, conecte ao servidor local e execute o seguinte comando na aba de query:

```sql
USE casa_gestor;
SHOW TABLES;
```

O resultado deve exibir as duas tabelas criadas:

```
+------------------------+
| Tables_in_casa_gestor  |
+------------------------+
| funcoes                |
| usuarios               |
+------------------------+
```

Se quiser ver a estrutura detalhada de uma tabela, execute:

```sql
DESCRIBE funcoes;
```

---

## 8. Estrutura do projeto até aqui

```
casagestor/
├── venv/
├── app.py
├── db.py
├── schema.sql
├── requirements.txt
└── .gitignore
```

---

## 9. Enviando as alterações para o GitHub

Com tudo funcionando, salve todos os arquivos no VS Code (`Ctrl + S`) e envie as alterações para o GitHub:

```
git add .
git commit -m "Etapa 02: conexão com o banco de dados"
git push
```

Explicando cada comando:

- `git add .` - prepara todos os arquivos novos e modificados para o commit
- `git commit -m "..."` - cria o ponto de salvamento com uma mensagem descritiva
- `git push` - envia para o GitHub (desta vez não precisa de `-u origin main` porque já foi configurado na Etapa 01)

Acesse seu repositório no GitHub e confirme que os arquivos `db.py` e `schema.sql` aparecem na listagem.

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| schema.sql | Criado com a estrutura das tabelas `funcoes` e `usuarios` |
| db.py | Criado com pool de conexões e funções `execute_query` e `execute_one` |
| iniciar_bd() | Função que lê o `schema.sql` e cria o banco automaticamente ao iniciar |
| app.py | Atualizado para importar e chamar `iniciar_bd()` na inicialização |
| Teste | Aplicação rodada e banco criado com sucesso |
| Workbench | Tabelas verificadas com `SHOW TABLES` |
| GitHub | Alterações enviadas com `git add`, `git commit` e `git push` |

---

**Próxima etapa:** Criação dos templates base e da página inicial do sistema.
