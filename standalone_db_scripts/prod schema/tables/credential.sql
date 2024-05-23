-- Table: prod.credential

-- DROP TABLE IF EXISTS prod.credential;

CREATE TABLE IF NOT EXISTS prod.credential
(
    personid bigint,
    taxid integer,
    providernumber bigint,
    credentialnumber character varying(50) COLLATE pg_catalog."default",
    providernamedshs character varying(100) COLLATE pg_catalog."default",
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
    primarycredential integer DEFAULT 0,
    dateofhire character varying COLLATE pg_catalog."default",
    dohcertduedate date,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.credential
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.credential TO PUBLIC;

GRANT SELECT ON TABLE prod.credential TO anveeraprasad;

GRANT ALL ON TABLE prod.credential TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE prod.credential TO readonly_testing;

GRANT ALL ON TABLE prod.credential TO system_pipeline;