-- FUNCTION: staging.fn_check_termination_erh(numeric, numeric, character varying)

-- DROP FUNCTION IF EXISTS staging.fn_check_termination_erh(numeric, numeric, character varying);

CREATE OR REPLACE FUNCTION staging.fn_check_termination_erh(
	p_employeeid numeric DEFAULT NULL::numeric,
	p_branchid numeric DEFAULT NULL::numeric,
	p_workercategory character varying DEFAULT NULL::character varying)
    RETURNS TABLE(ids bigint) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

BEGIN
	
	RETURN QUERY EXECUTE format('SELECT relationshipid from prod.employmentrelationship where employeeid= $1 and branchid= $2 and employerid= ''103'' and
        LOWER(empstatus)= LOWER(''Active'') and LOWER(workercategory)<>LOWER($3)') USING p_employeeid, p_branchid, p_workercategory;
	
END;
$BODY$;

