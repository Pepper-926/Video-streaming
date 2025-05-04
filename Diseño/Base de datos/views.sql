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

/*Query muy pesado. Hay que buscar la forma de optimizarlo*/
CREATE OR REPLACE VIEW vwDetalle_video AS
SELECT
	v.id_video,
	v.link,
	v.calificacion,
	v.titulo,
	v.publico,
	v.token_acceso_privado,
	v.descripcion,
	v.fecha_publicado,
	v.miniatura,
	c.nombre_canal,
	u.foto_perfil,
	count(DISTINCT s.seguidor) as seguidores,
	count(DISTINCT CASE WHEN L.tipo_reaccion = TRUE THEN l.id_usuario END) as me_gusta,
	count(DISTINCT CASE WHEN L.tipo_reaccion = FALSE THEN l.id_usuario END) as no_me_gusta,
	count(h.id_usuario) as reproducciones
FROM
	videos v
LEFT JOIN
	historial h on v.id_video = h.id_video
LEFT JOIN
	likes_dislikes_videos l on v.id_video = l.id_video
JOIN
	canales c on v.id_canal = c.id_canal
JOIN
	usuarios u on c.id_usuario = u.id_usuario
LEFT JOIN
	seguidores s on s.id_usuario = u.id_usuario
GROUP BY
	v.id_video,
	v.link,
	v.calificacion,
	v.titulo,
	v.descripcion,
	v.fecha_publicado,
	v.miniatura,
	c.nombre_canal,
	u.foto_perfil