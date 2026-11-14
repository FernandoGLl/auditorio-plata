-- ===== VERSIÓN SEGURA =====
CREATE TABLE eventos (
  id_evento        NUMBER PRIMARY KEY,
  nombre           VARCHAR2(100) NOT NULL,
  fecha_evento     DATE,
  aforo            NUMBER NOT NULL CHECK (aforo > 0),
  boletos_emitidos NUMBER DEFAULT 0 NOT NULL,
  CONSTRAINT ck_aforo CHECK (boletos_emitidos <= aforo)
);

CREATE SEQUENCE seq_folio START WITH 1 INCREMENT BY 1 NOCACHE;

CREATE TABLE boletos (
  folio          NUMBER PRIMARY KEY,
  id_evento      NUMBER NOT NULL REFERENCES eventos(id_evento),
  fecha_emision  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
  hash_firma     VARCHAR2(64)
);

CREATE TABLE bitacora_solicitudes (
  id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  hilo_id        VARCHAR2(30),
  hora_envio     TIMESTAMP,
  hora_respuesta TIMESTAMP,
  folio          NUMBER,
  estado         VARCHAR2(10) CHECK (estado IN ('EXITO','RECHAZO','ERROR'))
);

INSERT INTO eventos VALUES (1,'Concierto Navideño',DATE '2026-12-20',20000,0);

-- ===== VERSIÓN INSEGURA (para la demostración) =====
CREATE TABLE eventos_inseguro (
  id_evento NUMBER, aforo NUMBER, boletos_emitidos NUMBER
);
CREATE TABLE boletos_inseguro (
  folio NUMBER, id_evento NUMBER, fecha_emision TIMESTAMP DEFAULT SYSTIMESTAMP
);
INSERT INTO eventos_inseguro VALUES (1, 50, 0);

COMMIT;
EXIT;