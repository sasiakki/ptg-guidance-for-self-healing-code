-- FUNCTION: staging.fn_getquarantinehistory()

-- DROP FUNCTION IF EXISTS staging.fn_getquarantinehistory();

CREATE OR REPLACE FUNCTION staging.fn_getquarantinehistory(
	)
    RETURNS TABLE(relationshipid integer, employeeid bigint, workercategory character varying, categorycode character varying, esource character varying, branchid bigint, employerid bigint, hiredate timestamp without time zone, authstart date, authend date, terminationdate date, empstatus character varying, trackingdate date, isignored integer, isoverride integer, person_unique_id bigint, firstname character varying, lastname character varying, middlename character varying, ssn character varying, email1 character varying, email2 character varying, homephone character varying, mobilephone character varying, language character varying, physicaladdress character varying, mailingaddress character varying, status character varying, exempt character varying, type character varying, credentialnumber character varying, cdwaid bigint, dshsid bigint, iscarinaeligible boolean, dob character varying, ahcas_eligible boolean, recordmodifieddate timestamp without time zone, recordcreateddate timestamp without time zone, sfcontactid character varying, approval_status character varying, sourcekey character varying, mailingstreet1 character varying, mailingstreet2 character varying, mailingcity character varying, mailingstate character varying, mailingzip character varying, mailingcountry character varying, role character varying) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1e+06

AS $BODY$

DECLARE
  source ALIAS FOR $1;
  sql VARCHAR;
BEGIN
	sql = 'SELECT erq.relationshipid, erq.employeeid, coalesce(erq.workercategory,s.workercategory), coalesce(s.categorycode,erq.categorycode), erq.source as esource, erq.branchid,
	erq.employerid, coalesce(erq.hiredate,s.hiredate), erq.authstart, erq.authend, erq.terminationdate, erq.empstatus,
	coalesce(s.trackingdate,erq.trackingdate::date), erq.isignored, erq.isoverride,
	s.person_unique_id, s.firstname, s.lastname, s.middlename, s.ssn, s.email1, s.email2, s.homephone, s.mobilephone, s.language, s.physicaladdress, s.mailingaddress, s.status, s.exempt, s.type,
	s.credentialnumber, s.cdwaid, s.dshsid, s.iscarinaeligible, s.dob, s.ahcas_eligible, s.recordmodifieddate, s.recordcreateddate, s.sfcontactid, s.approval_status, s.sourcekey,
	s.mailingstreet1, s.mailingstreet2, s.mailingcity, s.mailingstate, s.mailingzip, s.mailingcountry, erq.role
	FROM
	(SELECT pq.person_unique_id, pq.firstname, pq.lastname, pq.middlename, pq.ssn, pq.email1, pq.email2, pq.homephone, pq.mobilephone, pq.language, pq.physicaladdress, pq.mailingaddress, pq.status, pq.exempt, pq.type, pq.workercategory, pq.credentialnumber, pq.cdwaid, pq.dshsid, pq.categorycode, pq.iscarinaeligible, pq.personid, pq.dob, pq.hiredate, pq.trackingdate, pq.ahcas_eligible, pq.recordmodifieddate, pq.recordcreateddate, pq.sfcontactid, pq.approval_status, pq.sourcekey, pq.dshsid as employeeid, pq.mailingstreet1, pq.mailingstreet2, pq.mailingcity, pq.mailingstate, pq.mailingzip, pq.mailingcountry
	 FROM staging.personquarantine pq
	 where pq.approval_status in (''approved'') ) s
left JOIN staging.employmentrelationshipquarantine erq
ON s.sourcekey = erq.source
where s.sourcekey is not null
order by s.recordmodifieddate';
  RETURN QUERY EXECUTE sql;
END;
$BODY$;

