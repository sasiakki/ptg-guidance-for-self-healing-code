-- Table: raw.transcriptretractions

-- DROP TABLE IF EXISTS "raw".transcriptretractions;

CREATE TABLE IF NOT EXISTS "raw".transcriptretractions
(
    id bigint NOT NULL DEFAULT nextval('raw.transcriptretractions_id_seq'::regclass),
    transcriptid bigint NOT NULL,
    personid bigint NOT NULL,
    courseid character varying COLLATE pg_catalog."default",
    dshsid character varying COLLATE pg_catalog."default",
    credithours numeric(5,2),
    completeddate date,
    coursename character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    instructor character varying COLLATE pg_catalog."default",
    trainingsource character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    archivedreason character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".transcriptretractions
    OWNER to postgres;

GRANT SELECT ON TABLE "raw".transcriptretractions TO PUBLIC;

GRANT ALL ON TABLE "raw".transcriptretractions TO cicd_pipeline;

GRANT ALL ON TABLE "raw".transcriptretractions TO postgres;

GRANT SELECT, INSERT ON TABLE "raw".transcriptretractions TO readonly_testing;

GRANT ALL ON TABLE "raw".transcriptretractions TO system_pipeline;