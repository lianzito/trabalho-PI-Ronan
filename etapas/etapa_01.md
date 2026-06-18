# Etapa 01 - Criação do Projeto

## O que você vai aprender nesta etapa

Nesta etapa você vai:

- Criar a pasta do projeto no Desktop
- Abrir a pasta no VS Code
- Criar e ativar um ambiente virtual (venv)
- Instalar o Flask e o MySQL Connector
- Criar o primeiro arquivo `app.py` com uma rota simples
- Criar o arquivo `.gitignore`
- Enviar o projeto para o GitHub

Ao final desta etapa, o projeto vai estar no ar no GitHub e rodando localmente no navegador.

---

## Pré-requisitos

Antes de começar, certifique-se de que você tem instalado na sua máquina:

- **Python 3.10 ou superior** (durante a instalação, marque a opção "Add Python to PATH")
- **VS Code** (editor de código)
- **Git** (para versionar e enviar o código ao GitHub)
- **Conta no GitHub** (gratuita, em [github.com](https://github.com))

Para verificar se o Python está instalado corretamente, abra o **Prompt de Comando** e digite:

```
python --version
```

Se aparecer algo como `Python 3.12.0`, está tudo certo.

---

## 1. Criando a pasta do projeto

Vamos criar a pasta do projeto diretamente pelo Prompt de Comando.

**Como abrir o Prompt de Comando:**
Pressione `Windows + R`, digite `cmd` e pressione Enter.

Com o Prompt aberto, navegue até o Desktop e crie a pasta:

```
cd %USERPROFILE%\Desktop
mkdir casagestor
cd casagestor
```

Explicando cada linha:

- `cd %USERPROFILE%\Desktop` - navega até o Desktop do seu usuário
- `mkdir casagestor` - cria a pasta chamada `casagestor`
- `cd casagestor` - entra dentro da pasta recém-criada

---

## 2. Abrindo a pasta no VS Code

Ainda dentro do Prompt de Comando, digite:

```
code .
```

O ponto (`.`) significa "abrir o VS Code nesta pasta atual". O VS Code vai abrir com a pasta `casagestor` pronta para uso.

> Se o comando `code .` não funcionar, abra o VS Code manualmente, clique em **File > Open Folder** e selecione a pasta `casagestor` no Desktop.

---

## 3. Abrindo o terminal dentro do VS Code

A partir daqui, vamos usar o **terminal integrado do VS Code** em vez do Prompt de Comando separado. Isso é mais prático porque você pode ver o código e o terminal na mesma tela.

Para abrir o terminal no VS Code:
- Clique no menu **Terminal** (na barra superior)
- Clique em **New Terminal**

Um painel vai aparecer na parte de baixo do VS Code, já posicionado dentro da pasta `casagestor`.

---

## 4. Criando o ambiente virtual (venv)

Um ambiente virtual é um espaço isolado onde as bibliotecas do seu projeto ficam guardadas, sem misturar com outros projetos do computador. É uma boa prática sempre criar um.

No terminal do VS Code, digite:

```
python -m venv venv
```

Esse comando cria uma pasta chamada `venv` dentro do projeto. Você vai vê-la aparecer no painel esquerdo do VS Code.

**Ativando o ambiente virtual:**

```
venv\Scripts\activate
```

Quando o ambiente estiver ativo, o terminal vai mostrar `(venv)` no início da linha, assim:

```
(venv) C:\Users\SeuNome\Desktop\casagestor>
```

> Se aparecer um erro de permissão no Windows, execute o comando abaixo e tente ativar novamente:
> ```
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## 5. Instalando o Flask e o MySQL Connector

Com o ambiente virtual ativo, instale as duas bibliotecas que o projeto vai usar:

```
pip install Flask==3.1.0
pip install mysql-connector-python
```

Para confirmar que o Flask foi instalado corretamente:

```
flask --version
```

Deve aparecer algo como `Flask 3.1.0`.

---

## 6. Criando o arquivo requirements.txt

O arquivo `requirements.txt` registra quais bibliotecas o projeto precisa. Isso permite que qualquer pessoa que baixar o projeto instale tudo de uma vez.

No terminal, gere o arquivo automaticamente:

```
pip freeze > requirements.txt
```

Agora crie o arquivo manualmente no VS Code clicando no ícone de **novo arquivo** no painel esquerdo e nomeie como `requirements.txt`. O conteúdo gerado pelo comando acima já vai estar salvo no arquivo.

> O `requirements.txt` do projeto final contém apenas `Flask==3.1.0`, mas o `pip freeze` vai listar todas as dependências instaladas, o que é o comportamento correto.

---

## 7. Criando o arquivo app.py

Este é o arquivo principal da aplicação Flask. Clique no ícone de **novo arquivo** no painel esquerdo do VS Code, nomeie como `app.py` e escreva o seguinte código:

```python
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>CasaGestor funcionando!</h1>'


if __name__ == '__main__':
    app.run(debug=True)
```

Explicando cada parte:

- `from flask import Flask` - importa a classe Flask da biblioteca instalada
- `app = Flask(__name__)` - cria a aplicação Flask
- `@app.route('/')` - define que a função abaixo responde à URL raiz (`/`)
- `def index():` - função que será executada quando alguém acessar a URL `/`
- `return '<h1>...'` - retorna um texto HTML simples para o navegador
- `app.run(debug=True)` - inicia o servidor em modo de desenvolvimento (com reinício automático ao salvar)

---

## 8. Testando a aplicação

No terminal do VS Code, execute:

```
python app.py
```

Você vai ver uma saída parecida com:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Abra o navegador e acesse `http://127.0.0.1:5000`. Deve aparecer o texto **CasaGestor funcionando!** na tela.

Para parar o servidor, pressione `Ctrl + C` no terminal.

---

## 9. Criando o arquivo .gitignore

O arquivo `.gitignore` diz ao Git quais arquivos e pastas ele deve ignorar ao versionar o projeto. A pasta `venv`, por exemplo, não deve ir para o GitHub porque é grande e cada pessoa cria a sua própria.

Crie um novo arquivo no VS Code chamado `.gitignore` (com o ponto na frente) e cole o conteúdo abaixo:

```
# Ambiente virtual
venv/
env/
.env/
.venv/

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg-info/
dist/
build/
*.egg

# Flask
instance/
.webassets-cache
flask_session/

# Variáveis de ambiente
.env
.env.local
*.env

# Banco de dados
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema operacional
.DS_Store
Thumbs.db
desktop.ini
```

---

## 10. Estrutura do projeto até aqui

Ao final desta etapa, a estrutura de arquivos deve estar assim:

```
casagestor/
├── venv/               (pasta do ambiente virtual, ignorada pelo Git)
├── app.py
├── requirements.txt
└── .gitignore
```

---

## 11. Enviando o projeto para o GitHub

### 11.1 Criando o repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique no botão **New** (ou no ícone de `+` no canto superior direito)
3. Em **Repository name**, digite `casagestor`
4. Deixe como **Public**
5. **Não marque** nenhuma opção de inicializar com README, .gitignore ou licença (vamos enviar tudo do nosso computador)
6. Clique em **Create repository**

O GitHub vai mostrar uma página com instruções. Vamos usar os comandos da seção **"…or create a new repository on the command line"**.

### 11.2 Configurando o Git localmente

Se for a primeira vez que você usa o Git neste computador, configure seu nome e e-mail (use os mesmos do GitHub):

```
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

### 11.3 Inicializando e enviando o repositório

No terminal do VS Code, execute os comandos um por um:

```
git init
```
Inicializa o repositório Git na pasta do projeto.

```
git add .
```
Adiciona todos os arquivos ao "palco" do Git (staging area). O ponto significa "todos os arquivos".

```
git commit -m "Etapa 01: criação do projeto inicial"
```
Cria um "ponto de salvamento" com a mensagem descritiva.

```
git branch -M main
```
Renomeia o branch principal para `main` (padrão atual do GitHub).

```
git remote add origin https://github.com/SEU-USUARIO/casagestor.git
```
Conecta o repositório local ao repositório remoto no GitHub. Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub.

```
git push -u origin main
```
Envia o código para o GitHub.

> O Git pode pedir suas credenciais do GitHub. Se pediu um token ao invés de senha, acesse **GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)** e gere um token com permissão `repo`.

---

## Verificação final

Acesse `https://github.com/SEU-USUARIO/casagestor` no navegador. Você deve ver os três arquivos (`app.py`, `requirements.txt` e `.gitignore`) listados no repositório.

Localmente, com `python app.py` rodando, o navegador em `http://127.0.0.1:5000` deve exibir **CasaGestor funcionando!**.

Se ambos estiverem certos, a Etapa 01 está concluída.

---

## Resumo do que foi feito

| Passo | O que foi feito |
|---|---|
| Pasta do projeto | Criada no Desktop via Prompt de Comando |
| VS Code | Aberto dentro da pasta do projeto |
| Ambiente virtual | Criado e ativado com `venv` |
| Flask e MySQL Connector | Instalados com `pip` |
| requirements.txt | Gerado com `pip freeze` |
| app.py | Criado com uma rota simples na URL `/` |
| .gitignore | Criado para ignorar arquivos desnecessários |
| GitHub | Repositório criado e código enviado |

---

**Próxima etapa:** Conexão com o banco de dados, criação do `schema.sql` e do `db.py`.
