-- FUNCTION: staging.fn_get_previous_categories(numeric, numeric, numeric, numeric, numeric)

-- DROP FUNCTION IF EXISTS staging.fn_get_previous_categories(numeric, numeric, numeric, numeric, numeric);

CREATE OR REPLACE FUNCTION staging.fn_get_previous_categories(
	var_employeeid numeric,
	var_branchid1 numeric,
	var_branchid3 numeric,
	var_branchid4 numeric,
	var_branchid5 numeric)
    RETURNS TABLE(fnbranchid character varying, prevclassification character varying, prevtccode character varying, prevpriority integer, prevauthend character varying, prevorientationandsafetycomplete date, prevfiledate date, prevempstatus character varying, prevtrackingdate character varying) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

DECLARE
	
	sql varchar;
	
begin
	var_employeeid:= var_employeeid;
	var_branchid1:= var_branchid1;
	--var_branchid2:= var_branchid2;
	var_branchid3:= var_branchid3;
	var_branchid4:= var_branchid4;
	var_branchid5:= var_branchid5;
	sql = '
	SELECT distinct empr.branchid::character varying, empr.workercategory,wcm.tccode,wcm.priority,empr.authend,l.orientationandsafetycomplete, empr.filedate, empr.empstatus, empr.trackingdate FROM prod.employmentrelationship empr
    	LEFT JOIN staging.workercategory wcm on empr.workercategory = wcm.workercategory
		LEFT JOIN staging.learner l on empr.personid = l.PersonID
		WHERE empr.employeeid = '''||var_employeeid||''' and empr.branchid in ('''||var_branchid1||''', '''||var_branchid5||''', '''||var_branchid3||''', '''||var_branchid4||''') and employerid=''103'' and isignored <> true ORDER BY empr.empstatus asc nulls last, empr.authend desc, empr.filedate desc nulls last, empr.trackingdate desc';
	
	RETURN QUERY EXECUTE sql;
	--RETURN QUERY EXECUTE sql;
	--RETURN QUERY EXECUTE format('SELECT distinct empr.branchid, empr.workercategory,wcm.tccode,wcm.priority,empr.authend,l.orientationandsafetycomplete, empr.filedate, empr.empstatus, empr.trackingdate FROM prod.employmentrelationship empr
      --    					 LEFT JOIN staging.workercategory wcm on empr.workercategory = wcm.workercategory
		--					 LEFT JOIN staging.learner l on empr.personid = l.PersonID
          --					 WHERE empr.employeeid = $1 and empr.branchid in ($2, $3, $4, $5) and employerid=103 and isignored <> true ORDER BY empr.empstatus asc nulls last, empr.authend desc, empr.filedate desc nulls last, empr.trackingdate desc') USING p_employeeid, p_branchid1, p_branchid2, p_branchid3, p_branchid4;
								
end;
$BODY$;

