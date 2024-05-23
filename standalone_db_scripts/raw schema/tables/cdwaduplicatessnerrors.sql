-- Table: raw.cdwaduplicatessnerrors

-- DROP TABLE IF EXISTS "raw".cdwaduplicatessnerrors;

CREATE TABLE IF NOT EXISTS "raw".cdwaduplicatessnerrors
(
    personid character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cdwaduplicatessnerrors
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".cdwaduplicatessnerrors TO PUBLIC;

GRANT DELETE, UPDATE, INSERT, SELECT ON TABLE "raw".cdwaduplicatessnerrors TO anveeraprasad;

GRANT ALL ON TABLE "raw".cdwaduplicatessnerrors TO cicd_pipeline;

GRANT INSERT ON TABLE "raw".cdwaduplicatessnerrors TO readonly_testing;

GRANT ALL ON TABLE "raw".cdwaduplicatessnerrors TO system_pipeline;