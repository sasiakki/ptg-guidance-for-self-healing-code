-- PROCEDURE: staging.sp_updatedohcertduedate()

-- DROP PROCEDURE IF EXISTS staging.sp_updatedohcertduedate();

CREATE OR REPLACE PROCEDURE staging.sp_updatedohcertduedate(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE
	var_max_date timestamptz := NULL::timestamptz; -- lower bound.
	-- NOW() will be upper bound
	
BEGIN
	
	WITH DOHCertDueDate AS
  (
    SELECT p.personid,c.credentialnumber,
    CASE
      WHEN c.credentialtype::text = 'HM' and c.credentialstatus = 'Pending' and upper(c.lepprovisionalcredential) = 'FALSE' AND c.dateofhire IS NOT NULL THEN to_date(c.dateofhire, 'MM/DD/YYYY') + '200 days'::interval
      WHEN c.credentialtype::text = 'HM' and c.credentialstatus = 'Pending' and upper(c.lepprovisionalcredential) = 'FALSE' AND c.dateofhire IS NULL AND p.hiredate IS NOT NULL THEN p.hiredate + '200 days'::interval
      WHEN c.credentialtype::text = 'HM' and c.credentialstatus = 'Pending' and upper(c.lepprovisionalcredential) = 'TRUE' THEN to_date(c.lepprovisionalcredentialexpirationdate, 'MM/DD/YYYY')
    END AS dohcertduedate
    FROM raw.credential_delta c
    JOIN staging.personhistory ps ON c.credentialnumber = ps.credentialnumber
    JOIN prod.person p ON ps.personid = p.personid
  )
  UPDATE raw.credential_delta c
  	SET dohcertduedate = doh.dohcertduedate::date FROM DOHCertDueDate doh
  WHERE c.credentialnumber = doh.credentialnumber
  AND doh.dohcertduedate is not null;
END;
$BODY$;

