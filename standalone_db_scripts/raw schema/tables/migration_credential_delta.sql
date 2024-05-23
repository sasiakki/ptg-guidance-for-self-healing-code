-- Table: raw.migration_credential_delta

-- DROP TABLE IF EXISTS "raw".migration_credential_delta;

CREATE TABLE IF NOT EXISTS "raw".migration_credential_delta
(
    studentid bigint,
    taxid integer,
    providernumber bigint,
    credentialnumber character varying(50) COLLATE pg_catalog."default",
    providernamedshs character varying(32) COLLATE pg_catalog."default",
    providernamedoh character varying(100) COLLATE pg_catalog."default",
    dateofbirth character varying COLLATE pg_catalog."default",
    limitedenglishproficiencyindicator character varying(5) COLLATE pg_catalog."default",
    firstissuancedate character varying COLLATE pg_catalog."default",
    lastissuancedate character varying COLLATE pg_catalog."default",
    expirationdate character varying COLLATE pg_catalog."default",
    credentialtype character varying(4) COLLATE pg_catalog."default",
    credentialstatus character varying(50) COLLATE pg_catalog."default",
    lepprovisionalcredential character varying(5) COLLATE pg_catalog."default",
    lepprovisionalcredentialissuedate character varying COLLATE pg_catalog."default",
    lepprovisionalcredentialexpirationdate character varying COLLATE pg_catalog."default",
    actiontaken character varying(5) COLLATE pg_catalog."default",
    continuingeducationduedate character varying COLLATE pg_catalog."default",
    longtermcareworkertype character varying(40) COLLATE pg_catalog."default",
    excludedlongtermcareworker character varying(49) COLLATE pg_catalog."default",
    paymentdate character varying COLLATE pg_catalog."default",
    credentiallastdateofcontact character varying COLLATE pg_catalog."default",
    preferredlanguage character varying(37) COLLATE pg_catalog."default",
    credentialstatusdate character varying COLLATE pg_catalog."default",
    nctrainingcompletedate character varying COLLATE pg_catalog."default",
    examscheduleddate character varying COLLATE pg_catalog."default",
    examscheduledsitecode character varying(50) COLLATE pg_catalog."default",
    examscheduledsitename character varying(38) COLLATE pg_catalog."default",
    examtestertype character varying(50) COLLATE pg_catalog."default",
    examemailaddress character varying(50) COLLATE pg_catalog."default",
    examdtrecdschedtestdate character varying COLLATE pg_catalog."default",
    phonenum character varying(20) COLLATE pg_catalog."default",
    hashidkey character varying(255) COLLATE pg_catalog."default",
    primarycredential integer,
    modified timestamp with time zone,
    dateofhire character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    newhashidkey character varying(255) COLLATE pg_catalog."default",
    audit character varying(25) COLLATE pg_catalog."default",
    dohcertduedate date,
    filename character varying COLLATE pg_catalog."default",
    filemodifieddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".migration_credential_delta
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".migration_credential_delta TO PUBLIC;

GRANT ALL ON TABLE "raw".migration_credential_delta TO cicd_pipeline;

GRANT INSERT ON TABLE "raw".migration_credential_delta TO readonly_testing;

GRANT ALL ON TABLE "raw".migration_credential_delta TO system_pipeline;