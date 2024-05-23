-- Table: logs.workercategoryerrors

-- DROP TABLE IF EXISTS logs.workercategoryerrors;

CREATE TABLE IF NOT EXISTS logs.workercategoryerrors
(
    sourcekey character varying COLLATE pg_catalog."default",
    employeeid numeric,
    filesource character varying COLLATE pg_catalog."default",
    filemodifieddate date,
    workercategory character varying COLLATE pg_catalog."default",
    code character varying COLLATE pg_catalog."default",
    error character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.workercategoryerrors
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.workercategoryerrors TO anveeraprasad;

GRANT ALL ON TABLE logs.workercategoryerrors TO cicd_pipeline;

GRANT SELECT ON TABLE logs.workercategoryerrors TO readonly_testing;

GRANT ALL ON TABLE logs.workercategoryerrors TO system_pipeline;