-- PROCEDURE: eligibility.sp_addto_course_completion()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_course_completion();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_course_completion(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE
    var_max_date timestamptz := NULL::timestamptz; -- lower bound.
    -- NOW() will be upper bound
BEGIN
    select max(recordmodifieddate) into var_max_date from prod.trainingrequirement;
    insert into "eligibility".course_completion (name, completed_date, personid, "studentId")
    select coursename, completeddate, personid, personid
    from prod.transcript s
    where personid is not null and s.recordmodifieddate::timestamptz > var_max_date
    AND s.recordmodifieddate::timestamptz <= NOW()
    and personid in (select distinct personid from eligibility.check_person);
END
$BODY$;

