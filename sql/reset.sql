-- Versión segura
DELETE FROM boletos;
DELETE FROM bitacora_solicitudes;
UPDATE eventos SET boletos_emitidos = 0 WHERE id_evento = 1;

-- Versión insegura
DELETE FROM boletos_inseguro;
UPDATE eventos_inseguro SET boletos_emitidos = 0 WHERE id_evento = 1;
COMMIT;

-- Reiniciar la secuencia de folios para que vuelva a empezar en 1
DROP SEQUENCE seq_folio;
CREATE SEQUENCE seq_folio START WITH 1 INCREMENT BY 1 NOCACHE;

EXIT;