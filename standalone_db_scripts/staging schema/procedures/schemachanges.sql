-- PROCEDURE: staging.schemachanges()

-- DROP PROCEDURE IF EXISTS staging.schemachanges();

CREATE OR REPLACE PROCEDURE staging.schemachanges(
	)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
  
   EXECUTE IMMEDIATE;
   ALTER TABLE IF EXISTS prod.employertrust ADD COLUMN trust character varying;
 
  -- The update sentence goes here
   EXECUTE IMMEDIATE;
   CREATE TABLE IF NOT EXISTS staging.registration
(
id integer NOT NULL,
status character varying COLLATE pg_catalog."default",
isdeleted integer,
sessionblockid bigint,
learnerid bigint,
sessionid bigint,
interpreter boolean,
timecreated timestamp with time zone,
timemodified timestamp with time zone,
recordcreateddate timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
recordmodifieddate timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
archived timestamp with time zone,
CONSTRAINT registration_d_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

  
   EXECUTE IMMEDIATE;
   CREATE TABLE IF NOT EXISTS logs.lastprocessed
(
id integer NOT NULL DEFAULT nextval('logs.lastprocessed_seq'::regclass),
processname character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
lastprocesseddate timestamp without time zone,
success character varying(50) COLLATE pg_catalog."default",
CONSTRAINT lastprocessed_pkey PRIMARY KEY (id)
)
TABLESPACE pg_default;
	EXECUTE IMMEDIATE;
	CREATE TABLE IF NOT EXISTS logs.traineestatuslogs
(
id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
employeeid character varying COLLATE pg_catalog."default" NOT NULL,
personid bigint NOT NULL,
compliancestatus character varying COLLATE pg_catalog."default" NOT NULL,
trainingexempt character varying COLLATE pg_catalog."default",
trainingprogram character varying COLLATE pg_catalog."default" NOT NULL,
trainingstatus character varying COLLATE pg_catalog."default",
classname character varying COLLATE pg_catalog."default",
dshscoursecode character varying COLLATE pg_catalog."default",
credithours numeric,
completeddate integer,
filename character varying COLLATE pg_catalog."default",
isvalid boolean NOT NULL DEFAULT true,
errormessage character varying COLLATE pg_catalog."default",
matchstatus character varying COLLATE pg_catalog."default",
createddate timestamp without time zone DEFAULT now(),
modifieddate timestamp without time zone DEFAULT now()
)

TABLESPACE pg_default;

	EXECUTE IMMEDIATE;
    ALTER TABLE prod.person ADD COLUMN sourcekey character varying;
	
	EXECUTE IMMEDIATE;
	--Adding required columns to Prod.Person table
ALTER TABLE prod.person
ADD COLUMN trainingstatus character varying(30),
ADD COLUMN middlename character varying(255),
ADD COLUMN MailingStreet1 character varying (255),
ADD COLUMN MailingStreet2 character varying (255),
ADD COLUMN MailingCity character varying (255),
ADD COLUMN MailingState character varying (255),
ADD COLUMN MailingZip character varying (20),
ADD COLUMN MailingCountry character varying (30);
	EXECUTE IMMEDIATE;

--Adding required columns to Staging.personhistory table 
ALTER TABLE staging.personhistory
ADD COLUMN trainingstatus character varying(30),
ADD COLUMN middlename character varying(255),
ADD COLUMN MailingStreet1 character varying (255),
ADD COLUMN MailingStreet2 character varying (255),
ADD COLUMN MailingCity character varying (255),
ADD COLUMN MailingState character varying (255),
ADD COLUMN MailingZip character varying (20),
ADD COLUMN MailingCountry character varying (30);

	EXECUTE IMMEDIATE;

--------------------------------------------------------------------------------------------------------

--Adding required columns to prod.employmentrelationship table
ALTER TABLE  prod.employmentrelationship
ADD COLUMN SFNGRecordID character varying(50);

	EXECUTE IMMEDIATE;

--Adding required columns to staging.employmentrelationshiphistory table
ALTER TABLE  staging.employmentrelationshiphistory
ADD COLUMN SFNGRecordID character varying(50);

---------------------------------------------------------------------------------------------------------
	EXECUTE IMMEDIATE;
--Adding required columns to prod.Transcript  table
ALTER TABLE prod."Transcript"
ADD COLUMN DSHSCourseID character varying(50),
ADD COLUMN TrainingSource character varying (50);

--------------------------------------------------------------------------------------------------------

--Adding required columns to prod.Instructor table
	EXECUTE IMMEDIATE;

ALTER TABLE prod.Instructor
ADD COLUMN DSHSInstructorID character varying(50);

END;
$BODY$;

