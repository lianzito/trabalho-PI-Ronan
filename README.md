Markdown
# CasaGestor

Sistema web completo para gerenciamento de tarefas e rotinas domésticas, desenvolvido com **Python**, **Flask** e **MySQL**. 

Este projeto foi construído como entrega final da disciplina, implementando o CRUD de Usuários e Funções base, além da finalização completa do CRUD de Tarefas e a adição de duas tabelas extras para expandir o escopo e utilidade do sistema.

---

## 🛠️ Funcionalidades Implementadas

O sistema conta com autenticação segura (login, logout e proteção de rotas com hash de senhas via Werkzeug) e 5 módulos principais 100% integrados ao banco de dados:

1. **Dashboard Dinâmico:** Tela inicial com contadores reais consumindo dados do banco (Tarefas Pendentes, Tarefas Concluídas, Ambientes Ativos e Despesas Pendentes) e listagem rápida das 5 tarefas mais recentes.
2. **CRUD de Funções:** Gerenciamento de níveis de acesso, cargos no sistema e permissões.
3. **CRUD de Usuários:** Cadastro de moradores/participantes da casa com validações de CPF e e-mail únicos.
4. **CRUD de Tarefas (Desafio Concluído):** Atribuição de atividades diárias com prazos, prioridades e status, vinculadas aos usuários responsáveis através de relacionamentos (JOINs).

### 🌟 Tabelas Extras (Escopo Adicional Escolhido)
Para complementar o gerenciamento da casa, implementamos dois novos módulos:

5. **CRUD de Ambientes:** Permite mapear os cômodos da casa (ex: Cozinha, Quintal, Garagem), definindo se são áreas internas ou externas e o seu status de uso.
6. **CRUD de Despesas:** Controle financeiro básico do lar, permitindo lançar contas (ex: Luz, Água, Mercado), atribuir valor, data de vencimento e vincular o usuário responsável pelo pagamento.

---

## 🚀 Como baixar e rodar o projeto

### Pré-requisitos

Certifique-se de ter instalado na sua máquina:
- **Git** (para clonar o repositório)
- **Python 3.10 ou superior** (com a opção "Add Python to PATH" marcada durante a instalação)
- **XAMPP** com o módulo **MySQL** ativo

> O projeto usa o MySQL do XAMPP. Antes de continuar, abra o **XAMPP Control Panel** e clique em **Start** no módulo MySQL.

### Passo 1: Clonar o repositório e acessar a pasta
Abra o terminal (cmd) e execute:
git clone [https://github.com/GTI-Fatec-Jahu/pi-01-26.git](https://github.com/GTI-Fatec-Jahu/pi-01-26.git)
cd pi-01-26

### Passo 2: Criar e ativar o ambiente virtualBashpython -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
(Quando o ambiente estiver ativo, o terminal mostrará (venv) no início da linha).

### Passo 3: Instalar as dependências
Bash
pip install -r requirements.txt
pip install mysql-connector-python

### Passo 4: Configurar a conexão com o bancoAbra o arquivo db.py e verifique as configurações:Python_DB_PARAMS = {
    'host':     'localhost',
    'user':     'root',
    'password': '',          # Deixe vazio se não definiu senha no XAMPP
    'database': 'casa_gestor',
   
    ...
}
Faça o mesmo ajuste de senha na função iniciar_bd() no final do mesmo arquivo, se necessário.

### Passo 5: Rodar a aplicaçãoBashpython app.py
Na primeira execução, o script de inicialização (schema.sql) criará o banco de dados, as tabelas automaticamente e o usuário administrador padrão. O terminal exibirá: Banco e tabelas inicializados com sucesso!
Usuário administrador padrão criado: admin@casagestor.com / admin1234
 * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)
Acesse http://127.0.0.1:5000 no seu navegador para utilizar o sistema.

### 🔐 Credenciais de acesso padrão
E-mail: admin@casagestor.com
Senha: admin1234