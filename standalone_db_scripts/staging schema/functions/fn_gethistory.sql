-- FUNCTION: staging.fn_gethistory()

-- DROP FUNCTION staging.fn_gethistory();

CREATE OR REPLACE FUNCTION staging.fn_gethistory(
    )
    RETURNS TABLE(firstname character varying, lastname character varying, middlename character varying, ssn character varying, email1 character varying, email2 character varying, homephone character varying, mobilephone character varying, language character varying, physicaladdress character varying, mailingaddress character varying, status character varying, exempt character varying, type character varying, workercategory character varying, credentialnumber character varying, cdwaid bigint, dshsid bigint, categorycode character varying, iscarinaeligible boolean, personid bigint, dob character varying, hiredate timestamp without time zone, trackingdate date, employeeid character varying, sourcekey character varying, recordmodifieddate timestamp without time zone, recordcreateddate timestamp without time zone, employerid character varying, branchid character varying, authstart date, authend date, empstatus character varying, terminationdate date, isoverride boolean, isignored boolean, e_source character varying, mailingstreet1 character varying, mailingstreet2 character varying, mailingcity character varying, mailingstate character varying, mailingzip character varying, mailingcountry character varying, role character varying, ahcas_eligible boolean, rn bigint) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

DECLARE
  source ALIAS FOR $1;
  sql VARCHAR;

  delta_timestamp_from TIMESTAMP WITH TIME ZONE;
  delta_timestamp_to TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT MAX(l.lastprocesseddate) INTO delta_timestamp_from 
                FROM logs.lastprocessed l WHERE processname = 'proc-personmastering' AND success = '1';
    SELECT CURRENT_TIMESTAMP INTO delta_timestamp_to;
    sql = '
    SELECT final.*
FROM (SELECT l2.*,
             ROW_NUMBER() OVER (PARTITION BY sourcekey ORDER BY recordmodifieddate DESC) AS rn
      FROM (SELECT 
                  REGEXP_REPLACE(s.firstname,''\W+'', '''', ''g'')::CHARACTER VARYING as firstname,
                  REGEXP_REPLACE(s.lastname,''\W+'', '''', ''g'')::CHARACTER VARYING as lastname,
                  REGEXP_REPLACE(s.middlename,''\W+'', '''', ''g'')::CHARACTER VARYING as middlename,
                  TRIM(s.ssn)::CHARACTER VARYING AS ssn,
                  TRIM(s.email1)::CHARACTER VARYING AS email1,
                  TRIM(s.email2)::CHARACTER VARYING AS email2,
                  TRIM(s.homephone)::CHARACTER VARYING AS homephone,
                  TRIM(s.mobilephone)::CHARACTER VARYING AS mobilephone,
                  TRIM(s.language)::CHARACTER VARYING AS language,
                  TRIM(s.physicaladdress)::CHARACTER VARYING AS physicaladdress,
                  TRIM(s.mailingaddress)::CHARACTER VARYING AS mailingaddress,
                  TRIM(s.status)::CHARACTER VARYING AS status,
                  TRIM(s.exempt)::CHARACTER VARYING AS exempt,
                  TRIM(s.type)::CHARACTER VARYING AS type,
                  TRIM(s.workercategory)::CHARACTER VARYING AS workercategory,
                  TRIM(s.credentialnumber)::CHARACTER VARYING AS credentialnumber,
                  TRIM(CAST(s.cdwa_id AS CHARACTER VARYING))::BIGINT AS cdwa_id,
                  TRIM(CAST(s.dshsid AS CHARACTER VARYING))::BIGINT AS dshsid,
                  TRIM(s.categorycode)::CHARACTER VARYING AS categorycode,
                  s.iscarinaeligible,
                  TRIM(CAST(s.personid AS CHARACTER VARYING))::BIGINT AS personid,
                  TRIM(s.dob)::CHARACTER VARYING AS dob,
                  s.hiredate::timestamp without time zone,
                  s.trackingdate::date,
                  TRIM(CAST(s.dshsid AS CHARACTER VARYING))::CHARACTER VARYING AS employeeid,
                  TRIM(s.sourcekey)::CHARACTER VARYING AS sourcekey,
                  s.recordmodifieddate,
                  s.recordcreateddate,
                  TRIM(s.employerid)::CHARACTER VARYING AS employerid,
                  TRIM(s.branchid)::CHARACTER VARYING AS branchid,
                  s.authstart::date,
                  s.authend::date,
                  TRIM(s.empstatus)::CHARACTER VARYING AS empstatus,
                  s.terminationdate::date,
                  s.isoverride,
                  s.isignored,
                  TRIM(s.e_source)::CHARACTER VARYING AS e_source,
                  TRIM(s.mailingstreet1)::CHARACTER VARYING AS mailingstreet1,
                  TRIM(s.mailingstreet2)::CHARACTER VARYING AS mailingstreet2,
                  TRIM(s.mailingcity)::CHARACTER VARYING AS mailingcity,
                  TRIM(s.mailingstate)::CHARACTER VARYING AS mailingstate,
                  TRIM(s.mailingzip)::CHARACTER VARYING AS mailingzip,
                  TRIM(s.mailingcountry)::CHARACTER VARYING AS mailingcountry,
                  TRIM(s.role)::CHARACTER VARYING AS role, 
                  s.ahcas_eligible
            FROM (SELECT firstname,
                         lastname,
                         middlename,
                         ssn,
                         email1,
                         email2,
                         homephone,
                         mobilephone,
                         LANGUAGE,
                         physicaladdress,
                         mailingaddress,
                         '''' as status,
                         '''' as exempt,
                         '''' as TYPE,
                         '''' as workercategory,
                         '''' as credentialnumber,
                         cdwa_id::BIGINT,
                         dshsid,
                         '''' as categorycode,
                         false as iscarinaeligible,
                         personid,
                         dob,
                         ''1900-01-01'' as hiredate,
                         ''1900-01-01'' as trackingdate,
                         sourcekey,
                         recordmodifieddate,
                         recordcreateddate,
                         '''' as employerid,
                        '''' as branchid,
                        ''1900-01-01'' as authstart,
                        ''1900-01-01'' as authend,
                        '''' as empstatus,
                        ''1900-01-01'' as terminationdate,
                        false as isoverride,
                        false as isignored,
                        ahcas_eligible,
                        '''' as e_source,
                         mailingstreet1,
                         mailingstreet2,
                         mailingcity,
                         mailingstate,
                         mailingzip,
                         mailingcountry,
                         '''' as role
                  FROM staging.personhistory ph
                  WHERE ph.recordmodifieddate::TIMESTAMPTZ > '''||delta_timestamp_from||''' 
                  AND   ph.recordmodifieddate::TIMESTAMPTZ <= '''||delta_timestamp_to||'''
                  AND   ph.sourcekey IS NOT NULL
                  
                  ORDER BY ph.recordmodifieddate ) AS s

             -- LEFT JOIN (SELECT *
                 --        FROM staging.employmentrelationshiphistory
                         --WHERE 
                         --recordmodifieddate::TIMESTAMPTZ > ''||var_max_date||''
                         --AND   recordmodifieddate::TIMESTAMPTZ <= NOW()
                     --    ) erh ON s.sourcekey = erh.source
            --WHERE s.sourcekey IS NOT NULL
           -- OR    erh.source IS NOT NULL
            ) l2) final
WHERE rn = 1';
  RETURN QUERY EXECUTE sql;
END;
$BODY$;