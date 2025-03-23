CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    senha VARCHAR(120) NOT NULL,
    celular VARCHAR(20) NOT NULL,
    tipo_usuario VARCHAR(50) NOT NULL CHECK (tipo_usuario IN ('telespectador', 'palestrante')),
    data_nascimento DATE,
    biografia TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(100),
    linkedin_url VARCHAR(200),
    github_url VARCHAR(200),
    twitter_url VARCHAR(200),
    site VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    vagas INTEGER NOT NULL,
    palestrante_id INTEGER NOT NULL,
    FOREIGN KEY (palestrante_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE certificados (
    id SERIAL PRIMARY KEY,
    nome_telespectador VARCHAR(100) NOT NULL,
    horas INTEGER NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    data_evento DATE NOT NULL,
    hora_evento TIME NOT NULL,
    evento_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE presencas (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

INSERT INTO usuarios (nome, email, senha, celular, tipo_usuario, data_nascimento, biografia, cidade, estado, linkedin_url, github_url, twitter_url, site)
VALUES
    ('João Silva', 'joao.silva@email.com', 'senha123', '(11) 98765-4321', 'palestrante', '1990-05-15', 'Profissional de marketing apaixonado por tecnologia.', 'São Paulo', 'SP', 'https://linkedin.com/in/joaosilva', 'https://github.com/joaosilva', 'https://twitter.com/joaosilva', 'https://joaosilva.com'),
    ('Maria Oliveira', 'maria.oliveira@email.com', 'senha456', '(11) 98765-1234', 'telespectador', '1985-08-20', 'Entusiasta de eventos e tecnologia.', 'Rio de Janeiro', 'RJ', 'https://linkedin.com/in/mariaoliveira', 'https://github.com/mariaoliveira', 'https://twitter.com/mariaoliveira', 'https://mariaoliveira.com'),
    ('Carlos Santos', 'carlos.santos@email.com', 'senha789', '(11) 98765-5678', 'palestrante', '1980-12-10', 'Especialista em desenvolvimento de software.', 'Belo Horizonte', 'MG', 'https://linkedin.com/in/carlossantos', 'https://github.com/carlossantos', 'https://twitter.com/carlossantos', 'https://carlossantos.com');


INSERT INTO eventos (nome, data, hora, vagas, palestrante_id)
VALUES
    ('Introdução ao Marketing Digital', '2023-11-15', '14:00', 50, 1),  
    ('Desenvolvimento Web com Python', '2023-11-20', '10:00', 30, 3),  
    ('Inovação e Tecnologia', '2023-12-01', '18:00', 100, 1);     

INSERT INTO presencas (evento_id, usuario_id)
VALUES
    (1, 2),  -- Maria Oliveira participou do evento 1
    (2, 2),  -- Maria Oliveira participou do evento 2
    (3, 2);  -- Maria Oliveira participou do evento 3

INSERT INTO certificados (nome_telespectador, horas, data, hora, data_evento, hora_evento, evento_id, usuario_id)
VALUES
    ('Maria Oliveira', 2, '2023-11-15', '16:00', '2023-11-15', '14:00', 1, 2),  
    ('Maria Oliveira', 4, '2023-11-20', '12:00', '2023-11-20', '10:00', 2, 2),  
    ('Maria Oliveira', 3, '2023-12-01', '20:00', '2023-12-01', '18:00', 3, 2);  