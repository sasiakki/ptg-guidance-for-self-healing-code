-- Table: prod.transcript

-- DROP TABLE IF EXISTS prod.transcript;

CREATE TABLE IF NOT EXISTS prod.transcript
(
    transcriptid bigint NOT NULL DEFAULT nextval('prod.transcript_id_seq'::regclass),
    personid bigint,
    coursename character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    completeddate character varying COLLATE pg_catalog."default",
    credithours numeric(5,2),
    coursetype character varying COLLATE pg_catalog."default",
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    instructorname character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    dshscourseid character varying(50) COLLATE pg_catalog."default",
    trainingsource character varying(50) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    trainingid character varying COLLATE pg_catalog."default",
    learningpath character varying(20) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.transcript
    OWNER to cicd_pipeline;

REVOKE ALL ON TABLE prod.transcript FROM tpawlitschek;

GRANT SELECT ON TABLE prod.transcript TO andiaye;

GRANT SELECT ON TABLE prod.transcript TO anveeraprasad;

GRANT SELECT ON TABLE prod.transcript TO bzeimet;

GRANT ALL ON TABLE prod.transcript TO cicd_pipeline;

GRANT SELECT ON TABLE prod.transcript TO cukaumunna;

GRANT SELECT ON TABLE prod.transcript TO eblythe;

GRANT SELECT ON TABLE prod.transcript TO htata;

GRANT SELECT ON TABLE prod.transcript TO jsharief;

GRANT SELECT ON TABLE prod.transcript TO kboyina;

GRANT SELECT ON TABLE prod.transcript TO lizawu;

GRANT SELECT ON TABLE prod.transcript TO readonly_testing;

GRANT ALL ON TABLE prod.transcript TO system_pipeline;

GRANT SELECT ON TABLE prod.transcript TO tjaggi;

GRANT SELECT ON TABLE prod.transcript TO tpawlitschek;
-- Index: ptr_personid_idx

-- DROP INDEX IF EXISTS prod.ptr_personid_idx;

CREATE INDEX IF NOT EXISTS ptr_personid_idx
    ON prod.transcript USING btree
    (personid ASC NULLS LAST)
    TABLESPACE pg_default;