-- Table: prod.person

-- DROP TABLE IF EXISTS prod.person;

CREATE TABLE IF NOT EXISTS prod.person
(
    firstname character varying(255) COLLATE pg_catalog."default",
    lastname character varying(255) COLLATE pg_catalog."default",
    ssn character varying(30) COLLATE pg_catalog."default",
    email1 character varying(255) COLLATE pg_catalog."default",
    email2 character varying(255) COLLATE pg_catalog."default",
    homephone character varying(30) COLLATE pg_catalog."default",
    mobilephone character varying(30) COLLATE pg_catalog."default",
    language character varying(255) COLLATE pg_catalog."default",
    physicaladdress text COLLATE pg_catalog."default",
    mailingaddress text COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    exempt character varying(30) COLLATE pg_catalog."default",
    type character varying(30) COLLATE pg_catalog."default",
    workercategory character varying(30) COLLATE pg_catalog."default",
    categorycode character varying(30) COLLATE pg_catalog."default",
    iscarinaeligible boolean DEFAULT false,
    personid bigint NOT NULL,
    dob character varying COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    trackingdate date,
    ahcas_eligible boolean DEFAULT false,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    trainingstatus character varying(30) COLLATE pg_catalog."default",
    middlename character varying(255) COLLATE pg_catalog."default",
    mailingstreet1 character varying(255) COLLATE pg_catalog."default",
    mailingstreet2 character varying(255) COLLATE pg_catalog."default",
    mailingcity character varying(255) COLLATE pg_catalog."default",
    mailingstate character varying(255) COLLATE pg_catalog."default",
    mailingzip character varying(20) COLLATE pg_catalog."default",
    mailingcountry character varying(30) COLLATE pg_catalog."default",
    dshsid bigint,
    credentialnumber character varying COLLATE pg_catalog."default",
    cdwaid bigint,
    sfcontactid character varying COLLATE pg_catalog."default",
    matched_sourcekeys character varying COLLATE pg_catalog."default",
    lasttermdate date,
    rehiredate date,
    CONSTRAINT person_pkey PRIMARY KEY (personid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.person
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.person TO anveeraprasad;

GRANT ALL ON TABLE prod.person TO cicd_pipeline;

GRANT SELECT ON TABLE prod.person TO cukaumunna;

GRANT SELECT ON TABLE prod.person TO eblythe;

GRANT SELECT ON TABLE prod.person TO htata;

GRANT SELECT ON TABLE prod.person TO lizawu;

GRANT SELECT ON TABLE prod.person TO readonly_testing;

GRANT ALL ON TABLE prod.person TO system_pipeline;
-- Index: ppr_addr_idx

-- DROP INDEX IF EXISTS prod.ppr_addr_idx;

CREATE INDEX IF NOT EXISTS ppr_addr_idx
    ON prod.person USING btree
    (mailingzip COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_dob_idx

-- DROP INDEX IF EXISTS prod.ppr_dob_idx;

CREATE INDEX IF NOT EXISTS ppr_dob_idx
    ON prod.person USING btree
    (dob COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_dshs_idx

-- DROP INDEX IF EXISTS prod.ppr_dshs_idx;

CREATE INDEX IF NOT EXISTS ppr_dshs_idx
    ON prod.person USING btree
    (dshsid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_email1_idx

-- DROP INDEX IF EXISTS prod.ppr_email1_idx;

CREATE INDEX IF NOT EXISTS ppr_email1_idx
    ON prod.person USING btree
    (email1 COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_email2_idx

-- DROP INDEX IF EXISTS prod.ppr_email2_idx;

CREATE INDEX IF NOT EXISTS ppr_email2_idx
    ON prod.person USING btree
    (email2 COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_fnameidx

-- DROP INDEX IF EXISTS prod.ppr_fnameidx;

CREATE INDEX IF NOT EXISTS ppr_fnameidx
    ON prod.person USING btree
    (firstname COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_hph_idx

-- DROP INDEX IF EXISTS prod.ppr_hph_idx;

CREATE INDEX IF NOT EXISTS ppr_hph_idx
    ON prod.person USING btree
    (homephone COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_lname_idx

-- DROP INDEX IF EXISTS prod.ppr_lname_idx;

CREATE INDEX IF NOT EXISTS ppr_lname_idx
    ON prod.person USING btree
    (lastname COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_mph_idx

-- DROP INDEX IF EXISTS prod.ppr_mph_idx;

CREATE INDEX IF NOT EXISTS ppr_mph_idx
    ON prod.person USING btree
    (mobilephone COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_ssn_idx

-- DROP INDEX IF EXISTS prod.ppr_ssn_idx;

CREATE INDEX IF NOT EXISTS ppr_ssn_idx
    ON prod.person USING btree
    (ssn COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ppr_status_idx

-- DROP INDEX IF EXISTS prod.ppr_status_idx;

CREATE INDEX IF NOT EXISTS ppr_status_idx
    ON prod.person USING btree
    (status COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;