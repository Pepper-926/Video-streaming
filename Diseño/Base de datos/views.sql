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