-- FUNCTION: staging.fn_checktrainingcode(character varying, character varying)

-- DROP FUNCTION IF EXISTS staging.fn_checktrainingcode(character varying, character varying);

CREATE OR REPLACE FUNCTION staging.fn_checktrainingcode(
	t_code character varying,
	c_code character varying)
    RETURNS integer
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
  sql VARCHAR;
BEGIN

	IF (t_code = '203' or t_code = '202') Then
		IF (c_code = '203' or c_code = '300' or c_code = '202') Then
			RETURN 1;
		ELSE
			RETURN 0;
		END IF;
	END IF;
	
	IF (t_code = '300') Then
		IF (c_code = '300' or c_code = '400') Then
			RETURN 1;
		ELSE
			RETURN 0;
		END IF;
	END IF;
	
	IF (t_code = c_code) Then
		RETURN 1;
	ELSE
		RETURN 0;
	END IF;

END;
$BODY$;

