-- Table: prod.trainingrequirement_arch

-- DROP TABLE IF EXISTS prod.trainingrequirement_arch;

CREATE TABLE IF NOT EXISTS prod.trainingrequirement_arch
(
    requiredhours real,
    earnedhours real,
    transferredhours real,
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    trainingid character varying COLLATE pg_catalog."default",
    trainreq_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    completeddate timestamp without time zone,
    isrequired boolean,
    trackingdate timestamp without time zone,
    duedate timestamp without time zone,
    isoverride boolean DEFAULT false,
    duedateextension timestamp without time zone,
    created timestamp without time zone,
    personid bigint,
    isarchived boolean,
    datearchived timestamp without time zone,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT trainingrequirement_arch_pkey PRIMARY KEY (trainreq_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.trainingrequirement_arch
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.trainingrequirement_arch TO PUBLIC;

GRANT SELECT ON TABLE prod.trainingrequirement_arch TO anveeraprasad;

GRANT ALL ON TABLE prod.trainingrequirement_arch TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE prod.trainingrequirement_arch TO readonly_testing;

GRANT ALL ON TABLE prod.trainingrequirement_arch TO system_pipeline;