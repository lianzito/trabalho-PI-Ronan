-- DROP DATABASE IF EXISTS casa_gestor;

CREATE DATABASE IF NOT EXISTS casa_gestor
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE casa_gestor;

-- DROP TABLE IF EXISTS funcoes;
CREATE TABLE IF NOT EXISTS funcoes(
    id_funcao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    descricao VARCHAR(255),
    gerenciar_funcoes BOOLEAN DEFAULT 0,
    gerenciar_usuarios BOOLEAN DEFAULT 0,
    gerenciar_tarefas BOOLEAN DEFAULT 0,

    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- DROP TABLE IF EXISTS usuarios;
CREATE TABLE IF NOT EXISTS usuarios(
    id_usuario BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    data_nascimento DATE NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    celular VARCHAR(20) NOT NULL,
    cep VARCHAR(9),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2) NOT NULL,
    pais VARCHAR(50) DEFAULT 'Brasil',
    senha VARCHAR(255) NOT NULL,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',

    funcao_id BIGINT UNSIGNED NOT NULL,   
    
    -- logs
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    -- Cria o relacionamento entre tabelas.
    CONSTRAINT fk_usuario_funcao
    FOREIGN KEY (funcao_id) REFERENCES funcoes (id_funcao)
);

-- TABELA DE TAREFAS (Concluindo o CRUD de tarefas)
CREATE TABLE IF NOT EXISTS tarefas(
    id_tarefa BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    prioridade ENUM('Baixa', 'Média', 'Alta') DEFAULT 'Média',
    status ENUM('Pendente', 'Em Andamento', 'Concluído') DEFAULT 'Pendente',
    prazo DATE NULL,
    responsavel_id BIGINT UNSIGNED,
    
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_tarefa_usuario 
    FOREIGN KEY (responsavel_id) REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

-- Tabela 1: Ambientes da casa
CREATE TABLE IF NOT EXISTS ambientes(
    id_ambiente BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('Interno', 'Externo') DEFAULT 'Interno',
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    descricao VARCHAR(255),
    
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela 2: Despesas/Contas da casa
CREATE TABLE IF NOT EXISTS despesas(
    id_despesa BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    vencimento DATE NOT NULL,
    status ENUM('Pendente', 'Pago') DEFAULT 'Pendente',
    usuario_id BIGINT UNSIGNED NOT NULL,
    
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_despesa_usuario 
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id_usuario)
);