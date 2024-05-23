-- FUNCTION: staging.fn_getemploymentrelationshiphistory()

-- DROP FUNCTION IF EXISTS staging.fn_getemploymentrelationshiphistory();

CREATE OR REPLACE FUNCTION staging.fn_getemploymentrelationshiphistory(
	)
    RETURNS TABLE(personid bigint, employeeid integer, employerid integer, branchid integer, workercategory character varying, categorycode character varying, hiredate timestamp without time zone, authstart timestamp without time zone, authend timestamp without time zone, empstatus character varying, terminationdate timestamp without time zone, trackingdate date, isoverride integer, isignored integer, recordmodifieddate timestamp without time zone, recordcreateddate timestamp without time zone) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
  source ALIAS FOR $1;
  sql VARCHAR;
BEGIN

	sql = 'select personid, employeeid, employerid, branchid, workercategory, categorycode, hiredate, authstart, authend, empstatus, terminationdate, trackingdate, isoverride, isignored, recordmodifieddate, recordcreateddate
	from staging.employmentrelationshiphistory erh 
	where NOW() > erh.recordmodifieddate::timestamptz
    AND NOW() - erh.recordmodifieddate::timestamptz <= interval "24 hours"
	order by erh.recordmodifieddate';

  RETURN QUERY EXECUTE sql;
END;
$BODY$;

