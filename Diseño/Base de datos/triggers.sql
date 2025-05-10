CREATE OR REPLACE FUNCTION toggle_like_dislike()
RETURNS TRIGGER AS $$
BEGIN
  -- Buscar si ya existe una reacción igual
  IF EXISTS (
    SELECT 1 FROM likes_dislikes_videos
    WHERE id_usuario = NEW.id_usuario AND id_video = NEW.id_video
  ) THEN
    -- Solo cambiar si el valor es diferente
    IF EXISTS (
      SELECT 1 FROM likes_dislikes_videos
      WHERE id_usuario = NEW.id_usuario AND id_video = NEW.id_video
      AND tipo_reaccion <> NEW.tipo_reaccion
    ) THEN
      UPDATE likes_dislikes_videos
      SET tipo_reaccion = NEW.tipo_reaccion,
          fecha_reaccion = CURRENT_TIMESTAMP
      WHERE id_usuario = NEW.id_usuario AND id_video = NEW.id_video;
    END IF;

    -- Cancelar la inserción
    RETURN NULL;
  ELSE
    -- Permitir inserción si no existe
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;
