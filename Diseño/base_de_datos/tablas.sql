CREATE TABLE Roles (
    id_rol INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rol VARCHAR(10)  UNIQUE NOT NULL
);

CREATE TABLE Usuarios (
    id_usuario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(16) NOT NULL,
    a_pat VARCHAR(16),
    a_mat VARCHAR(16),
    nacimiento DATE NOT NULL,
    correo VARCHAR(50) UNIQUE NOT NULL,
    contra VARCHAR(64) NOT NULL,
    id_rol INT NOT NULL,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE
);

CREATE TABLE Canales (
    id_canal INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(30) UNIQUE NOT NULL,
    subscriptores INT NOT NULL DEFAULT 0 CHECK (subscriptores >= 0),
    id_usuario INT NOT NULL,
    CONSTRAINT fk_canales_usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Etiquetas (
    id_etiqueta INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    categoria VARCHAR(15) UNIQUE NOT NULL,
    descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE Videos (
    id_video INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    likes INT NOT NULL DEFAULT 0 CHECK (likes >= 0),
    dislikes INT NOT NULL DEFAULT 0 CHECK (dislikes >= 0),
    link VARCHAR(128) NOT NULL,
    calificacion NUMERIC(2,1) CHECK (calificacion >= 0 AND calificacion <= 5),
    titulo VARCHAR(30) NOT NULL,
    descripcion TEXT,  
    revisado BOOLEAN NOT NULL DEFAULT FALSE,
    publico BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_publicado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_canal INT NOT NULL,
    CONSTRAINT fk_videos_canal FOREIGN KEY (id_canal) REFERENCES Canales(id_canal) ON DELETE CASCADE
);

CREATE TABLE Videos_Etiquetas (
    id_video INT NOT NULL,
    id_etiqueta INT NOT NULL,
    PRIMARY KEY (id_video, id_etiqueta),
    CONSTRAINT fk_videos_etiquetas_video FOREIGN KEY (id_video) REFERENCES Videos(id_video) ON DELETE CASCADE,
    CONSTRAINT fk_videos_etiquetas_etiqueta FOREIGN KEY (id_etiqueta) REFERENCES Etiquetas(id_etiqueta) ON DELETE CASCADE
);

CREATE TABLE Comentarios (
    id_comentario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    likes INT NOT NULL DEFAULT 0 CHECK (likes >= 0),
    dislikes INT NOT NULL DEFAULT 0 CHECK (dislikes >= 0),
    texto TEXT NOT NULL,
    revisado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_comentado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_video INT NOT NULL,
    id_usuario INT NOT NULL,
    id_respuesta INT NULL,
    CONSTRAINT fk_comentarios_video FOREIGN KEY (id_video) REFERENCES Videos(id_video) ON DELETE CASCADE,
    CONSTRAINT fk_comentarios_usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_comentarios_respuesta FOREIGN KEY (id_respuesta) REFERENCES Comentarios(id_comentario) ON DELETE CASCADE
);

CREATE TABLE Historial (
    id_usuario INT NOT NULL,
    id_video INT NOT NULL,
    fecha_visto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_video, fecha_visto),
    CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_historial_video FOREIGN KEY (id_video)  REFERENCES Videos(id_video) ON DELETE CASCADE
);
