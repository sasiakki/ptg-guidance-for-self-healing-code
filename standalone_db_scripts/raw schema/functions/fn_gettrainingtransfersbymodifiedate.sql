-- FUNCTION: raw.fn_gettrainingtransfersbymodifiedate(boolean)

-- DROP FUNCTION IF EXISTS "raw".fn_gettrainingtransfersbymodifiedate(boolean);

CREATE OR REPLACE FUNCTION "raw".fn_gettrainingtransfersbymodifiedate(
	in_is_valid boolean DEFAULT false)
    RETURNS TABLE(employeeid bigint, personid bigint, trainingprogram character varying, classname character varying, dshscoursecode character varying, credithours numeric, completeddate date, trainingentity character varying, reasonfortransfer character varying, employerstaff character varying, filename character varying, filedate date, createddate date, recordcreateddate timestamp without time zone, recordmodifieddate timestamp without time zone, isvalid boolean, error_message character varying) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

 
BEGIN 
RETURN query
SELECT transfer.employeeid,
       transfer.personid,
       transfer.trainingprogram,
       transfer.classname,
       transfer.dshscoursecode,
       cast(transfer.credithours as numeric) as credithours,
       transfer.completeddate,
       transfer.trainingentity as trainingentity,
       transfer.reasonfortransfer as reasonfortransfer,
       transfer.employerstaff,
       transfer.filename,
	   transfer.filedate,
	   transfer.createddate,
	   transfer.recordcreateddate,
	   transfer.recordmodifieddate,
       transfer.isvalid,
       transfer.error_message 
FROM raw.cdwaoandstransfers transfer
WHERE transfer.isvalid = in_is_valid
--AND  transfer.recordmodifieddate  = ((SELECT MAX(t2.recordmodifieddate) AS MAX FROM raw.cdwaoandstransfers t2))
UNION
SELECT tt.employeeid,
       tt.personid,
       tt.trainingprogram,       
       tt.classname,
       tt.dshscoursecode,
       cast(tt.credithours as numeric) as credithours,
       tt.completeddate,
       tt.trainingentity,
       tt.reasonfortransfer,
       tt.employerstaff,
       tt.filename,
	   tt.filedate,
	   tt.createddate,
	   tt.recordcreateddate,
	   tt.recordmodifieddate,
       tt.isvalid,
       tt.error_message
FROM raw.cdwatrainingtransfers tt
WHERE tt.isvalid = in_is_valid;
--AND  tt.recordmodifieddate  = ((SELECT MAX(t2.recordmodifieddate) AS MAX FROM raw.cdwatrainingtransfers t2));

END;

$BODY$;

