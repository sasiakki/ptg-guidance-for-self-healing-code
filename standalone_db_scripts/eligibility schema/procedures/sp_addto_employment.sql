-- PROCEDURE: eligibility.sp_addto_employment()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_employment();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_employment(
	)
LANGUAGE 'plpgsql'
AS $BODY$



--DECLARE
--	var_max_date timestamptz := NULL::timestamptz; -- lower bound.
	-- NOW() will be upper bound
	
BEGIN	
	INSERT INTO eligibility.employment(status, hire_date, terminate_date, authentication_date, training_category, ignore_assigned_category, "studentId")
	Select status as empstatus, hiredate::text , terminationdate, authstart, categorycode, isignored, personid::text from (
		select distinct p.status,p.hiredate, null as terminationdate, null as authstart, p.categorycode,e.isignored, e.personid
		from prod.employmentrelationship e 
		join prod.person p on e.personid = p.personid
		and e.isignored = false
		and e.role = 'CARE'
		and e.createdby::text <> 'ZenithLegacy' 
		group by p.status,p.categorycode,e.isignored,e.personid,p.hiredate
	) as employmentrelationship  where hiredate is not null and status is not null and personid in (select distinct personid from eligibility.check_person);
	
END
$BODY$;

