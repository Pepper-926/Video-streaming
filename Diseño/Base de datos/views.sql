CREATE OR REPLACE VIEW vw_videos_con_etiquetas AS
SELECT
    v.id_video,
	v.publico,
    e.categoria
FROM
    Videos v
JOIN
    Videos_Etiquetas ve ON v.id_video = ve.id_video
JOIN
    Etiquetas e ON ve.id_etiqueta = e.id_etiqueta

CREATE OR REPLACE VIEW vista_canal_de_video AS
SELECT
    v.id_video,
    v.publico,
    c.nombre_canal AS nombre_canal,
    u.foto_perfil
FROM
    Videos v
JOIN
    Canales c ON v.id_canal = c.id_canal
JOIN
    Usuarios u ON c.id_usuario = u.id_usuario;
