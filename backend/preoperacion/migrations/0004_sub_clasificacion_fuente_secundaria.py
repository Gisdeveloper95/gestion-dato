"""
Migración: Agregar sub-clasificaciones para Insumos Fuentes Secundarias
Fecha: 2026-02-10
Descripción: Crea tabla lookup de sub-dominios por entidad, agrega columna
             en detalle_insumo, y agrega clasificación DETERMINANTE AMBIENTAL.
"""

from django.db import migrations


FORWARD_SQL = """
-- 1. Crear tabla lookup de sub-clasificaciones
CREATE TABLE IF NOT EXISTS sub_clasificacion_fuente_secundaria (
    cod_sub_clasificacion SERIAL PRIMARY KEY,
    dominio VARCHAR(50) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    orden INT DEFAULT 0,
    UNIQUE(dominio, nombre)
);

CREATE INDEX IF NOT EXISTS idx_sub_clasif_dominio
ON sub_clasificacion_fuente_secundaria(dominio);

-- 2. Agregar columna nullable en detalle_insumo
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'detalle_insumo' AND column_name = 'cod_sub_clasificacion'
    ) THEN
        ALTER TABLE detalle_insumo
        ADD COLUMN cod_sub_clasificacion INT NULL
        REFERENCES sub_clasificacion_fuente_secundaria(cod_sub_clasificacion);
    END IF;
END $$;

-- 3. Agregar DETERMINANTE AMBIENTAL como clasificación para cada insumo secundario
INSERT INTO clasificacion_insumo (cod_insumo, nombre, observacion)
SELECT i.cod_insumo, 'DETERMINANTE AMBIENTAL', 'Determinantes ambientales para fuentes secundarias'
FROM insumos i
JOIN categorias c ON i.cod_categoria = c.cod_categoria
WHERE c.nom_categoria = 'Insumos Fuentes Secundarias'
  AND NOT EXISTS (
    SELECT 1 FROM clasificacion_insumo ci
    WHERE ci.cod_insumo = i.cod_insumo AND ci.nombre = 'DETERMINANTE AMBIENTAL'
  );

-- 4. Poblar sub-dominios (124 registros, 15 dominios)
INSERT INTO sub_clasificacion_fuente_secundaria (dominio, nombre, orden) VALUES
-- ANT (9)
('ANT', 'Zona de Reserva Campesina', 1),
('ANT', 'Consejo Comunitario Titulado / Comunidad Negra Titulada', 2),
('ANT', 'Resguardo Indígena Legalizado', 3),
('ANT', 'Solicitudes Resguardos Indígenas', 4),
('ANT', 'Resolución Consejos Comunitarios', 5),
('ANT', 'Resguardo Acuerdo', 6),
('ANT', 'Solicitudes Consejos Comunitarios', 7),
('ANT', 'Solicitud Expectativas Ancestrales', 8),
('ANT', 'Solicitudes Resguardos Indígenas Coloniales', 9),
-- ART (1)
('ART', 'Municipios Priorizados PDET', 1),
-- DAPRE (2)
('DAPRE', 'Minas Antipersonal', 1),
('DAPRE', 'Densidad Cultivos de Coca', 2),
-- MADS (6)
('MADS', 'Humedales RAMSAR', 1),
('MADS', 'Humedales', 2),
('MADS', 'Páramos', 3),
('MADS', 'Reserva de la Biosfera', 4),
('MADS', 'Manglares', 5),
('MADS', 'Reserva Forestal Ley 2da', 6),
-- PNN (2)
('PNN', 'RUNAP Registro Único de Áreas Protegidas', 1),
('PNN', 'Parques Nacionales Naturales de Colombia', 2),
-- SICHI (1)
('SICHI', 'Cicatrices Quema Amazonas', 1),
-- URT (3)
('URT', 'Solicitud Inscrita RUPTA', 1),
('URT', 'Solicitud Recibida Demandas RUPTA Individual', 2),
('URT', 'Sentencias URT', 3),
-- ICANH (2)
('ICANH', 'Áreas Arqueológicas Protegidas', 1),
('ICANH', 'Sitios Arqueológicos', 2),
-- ANLA (5)
('ANLA', 'Líneas Licenciadas', 1),
('ANLA', 'Líneas en Evaluación', 2),
('ANLA', 'Áreas Licenciadas', 3),
('ANLA', 'Áreas en Evaluación', 4),
('ANLA', 'Puntos Licenciados', 5),
-- MIN. CULTURA (1)
('MIN. CULTURA', 'Bienes de Interés Cultural Nacional', 1),
-- IGAC (19)
('IGAC', 'Diagnóstico Límite', 1),
('IGAC', 'Límite Líneas', 2),
('IGAC', 'Límites Polígono', 3),
('IGAC', 'Línea Negra', 4),
('IGAC', 'Espacios Sagrados', 5),
('IGAC', 'Caracterización Territorial', 6),
('IGAC', 'Saldo de Conservación (Inventario Saldos)', 7),
('IGAC', 'Saldos Tramitados', 8),
('IGAC', 'Saldos Anulados', 9),
('IGAC', 'Saldos Urbano Terreno', 10),
('IGAC', 'Saldos Urbano Construcción', 11),
('IGAC', 'Saldos Rural Construcción', 12),
('IGAC', 'Saldos Rural Terreno', 13),
('IGAC', 'Avalúos Comerciales', 14),
('IGAC', 'Ofertas', 15),
('IGAC', 'Transacciones', 16),
('IGAC', 'Vigencias Catastrales', 17),
('IGAC', 'Memorias ZHFG', 18),
('IGAC', 'Tablas Terreno y Construcción SNC', 19),
-- DANE (3)
('DANE', 'Clúster Grupos Étnicos', 1),
('DANE', 'MGN Urbano Sección', 2),
('DANE', 'MGN Rural Sección', 3),
-- ANM (12)
('ANM', 'Zona Reservada con Potencial', 1),
('ANM', 'Áreas Estratégicas Mineras', 2),
('ANM', 'Áreas de Inversión del Estado', 3),
('ANM', 'Área Susceptible de Minería', 4),
('ANM', 'Área de Reserva Especial en Trámite', 5),
('ANM', 'Área de Reserva Especial Declarada', 6),
('ANM', 'Zona Minera Étnica', 7),
('ANM', 'Área Indígena Restringida', 8),
('ANM', 'Título Vigente', 9),
('ANM', 'Solicitud Área Reserva Especial PT', 10),
('ANM', 'Solicitud Vigente', 11),
('ANM', 'Subcontrato Vigente', 12),
-- INVIAS (5)
('INVIAS', 'Peajes', 1),
('INVIAS', 'Postes de Referencia', 2),
('INVIAS', 'Predios Priorizados', 3),
('INVIAS', 'Red Vial', 4),
('INVIAS', 'Puentes', 5),
-- DETERMINANTE AMBIENTAL (53)
('DETERMINANTE AMBIENTAL', 'CAR', 1),
('DETERMINANTE AMBIENTAL', 'Licencias Ambientales', 2),
('DETERMINANTE AMBIENTAL', 'Títulos Mineros', 3),
('DETERMINANTE AMBIENTAL', 'Capacidad de Suelos Cuenca', 4),
('DETERMINANTE AMBIENTAL', 'Embalses', 5),
('DETERMINANTE AMBIENTAL', 'Zonificación Humedales', 6),
('DETERMINANTE AMBIENTAL', 'Límites Humedales', 7),
('DETERMINANTE AMBIENTAL', 'Humedales Litigio', 8),
('DETERMINANTE AMBIENTAL', 'Humedales CRC', 9),
('DETERMINANTE AMBIENTAL', 'Humedales 2', 10),
('DETERMINANTE AMBIENTAL', 'Restauración', 11),
('DETERMINANTE AMBIENTAL', 'Reservas Natural Sociedad Civil', 12),
('DETERMINANTE AMBIENTAL', 'Reservas Forestales Protectoras Regionales', 13),
('DETERMINANTE AMBIENTAL', 'AIERH', 14),
('DETERMINANTE AMBIENTAL', 'Cambio Climático', 15),
('DETERMINANTE AMBIENTAL', 'PNN', 16),
('DETERMINANTE AMBIENTAL', 'RFP', 17),
('DETERMINANTE AMBIENTAL', 'Subzh', 18),
('DETERMINANTE AMBIENTAL', 'Límites', 19),
('DETERMINANTE AMBIENTAL', 'Ordenación Forestal', 20),
('DETERMINANTE AMBIENTAL', 'POMCA', 21),
('DETERMINANTE AMBIENTAL', 'POF Bioma', 22),
('DETERMINANTE AMBIENTAL', 'POF Unicauca', 23),
('DETERMINANTE AMBIENTAL', 'Reserva Biosfera', 24),
('DETERMINANTE AMBIENTAL', 'Reservas Ley 2da', 25),
('DETERMINANTE AMBIENTAL', 'Reservas Forestales', 26),
('DETERMINANTE AMBIENTAL', 'Bosque Seco Resolución 1628', 27),
('DETERMINANTE AMBIENTAL', 'SINAP', 28),
('DETERMINANTE AMBIENTAL', 'Acuífero Patía', 29),
('DETERMINANTE AMBIENTAL', 'Acuífero Norte', 30),
('DETERMINANTE AMBIENTAL', 'AICAS', 31),
('DETERMINANTE AMBIENTAL', 'Páramo', 32),
('DETERMINANTE AMBIENTAL', 'Parques Naturales Regionales', 33),
('DETERMINANTE AMBIENTAL', 'Parques Naturales Municipal', 34),
('DETERMINANTE AMBIENTAL', 'Veredas', 35),
('DETERMINANTE AMBIENTAL', 'Áreas Estratégicas', 36),
('DETERMINANTE AMBIENTAL', 'Áreas Protegidas', 37),
('DETERMINANTE AMBIENTAL', 'Documentos PDF', 38),
('DETERMINANTE AMBIENTAL', 'Zonificación Municipio', 39),
('DETERMINANTE AMBIENTAL', 'Determinantes', 40),
('DETERMINANTE AMBIENTAL', 'Resolución 1282', 41),
('DETERMINANTE AMBIENTAL', 'Medio Natural', 42),
('DETERMINANTE AMBIENTAL', 'Medio Transformado', 43),
('DETERMINANTE AMBIENTAL', 'Cambio Climático 2', 44),
('DETERMINANTE AMBIENTAL', 'Gestión del Riesgo', 45),
('DETERMINANTE AMBIENTAL', 'Densidad del Suelo', 46),
('DETERMINANTE AMBIENTAL', 'Zonificación 2', 47),
('DETERMINANTE AMBIENTAL', 'Susceptibilidad', 48),
('DETERMINANTE AMBIENTAL', 'Ronda Hídrica', 49),
('DETERMINANTE AMBIENTAL', 'Humedales y Zonas de Carga', 50),
('DETERMINANTE AMBIENTAL', 'POMCA y Usos', 51),
('DETERMINANTE AMBIENTAL', 'Frontera Agrícola', 52),
('DETERMINANTE AMBIENTAL', 'Riesgos Climáticos', 53)
ON CONFLICT (dominio, nombre) DO NOTHING;
"""

REVERSE_SQL = """
-- Revertir: quitar columna, eliminar datos, eliminar tabla
ALTER TABLE detalle_insumo DROP COLUMN IF EXISTS cod_sub_clasificacion;
DROP TABLE IF EXISTS sub_clasificacion_fuente_secundaria;
DELETE FROM clasificacion_insumo WHERE nombre = 'DETERMINANTE AMBIENTAL';
"""


class Migration(migrations.Migration):

    dependencies = [
        ('preoperacion', '0003_add_preoperacion_indexacion'),
    ]

    operations = [
        migrations.RunSQL(
            sql=FORWARD_SQL,
            reverse_sql=REVERSE_SQL,
        ),
    ]
