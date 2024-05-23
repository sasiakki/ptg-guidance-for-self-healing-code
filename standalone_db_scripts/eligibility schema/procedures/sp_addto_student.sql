-- PROCEDURE: eligibility.sp_addto_student()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_student();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_student(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE
	var_max_date timestamptz := NULL::timestamptz; -- lower bound.
	-- NOW() will be upper bound
	
BEGIN
	--select max(recordmodifieddate) into var_max_date from prod.trainingrequirement;
	
	INSERT INTO eligibility.student(id, first_name, last_name, status, assigned_category, prefer_language, birth_date)
	select distinct personid, firstname, lastname, status, categorycode, language, dob
	from "prod".person p
	where p.personid in (select distinct personid from eligibility.check_person);
END
$BODY$;

