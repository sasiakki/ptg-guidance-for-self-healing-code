-- FUNCTION: prod.fn_matchsourcekey(character varying)

-- DROP FUNCTION IF EXISTS prod.fn_matchsourcekey();

CREATE OR REPLACE FUNCTION prod.fn_matchsourcekey(
	var_sourcekey character varying DEFAULT NULL::character varying)
    RETURNS bigint
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

 
DECLARE	
	
	c_personId bigint := NULL::bigint;
	
BEGIN

	var_sourcekey := trim(var_sourcekey);
	
	IF (var_sourcekey is not null) and
		Exists (select * from prod.person p where p.matched_sourcekeys like CONCAT('%',var_sourcekey,'%')::text) THEN
			
        select p.personid into c_personId from prod.person p where p.matched_sourcekeys like CONCAT('%',var_sourcekey,'%')::text;

	ELSE
	
		c_personId := NULL::bigint;
		
	END IF;
	
	return c_personId::bigint;
	
END;
$BODY$;