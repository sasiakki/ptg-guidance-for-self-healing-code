-- PROCEDURE: eligibility.sp_addto_student_status_set()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_student_status_set();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_student_status_set(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN
	
	INSERT INTO eligibility.student_status_set("studentId", ahcas_eligible, "complianceStatus")
	select distinct personid, ahcas_eligible, trainingstatus
	from prod.person
	where personid in (select distinct personid from eligibility.check_person);
END
$BODY$;


