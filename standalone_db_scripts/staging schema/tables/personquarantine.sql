-- Table: staging.personquarantine

-- DROP TABLE IF EXISTS staging.personquarantine;

CREATE TABLE IF NOT EXISTS staging.personquarantine
(
    person_unique_id bigint NOT NULL DEFAULT nextval('staging.quarantineperson_relationshipid_seq'::regclass),
    firstname character varying(255) COLLATE pg_catalog."default",
    lastname character varying(255) COLLATE pg_catalog."default",
    middlename character varying(255) COLLATE pg_catalog."default",
    ssn character varying(30) COLLATE pg_catalog."default",
    email1 character varying(255) COLLATE pg_catalog."default",
    email2 character varying(255) COLLATE pg_catalog."default",
    homephone character varying(255) COLLATE pg_catalog."default",
    mobilephone character varying(30) COLLATE pg_catalog."default",
    language character varying(255) COLLATE pg_catalog."default",
    physicaladdress character varying(255) COLLATE pg_catalog."default",
    mailingaddress character varying(255) COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    exempt character varying(30) COLLATE pg_catalog."default",
    type character varying(255) COLLATE pg_catalog."default",
    workercategory character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    cdwaid bigint,
    dshsid bigint,
    categorycode character varying(10) COLLATE pg_catalog."default",
    iscarinaeligible boolean,
    personid bigint,
    dob character varying COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    trackingdate date,
    ahcas_eligible boolean DEFAULT false,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    sfcontactid character varying COLLATE pg_catalog."default",
    approval_status character varying COLLATE pg_catalog."default" DEFAULT 'pending'::character varying,
    sourcekey character varying COLLATE pg_catalog."default",
    mailingstreet1 character varying COLLATE pg_catalog."default",
    mailingstreet2 character varying COLLATE pg_catalog."default",
    mailingcity character varying COLLATE pg_catalog."default",
    mailingstate character varying COLLATE pg_catalog."default",
    mailingzip character varying COLLATE pg_catalog."default",
    mailingcountry character varying COLLATE pg_catalog."default",
    matched_sourcekeys character varying COLLATE pg_catalog."default",
    studentid bigint,
    CONSTRAINT personquarantine_pkey PRIMARY KEY (person_unique_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.personquarantine
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.personquarantine TO anveeraprasad;

GRANT ALL ON TABLE staging.personquarantine TO cicd_pipeline;

GRANT SELECT ON TABLE staging.personquarantine TO readonly_testing;

GRANT ALL ON TABLE staging.personquarantine TO system_pipeline;
-- Index: spq_addr_idx

-- DROP INDEX IF EXISTS staging.spq_addr_idx;

CREATE INDEX IF NOT EXISTS spq_addr_idx
    ON staging.personquarantine USING btree
    (mailingzip COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_dob_idx

-- DROP INDEX IF EXISTS staging.spq_dob_idx;

CREATE INDEX IF NOT EXISTS spq_dob_idx
    ON staging.personquarantine USING btree
    (dob COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_dshs_idx

-- DROP INDEX IF EXISTS staging.spq_dshs_idx;

CREATE INDEX IF NOT EXISTS spq_dshs_idx
    ON staging.personquarantine USING btree
    (dshsid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_email1_idx

-- DROP INDEX IF EXISTS staging.spq_email1_idx;

CREATE INDEX IF NOT EXISTS spq_email1_idx
    ON staging.personquarantine USING btree
    (email1 COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_email2_idx

-- DROP INDEX IF EXISTS staging.spq_email2_idx;

CREATE INDEX IF NOT EXISTS spq_email2_idx
    ON staging.personquarantine USING btree
    (email2 COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_fnameidx

-- DROP INDEX IF EXISTS staging.spq_fnameidx;

CREATE INDEX IF NOT EXISTS spq_fnameidx
    ON staging.personquarantine USING btree
    (firstname COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_hph_idx

-- DROP INDEX IF EXISTS staging.spq_hph_idx;

CREATE INDEX IF NOT EXISTS spq_hph_idx
    ON staging.personquarantine USING btree
    (homephone COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_lname_idx

-- DROP INDEX IF EXISTS staging.spq_lname_idx;

CREATE INDEX IF NOT EXISTS spq_lname_idx
    ON staging.personquarantine USING btree
    (lastname COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_mph_idx

-- DROP INDEX IF EXISTS staging.spq_mph_idx;

CREATE INDEX IF NOT EXISTS spq_mph_idx
    ON staging.personquarantine USING btree
    (mobilephone COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_ssn_idx

-- DROP INDEX IF EXISTS staging.spq_ssn_idx;

CREATE INDEX IF NOT EXISTS spq_ssn_idx
    ON staging.personquarantine USING btree
    (ssn COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: spq_status_idx

-- DROP INDEX IF EXISTS staging.spq_status_idx;

CREATE INDEX IF NOT EXISTS spq_status_idx
    ON staging.personquarantine USING btree
    (status COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;