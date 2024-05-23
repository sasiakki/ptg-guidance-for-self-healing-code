-- PROCEDURE: eligibility.sp_addto_credential()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_credential();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_credential(
	)
LANGUAGE 'plpgsql'
AS $BODY$


BEGIN
	INSERT INTO eligibility.credential(name, status, "firstIssuance_date", expiration_date, credential_number, "studentId")
	select distinct c.credentialtype, c.credentialstatus, c.firstissuancedate, c.expirationdate, p.credentialnumber, p.personid
	from staging.personhistory p
	join
	raw.credential_delta c on p.credentialnumber = c.credentialnumber
	where p.credentialnumber is not null
	and c.credentialnumber is not null
	and c.primarycredential = 1
	and p.personid in (select distinct personid from eligibility.check_person);
	
END
$BODY$;
