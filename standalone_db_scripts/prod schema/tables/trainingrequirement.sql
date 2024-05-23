-- Table: prod.trainingrequirement

-- DROP TABLE IF EXISTS prod.trainingrequirement;

CREATE TABLE IF NOT EXISTS prod.trainingrequirement
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
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    reasonfortransfer character varying COLLATE pg_catalog."default",
    comments character varying COLLATE pg_catalog."default",
    duedateoverridereason character varying(50) COLLATE pg_catalog."default",
    archived timestamp without time zone,
    learningpath character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT "PK_d010fb4aa9a0bfbeebf6e6ae29d" PRIMARY KEY (trainreq_id),
    CONSTRAINT "UQ_8e35b747b8ca7b31bdd4c71146a" UNIQUE (trainingid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.trainingrequirement
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.trainingrequirement TO anveeraprasad;

GRANT ALL ON TABLE prod.trainingrequirement TO cicd_pipeline;

GRANT SELECT ON TABLE prod.trainingrequirement TO cukaumunna;

GRANT SELECT ON TABLE prod.trainingrequirement TO eblythe;

GRANT SELECT ON TABLE prod.trainingrequirement TO htata;

GRANT SELECT ON TABLE prod.trainingrequirement TO lizawu;

GRANT SELECT ON TABLE prod.trainingrequirement TO readonly_testing;

GRANT ALL ON TABLE prod.trainingrequirement TO system_pipeline;