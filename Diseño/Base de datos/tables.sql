CREATE TABLE Roles (
    id_rol INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rol VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE PasswordResetToken (
    id SERIAL PRIMARY KEY,  -- ID único para cada token (autoincremental)
    id_usuario INTEGER NOT NULL,  -- Relación con la tabla de usuarios
    token VARCHAR(255) NOT NULL,  -- Token de recuperación
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  -- Fecha de creación del token
    is_used BOOLEAN DEFAULT FALSE,  -- Indica si el token ha sido utilizado
    CONSTRAINT fk_user FOREIGN KEY(id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE  -- Relación con la tabla auth_user (que es donde se encuentra el modelo User)
);

CREATE TABLE Usuarios (
    id_usuario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(16) NOT NULL,
    a_pat VARCHAR(16),
    a_mat VARCHAR(16),
    nacimiento DATE NOT NULL,
    correo VARCHAR(50) UNIQUE NOT NULL,
    contra VARCHAR(64) NOT NULL,
    foto_perfil VARCHAR(64),
    id_rol INT NOT NULL,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE CASCADE
);

CREATE OR REPLACE TABLE Seguidores (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
    id_usuario INT NOT NULL,
    seguidor INT NOT NULL,
    CONSTRAINT unique_usuario_seguidor UNIQUE (id_usuario, seguidor);
    CONSTRAINT fk_usuario_seguidor FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_seguidor_usuario FOREIGN KEY (seguidor) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Canales (
    id_canal INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_canal VARCHAR(30) UNIQUE NOT NULL,
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
    link VARCHAR(128) NOT NULL,
    calificacion NUMERIC(2,1) CHECK (calificacion >= 0 AND calificacion <= 5),
    titulo VARCHAR(30) NOT NULL,
    descripcion TEXT,
    conversion_completa BOOLEAN NOT NULL DEFAULT FALSE,
    estado BOOLEAN NOT NULL DEFAULT FALSE,
    revisado BOOLEAN NOT NULL DEFAULT FALSE,
    publico BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_publicado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    miniatura VARCHAR(64),
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

CREATE TABLE Likes_Dislikes_Videos (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_video INT NOT NULL,
    tipo_reaccion BOOLEAN NOT NULL,
    fecha_reaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_likes_dislikes_usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_likes_dislikes_video FOREIGN KEY (id_video) REFERENCES Videos(id_video) ON DELETE CASCADE,
    CONSTRAINT unique_usuario_video UNIQUE (id_usuario, id_video);
);

CREATE TABLE Comentarios (
    id_comentario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,  -- Clave primaria individual para Django y el ORM
    id_usuario INT NOT NULL,
    id_video INT NOT NULL,
    fecha_visto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    eliminado BOOLEAN DEFAULT FALSE NOT NULL,

    CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_historial_video FOREIGN KEY (id_video) REFERENCES Videos(id_video) ON DELETE CASCADE,

    CONSTRAINT historial_unique UNIQUE (id_usuario, id_video, fecha_visto) -- Mantenemos la unicidad lógica
);