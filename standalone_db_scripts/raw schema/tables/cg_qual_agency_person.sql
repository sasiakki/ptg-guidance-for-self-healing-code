-- Table: raw.cg_qual_agency_person

-- DROP TABLE IF EXISTS "raw".cg_qual_agency_person;

CREATE TABLE IF NOT EXISTS "raw".cg_qual_agency_person
(
    startdate character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    enddate character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    status character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    ipaddress character varying(1000) COLLATE pg_catalog."default",
    progress character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    duration_in_seconds character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    finished character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    recordeddate character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    responseid character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    recipientlastname character varying(1000) COLLATE pg_catalog."default",
    recipientfirstname character varying(1000) COLLATE pg_catalog."default",
    recipientemail character varying(1000) COLLATE pg_catalog."default",
    externalreference character varying(1000) COLLATE pg_catalog."default",
    locationlatitude character varying(1000) COLLATE pg_catalog."default",
    locationlongitude character varying(1000) COLLATE pg_catalog."default",
    distributionchannel character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    userlanguage character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    q_recaptchascore character varying(1000) COLLATE pg_catalog."default",
    person_emp_status character varying(1000) COLLATE pg_catalog."default",
    agency_firstname character varying(1000) COLLATE pg_catalog."default",
    agency_lastname character varying(1000) COLLATE pg_catalog."default",
    agency_email character varying(1000) COLLATE pg_catalog."default",
    agency_phone character varying(1000) COLLATE pg_catalog."default",
    employername character varying(1000) COLLATE pg_catalog."default",
    terminated_person_firstname character varying(1000) COLLATE pg_catalog."default",
    terminated_person_middlename character varying(1000) COLLATE pg_catalog."default",
    terminated_person_lastname character varying(1000) COLLATE pg_catalog."default",
    terminated_person_dob character varying(1000) COLLATE pg_catalog."default",
    terminated_person_ssn character varying(1000) COLLATE pg_catalog."default",
    terminated_person_id character varying(1000) COLLATE pg_catalog."default",
    terminated_person_phone character varying(1000) COLLATE pg_catalog."default",
    terminated_person_email character varying(1000) COLLATE pg_catalog."default",
    terminated_person_street character varying(1000) COLLATE pg_catalog."default",
    terminated_person_city character varying(1000) COLLATE pg_catalog."default",
    terminated_person_state character varying(1000) COLLATE pg_catalog."default",
    terminated_person_zipcode character varying(1000) COLLATE pg_catalog."default",
    terminated_person_employerbranch character varying(1000) COLLATE pg_catalog."default",
    person_termination_date character varying(1000) COLLATE pg_catalog."default",
    newhire_person_firstname character varying(1000) COLLATE pg_catalog."default",
    newhire_person_middlename character varying(1000) COLLATE pg_catalog."default",
    newhire_person_lastname character varying(1000) COLLATE pg_catalog."default",
    newhire_person_dob character varying(1000) COLLATE pg_catalog."default",
    newhire_person_ssn character varying(1000) COLLATE pg_catalog."default",
    newhire_person_phone1 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_phone2 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_phone3 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_email1 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_email2 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_street character varying(1000) COLLATE pg_catalog."default",
    newhire_person_city character varying(1000) COLLATE pg_catalog."default",
    newhire_person_state character varying(1000) COLLATE pg_catalog."default",
    newhire_person_zipcode character varying(1000) COLLATE pg_catalog."default",
    preferredlanguage character varying(1000) COLLATE pg_catalog."default",
    newhire_personemployerbranch character varying(1000) COLLATE pg_catalog."default",
    person_hire_date character varying(1000) COLLATE pg_catalog."default",
    exempt character varying(1000) COLLATE pg_catalog."default",
    person_workercategory character varying(1000) COLLATE pg_catalog."default",
    cg_status character varying(1000) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filename character varying COLLATE pg_catalog."default",
    filemodifieddate timestamp without time zone,
    isdelta boolean NOT NULL DEFAULT false
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cg_qual_agency_person
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".cg_qual_agency_person TO anveeraprasad;

GRANT ALL ON TABLE "raw".cg_qual_agency_person TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".cg_qual_agency_person TO cukaumunna;

GRANT SELECT ON TABLE "raw".cg_qual_agency_person TO eblythe;

GRANT SELECT ON TABLE "raw".cg_qual_agency_person TO htata;

GRANT SELECT ON TABLE "raw".cg_qual_agency_person TO lizawu;

GRANT SELECT ON TABLE "raw".cg_qual_agency_person TO readonly_testing;

GRANT ALL ON TABLE "raw".cg_qual_agency_person TO system_pipeline;