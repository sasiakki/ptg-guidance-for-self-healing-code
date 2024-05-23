-- PROCEDURE: eligibility.sp_addto_check_person()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_check_person();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_check_person(
	)
LANGUAGE 'plpgsql'
AS $BODY$


DECLARE
	var_max_date timestamptz := NULL::timestamptz; -- lower bound.
	-- NOW() will be upper bound
BEGIN
	select max(recordmodifieddate) into var_max_date from prod.trainingrequirement;

	DROP TABLE IF EXISTS tmp_eligibleperson;

	create temp table tmp_eligibleperson as 
	select s3.personid, s3.workercategory, s3.categorycode, s3.hiredate, s3.exempt,s3.rehiredate,s3.last_termination_date,s3.ahcas_eligible, s3.trackingdate, s3.empstatus, s3.dob
	FROM
	(
	select p.personid, p.workercategory, p.categorycode, p.hiredate, p.exempt,p.rehiredate,p.lasttermdate as last_termination_date,p.ahcas_eligible, p.trackingdate, p.status as empstatus, p.dob
	from prod.person p
	where p.recordmodifieddate::timestamptz > var_max_date
	and p.recordmodifieddate::timestamptz <= NOW()
	
	UNION
	
	select p1.personid, p1.workercategory, p1.categorycode, p1.hiredate, p1.exempt,p1.rehiredate,p1.lasttermdate as last_termination_date, p1.ahcas_eligible, p1.trackingdate, p1.status as empstatus, p1.dob
	from prod.person p1
	JOIN staging.personhistory prc1 ON p1.personid = prc1.personid
	JOIN raw.credential_delta c1 ON c1.credentialnumber::text = prc1.credentialnumber::text
	where c1.recordmodifieddate::timestamptz > var_max_date
	and c1.recordmodifieddate::timestamptz <= NOW()
	and ((p1.credentialnumber is not null and c1.primarycredential = 1) or (p1.credentialnumber is null))
	
	UNION

	select tp.personid, tp.workercategory, tp.categorycode, tp.hiredate, tp.exempt,tp.rehiredate,tp.lasttermdate as last_termination_date, tp.ahcas_eligible, tp.trackingdate, tp.status as empstatus, tp.dob
	from
	(
	select * from prod.person
	where personid in (select distinct personid from prod.trainingrequirement tr
					   where tr.recordmodifieddate::timestamptz > COALESCE((select max(recordmodifieddate) from staging.traininghistory),var_max_date)
					   and tr.recordmodifieddate::timestamptz <= NOW()
					   )
	) tp
	) s3 JOIN (Select distinct personid from (
		select distinct p.status, p.hiredate, p.categorycode, e.isignored, p.personid
		from prod.employmentrelationship e 
		join prod.person p on e.personid = p.personid
		and e.isignored = false
		and UPPER(e.role) = 'CARE'
		and UPPER(e.createdby) <> 'ZENITHLEGACY' 
		group by p.status,p.categorycode,e.isignored,p.personid,p.hiredate
	) as employmentrelationship) s4 on s3.personid = s4.personid;

	insert into eligibility.check_person(personid, workercategory, categorycode, hiredate, exempt, rehiredate, last_termination_date, ahcas_eligible, trackingdate, empstatus, dob)
	select e.personid, e.workercategory, e.categorycode, e.hiredate, e.exempt, e.rehiredate, e.last_termination_date, e.ahcas_eligible, e.trackingdate, e.empstatus, e.dob
	from tmp_eligibleperson e
    inner join prod.person p on p.personid = e.personid 
        and lower(p.status) = 'active';

END;
$BODY$;

