-- FUNCTION: staging.fn_getpreviouscategories(numeric, numeric)

-- DROP FUNCTION IF EXISTS staging.fn_getpreviouscategories(numeric, numeric);

CREATE OR REPLACE FUNCTION staging.fn_getpreviouscategories(
	p_employeeid numeric DEFAULT NULL::numeric,
	p_branchid numeric DEFAULT NULL::numeric)
    RETURNS TABLE(prevclassification character varying, prevtccode character varying, prevpriority integer, prevauthend character varying, prevorientationandsafetydate date) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

	
declare 
	sql VARCHAR;

begin
	sql ='SELECT distinct empr.workercategory,wcm.tccode,wcm.priority,empr.authend,l.orientationandsafetycomplete FROM staging.employmentrelationshiphistory empr 
          					 LEFT JOIN staging.workercategory wcm on empr.workercategory = wcm.workercategory 
          					 LEFT JOIN staging.learner l on empr.personid = l.PersonID
          					 WHERE cast(empr.employeeid as character varying) =''' || p_employeeid || ''' and empr.branchid = ''' || p_branchid || '''  ';

	--RETURN QUERY EXECUTE sql;
	RETURN QUERY EXECUTE format('SELECT distinct empr.workercategory,wcm.tccode,wcm.priority,empr.authend,l.orientationandsafetycomplete FROM staging.employmentrelationshiphistory empr 
          					 LEFT JOIN staging.workercategory wcm on empr.workercategory = wcm.workercategory 
							 LEFT JOIN staging.learner l on empr.personid = l.PersonID
          					 WHERE empr.employeeid = $1 and empr.branchid = $2') USING p_employeeid, p_branchid;

								
end;
$BODY$;

