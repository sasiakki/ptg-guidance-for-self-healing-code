-- Table: raw.icd12

-- DROP TABLE IF EXISTS "raw".icd12;

CREATE TABLE IF NOT EXISTS "raw".icd12
(
    employeename character varying(255) COLLATE pg_catalog."default",
    employeeno bigint,
    ssn character varying(30) COLLATE pg_catalog."default",
    employeeaddr1 character varying(255) COLLATE pg_catalog."default",
    employeeaddr2 character varying(255) COLLATE pg_catalog."default",
    employeecity character varying(255) COLLATE pg_catalog."default",
    employeestate character varying(255) COLLATE pg_catalog."default",
    employeezipcode character varying(255) COLLATE pg_catalog."default",
    telephone character varying(30) COLLATE pg_catalog."default",
    safetyandorientation bigint,
    safetyandortrackstartdate character varying(255) COLLATE pg_catalog."default",
    standardservicegroup bigint,
    stservicegrstartdatebasictr character varying(255) COLLATE pg_catalog."default",
    adultchildproservforparents bigint,
    adchildproservforparentsstdate character varying(255) COLLATE pg_catalog."default",
    parentprovforddchildgroup bigint,
    parproforddchildtrackingdate character varying(255) COLLATE pg_catalog."default",
    parprovfornonddchildgroup bigint,
    parprovfornonddchgrtrstdate character varying(255) COLLATE pg_catalog."default",
    limithrsgroup bigint,
    respiteprovider bigint,
    respitetrackstartdate character varying(255) COLLATE pg_catalog."default",
    limitedhrstrackstartdate character varying(255) COLLATE pg_catalog."default",
    authtermflag bigint,
    ru1 character varying COLLATE pg_catalog."default",
    ru2 character varying COLLATE pg_catalog."default",
    ru3 character varying COLLATE pg_catalog."default",
    ru4 character varying(255) COLLATE pg_catalog."default",
    employeeemail character varying(400) COLLATE pg_catalog."default",
    filesource character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filemodifieddate timestamp without time zone,
    encryptedssn character varying(100) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".icd12
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".icd12 TO anveeraprasad;

GRANT ALL ON TABLE "raw".icd12 TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".icd12 TO cukaumunna;

GRANT SELECT ON TABLE "raw".icd12 TO eblythe;

GRANT SELECT ON TABLE "raw".icd12 TO htata;

GRANT SELECT ON TABLE "raw".icd12 TO lizawu;

GRANT SELECT ON TABLE "raw".icd12 TO readonly_testing;

GRANT ALL ON TABLE "raw".icd12 TO system_pipeline;