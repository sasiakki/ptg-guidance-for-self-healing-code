-- Table: prod.instructor

-- DROP TABLE IF EXISTS prod.instructor;

CREATE TABLE IF NOT EXISTS prod.instructor
(
    instructorid character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    firstname character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    lastname character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dshsinstructorid character varying(50) COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default",
    isactive boolean,
    trainingproviderexternalcode character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.instructor
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.instructor TO anveeraprasad;

GRANT ALL ON TABLE prod.instructor TO cicd_pipeline;

GRANT SELECT ON TABLE prod.instructor TO cukaumunna;

GRANT SELECT ON TABLE prod.instructor TO eblythe;

GRANT SELECT ON TABLE prod.instructor TO htata;

GRANT SELECT ON TABLE prod.instructor TO lizawu;

GRANT SELECT ON TABLE prod.instructor TO readonly_testing;

GRANT ALL ON TABLE prod.instructor TO system_pipeline;