-- Versión segura
DELETE FROM boletos;
DELETE FROM bitacora_solicitudes;
UPDATE eventos SET boletos_emitidos = 0 WHERE id_evento = 1;

-- Versión insegura (se recrea la fila para evitar duplicados)
DELETE FROM boletos_inseguro;
DELETE FROM eventos_inseguro;
INSERT INTO eventos_inseguro VALUES (1, 50, 0);
COMMIT;

-- Reiniciar la secuencia de folios
BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE seq_folio';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
CREATE SEQUENCE seq_folio START WITH 1 INCREMENT BY 1 NOCACHE;

EXIT;