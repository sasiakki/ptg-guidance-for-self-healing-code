-- Table: logs.sftpfilelog

-- DROP TABLE IF EXISTS logs.sftpfilelog;

CREATE TABLE IF NOT EXISTS logs.sftpfilelog
(
    filename character varying COLLATE pg_catalog."default",
    filecategory character varying COLLATE pg_catalog."default",
    numberofrows integer,
    filesize integer,
    processeddate date,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.sftpfilelog
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.sftpfilelog TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.sftpfilelog TO readonly_testing;

GRANT ALL ON TABLE logs.sftpfilelog TO system_pipeline;