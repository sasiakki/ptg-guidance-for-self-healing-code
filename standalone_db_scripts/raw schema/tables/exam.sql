-- Table: raw.exam

-- DROP TABLE IF EXISTS "raw".exam;

CREATE TABLE IF NOT EXISTS "raw".exam
(
    studentid character varying COLLATE pg_catalog."default",
    taxid character varying COLLATE pg_catalog."default",
    credentialnumber character varying COLLATE pg_catalog."default",
    examdate character varying COLLATE pg_catalog."default",
    examstatus character varying COLLATE pg_catalog."default",
    examtitlefromprometrics character varying COLLATE pg_catalog."default",
    testlanguage character varying COLLATE pg_catalog."default",
    testsite character varying COLLATE pg_catalog."default",
    sitename character varying COLLATE pg_catalog."default",
    rolesandresponsibilitiesofthehomecareaide character varying COLLATE pg_catalog."default",
    supportingphysicalandpsychosocialwellbeing character varying COLLATE pg_catalog."default",
    promotingsafety character varying COLLATE pg_catalog."default",
    handwashingskillresult character varying COLLATE pg_catalog."default",
    randomskill1result character varying COLLATE pg_catalog."default",
    randomskill2result character varying COLLATE pg_catalog."default",
    randomskill3result character varying COLLATE pg_catalog."default",
    commoncarepracticesskillresult character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filemodifieddate timestamp without time zone,
    filename character varying COLLATE pg_catalog."default",
    isdelta boolean
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".exam
    OWNER to cicd_pipeline;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".exam TO anveeraprasad;

GRANT ALL ON TABLE "raw".exam TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".exam TO cukaumunna;

GRANT SELECT ON TABLE "raw".exam TO lizawu;

GRANT SELECT ON TABLE "raw".exam TO readonly_testing;

GRANT ALL ON TABLE "raw".exam TO system_pipeline;