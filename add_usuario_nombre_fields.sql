-- Agregar campo usuario_id a la tabla ubicaciones_ubicacion
ALTER TABLE ubicaciones_ubicacion ADD COLUMN usuario_id integer NULL REFERENCES core_user(id) ON DELETE CASCADE;

-- Agregar campo nombre a la tabla ubicaciones_ubicacion
ALTER TABLE ubicaciones_ubicacion ADD COLUMN nombre varchar(100) NULL;

-- Comentario: Después de ejecutar esta migración, es recomendable actualizar los registros existentes
-- para asignarles un usuario_id y un nombre, y luego modificar la tabla para hacer estos campos obligatorios si es necesario. 