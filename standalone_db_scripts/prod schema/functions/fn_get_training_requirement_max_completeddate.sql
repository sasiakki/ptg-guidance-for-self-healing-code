-- FUNCTION: prod.fn_get_training_requirement_max_completeddate(bigint, character varying)

-- DROP FUNCTION IF EXISTS prod.fn_get_training_requirement_max_completeddate(bigint, character varying);

CREATE OR REPLACE FUNCTION prod.fn_get_training_requirement_max_completeddate(
	person_id bigint,
	training_id character varying)
    RETURNS date
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$


DECLARE	
	max_completed_date date:=NULL::DATE;
BEGIN

	IF (training_id is not null)  THEN
        SELECT max(completeddate)::DATE INTO max_completed_date FROM prod.transcript WHERE personid = person_id and trainingid = training_id  GROUP BY trainingid;
    END IF;
    RETURN max_completed_date;
END;
$BODY$;

