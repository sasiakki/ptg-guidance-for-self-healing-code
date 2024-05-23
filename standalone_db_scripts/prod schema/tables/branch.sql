-- Table: prod.branch

-- DROP TABLE IF EXISTS prod.branch;

CREATE TABLE IF NOT EXISTS prod.branch
(
    branchid integer,
    branchname character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    branchcode character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    address character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    employerid character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    phone character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.branch
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.branch TO anveeraprasad;

GRANT ALL ON TABLE prod.branch TO cicd_pipeline;

GRANT SELECT ON TABLE prod.branch TO cukaumunna;

GRANT SELECT ON TABLE prod.branch TO eblythe;

GRANT SELECT ON TABLE prod.branch TO htata;

GRANT SELECT ON TABLE prod.branch TO lizawu;

GRANT SELECT ON TABLE prod.branch TO readonly_testing;

GRANT ALL ON TABLE prod.branch TO system_pipeline;