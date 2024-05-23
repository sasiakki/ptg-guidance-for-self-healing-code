-- FUNCTION: staging.fn_getcoursecompletions()

-- DROP FUNCTION IF EXISTS staging.fn_getcoursecompletions();

CREATE OR REPLACE FUNCTION staging.fn_getcoursecompletions(
	)
    RETURNS TABLE(learner_id character varying, first_name character varying, last_name character varying, phone_number character varying, learner_email character varying, attendance character varying, class_id character varying, class_title character varying, date date, duration numeric, when_enrolled date, instructor character varying, sheet_name character varying, recordmodifieddate timestamp without time zone, recordcreateddate timestamp without time zone) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1e+06

AS $BODY$
DECLARE
  source ALIAS FOR $1;
  sql VARCHAR;
BEGIN

	sql = 'select * from raw.ss_course_completion order by recordmodifieddate';

  RETURN QUERY EXECUTE sql;
END;
$BODY$;

