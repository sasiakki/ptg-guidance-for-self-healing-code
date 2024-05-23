-- FUNCTION: staging.fn_getclassification(character varying)

-- DROP FUNCTION IF EXISTS staging.fn_getclassification(character varying);

CREATE OR REPLACE FUNCTION staging.fn_getclassification(
	p_source character varying)
    RETURNS TABLE(workercategory character varying, tccode character varying, workercode character varying, filesource character varying, employeeid character varying, safetyandorientation character varying, authtermflag character varying, priority integer, branch1 character varying, branch2 character varying, branch3 character varying, branch4 character varying, trackingdate date, processeddate timestamp without time zone, modifieddate timestamp without time zone, employerid integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

DECLARE
  source ALIAS FOR $1;
  sql VARCHAR;
BEGIN
  sql = 'SELECT workercategory,tccode,workercode,filesource,employeeid,safetyandorientation,authtermflag,
  priority,branch1,branch2,branch3,branch4,trackingdate,processeddate,modifieddate,employerid
  FROM
  (SELECT ''DSHS'' as actsource,
      wcm.workercategory AS workercategory,
      wcm.tccode AS tccode,
      wcm.workercode AS workercode,
      ''DSHS''::character varying AS filesource,
      CAST(provider.employeeno AS character varying) AS employeeid,
      CAST(provider.safetyandorientation AS character varying),
      CAST(provider.authtermflag AS character varying),
      wcm.priority,
      CAST(provider.ru1 AS character varying) AS branch1,
      CAST(provider.ru2 AS character varying) AS branch2,
      CAST(provider.ru3 AS character varying) AS branch3,
      CAST(provider.ru4 AS character varying) AS branch4,
      CAST(provider.trackingdate AS DATE),
      provider.processeddate,
      provider.modifieddate,
      CAST(etm.employerid AS int) AS employerid
     FROM (SELECT pf.employeeno,
			  pf.filesource,
              pf.safetyandorientation,
              pf.authtermflag,
                  CASE
                      WHEN pf.safetyandorientation = 1 THEN NULLIF(pf.safetyandortrackstartdate,'''')::timestamp without time zone
                      WHEN pf.standardservicegroup= 1 THEN NULLIF(pf.stservicegrstartdatebasictr,'''')::timestamp without time zone
                      WHEN pf.adultchildproservforparents = 1 THEN NULLIF(pf.adchildproservforparentsstdate,'''')::timestamp without time zone
                      WHEN pf.parentprovforddchildgroup = 1 THEN NULLIF(pf.parproforddchildtrackingdate,'''')::timestamp without time zone
                      WHEN pf.parprovfornonddchildgroup = 1 THEN NULLIF(pf.parprovfornonddchgrtrstdate,'''')::timestamp without time zone
                      WHEN pf.limithrsgroup = 1 THEN NULLIF(pf.limitedhrstrackstartdate,'''')::timestamp without time zone
                      WHEN pf.respiteprovider = 1  THEN NULLIF(pf.respitetrackstartdate,'''')::timestamp without time zone
                      WHEN pf.authtermflag = 1  THEN pf.recordcreateddate
                      ELSE NULL::date::timestamp without time zone
                  END AS trackingdate,
              pf.recordcreateddate AS processeddate,
              concat(pf.standardservicegroup, pf.adultchildproservforparents, pf.parentprovforddchildgroup, pf.parprovfornonddchildgroup, pf.limithrsgroup, pf.respiteprovider) AS w_code,
              pf.filemodifieddate AS modifieddate,
              CASE
                WHEN pf.ru1 ~ ''^[0\.]+$'' <> true
                THEN (select distinct branchid from prod.branch where ltrim(branchcode,''0'') = ltrim(pf.ru1,''0''))
                WHEN pf.ru1 ~ ''^[0\.]+$'' = true
                THEN (select distinct branchid from prod.branch where branchcode = ''0000'')
                ELSE NULL
              END as ru1,
              CASE
                WHEN pf.ru2 ~ ''^[0\.]+$'' <> true
                THEN (select distinct branchid from prod.branch  where ltrim(branchcode,''0'') = ltrim(pf.ru2,''0''))
                WHEN pf.ru2 ~ ''^[0\.]+$'' = true
                THEN (select distinct branchid from prod.branch where branchcode = ''0000'')
                ELSE NULL
              END as ru2,
              CASE
                WHEN pf.ru3 ~ ''^[0\.]+$'' <> true
                THEN (select distinct branchid from prod.branch  where ltrim(branchcode,''0'') = ltrim(pf.ru3,''0''))
                WHEN pf.ru3 ~ ''^[0\.]+$'' = true
                THEN (select distinct branchid from prod.branch  where branchcode = ''0000'')
                ELSE NULL
              END as ru3,
              CASE
                WHEN pf.ru4 ~ ''^[0\.]+$'' <> true
                THEN (select distinct branchid from prod.branch  where ltrim(branchcode,''0'') = ltrim(pf.ru4,''0''))
                WHEN pf.ru4 ~ ''^[0\.]+$'' = true
                THEN (select distinct branchid from prod.branch  where branchcode = ''0000'')
                ELSE NULL
              END as ru4
       FROM raw.icd12 pf
       WHERE pf.filemodifieddate = (SELECT max(t2.filemodifieddate) AS max
                     FROM raw.icd12 t2)) provider
       LEFT JOIN staging.workercategory wcm ON provider.w_code = wcm.workercode::text
       LEFT JOIN prod.employertrust etm on etm.sourcename=''DSHS'' and trust = ''TP'') mainquery
	   WHERE upper(actsource) = ''DSHS''  order by processeddate';
	
  RETURN QUERY EXECUTE sql;
END;
$BODY$;

