-- FUNCTION: staging.fn_check_active_erh_update(character varying, integer, character varying, numeric, timestamp without time zone)

-- DROP FUNCTION IF EXISTS staging.fn_check_active_erh_update(character varying, integer, character varying, numeric, timestamp without time zone);

CREATE OR REPLACE FUNCTION staging.fn_check_active_erh_update(
	p_branch character varying DEFAULT NULL::character varying,
	p_lpoverride integer DEFAULT 0,
	p_workercategory character varying DEFAULT NULL::character varying,
	p_employeeid numeric DEFAULT NULL::numeric,
	p_modifieddate timestamp without time zone DEFAULT NULL::timestamp without time zone)
    RETURNS boolean
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

DECLARE
	cur_terminate cursor for select * from staging.fn_check_termination_erh(p_employeeid, p_branch::numeric, p_workercategory);
	cur_active cursor for select * from staging.fn_check_active_erh(p_employeeid, p_branch::numeric, p_workercategory);
	var_id bigint;
	
BEGIN
	
	open cur_terminate;
	LOOP
		fetch cur_terminate into var_id;
		EXIT WHEN NOT FOUND;
		
		UPDATE prod.employmentrelationship
			SET authend = p_modifieddate,
				empstatus = 'Terminated',
				recordmodifieddate = CURRENT_TIMESTAMP
			WHERE relationshipid = var_id;
	
	END LOOP;
	CLOSE cur_terminate;
	
	open cur_active;
	LOOP
		fetch cur_active into var_id;
		EXIT WHEN NOT FOUND;
		
			UPDATE prod.employmentrelationship
			SET authend = p_modifieddate,
				empstatus = 'Terminated',
				recordmodifieddate = CURRENT_TIMESTAMP
			WHERE relationshipid = var_id;			
	
	END LOOP;
	CLOSE cur_active;
	
	IF p_lpoverride = 0 THEN
		
		RETURN TRUE;
			
	ELSIF p_lpoverride = 1 THEN	
		
		RETURN FALSE;
			
	END IF;
	
	RETURN TRUE;
	
END;
$BODY$;

