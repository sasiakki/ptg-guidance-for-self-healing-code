-- PROCEDURE: staging.sp_agencysourcekeycleanup()

-- DROP PROCEDURE staging.sp_agencysourcekeycleanup();

CREATE OR REPLACE PROCEDURE staging.sp_agencysourcekeycleanup(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE 

delta_timestamp_from TIMESTAMP WITH TIME ZONE;
delta_timestamp_to TIMESTAMP WITH TIME ZONE;

BEGIN

--Get the previous execution timestamp, to deduct the delta

SELECT MAX(lastprocesseddate) INTO delta_timestamp_from 
	FROM logs.lastprocessed WHERE processname = 'proc-clean-agency-sourcekey' AND success = '1';
SELECT CURRENT_TIMESTAMP INTO delta_timestamp_to;

/*
	RAISE NOTICE 'delta_timestamp_from from logs table %', delta_timestamp_from;
	RAISE NOTICE 'delta_timestamp_to from fn_gethistory table %', delta_timestamp_to;

*/

--From the Qualtrics API we are receiving for the same person from same source different dob or SSN. In reality these persons are same and they should have same firstname,lastname,dob and SSN
--In order to avoid this issue, we agree with the BAs to just conisder the latest record during cleanup.This script will identify these invalid sourcekey and take latest one 

--After PerMastering in BusinessLogic

/*
RAISE NOTICE 'delta_timestamp %', delta_timestamp;
RAISE NOTICE 'currenttimestamp %', currenttimestamp;
*/

DROP TABLE IF EXISTS tempcteagency;

CREATE TEMP TABLE tempcteagency  AS
with cte as (select personid, count(distinct(sourcekey)), min(recordcreateddate) as mindate , max(recordcreateddate) as maxdate
from staging.personhistory where sourcekey not like '%DSHS%' and sourcekey not like '%CDWA%' and sourcekey not like '%CRED%'and sourcekey not like '%SFLegacy%' 
and sourcekey is not null 
AND recordmodifieddate > delta_timestamp_from AND recordmodifieddate <= delta_timestamp_to	
group by personid  having count(distinct(sourcekey)) > '1')

,cte1 as ( select personid,sourcekey,ssn,dob,split_part(sourcekey, '-', 2) as src   from staging.personhistory where personid in (select distinct personid from cte )
and sourcekey not like '%DSHS%' and sourcekey not like '%CDWA%' and sourcekey not like '%CRED%'and sourcekey not like '%SFLegacy%' 
and sourcekey is not null
)
,ctefinal as (
select  count(distinct src),personid  from cte1 
group by personid 
having count(distinct src)>1)

,cteupdate as (
select distinct personid,dob,ssn,firstname,lastname,sourcekey,recordmodifieddate,row_number() over(partition by sourcekey,personid order by recordmodifieddate desc) as rn
 from staging.personhistory where personid in (select personid from ctefinal)
and  sourcekey not like '%DSHS%' and sourcekey not like '%CDWA%' and sourcekey not like '%CRED%'and sourcekey not like '%SFLegacy%') 

,cteagency as (
select * ,split_part(sourcekey, '-', 1) as src ,row_number() over (partition by personid,split_part(sourcekey, '-', 1)  order by recordmodifieddate desc )as rnt from cteupdate where rn=1) 
select *   from cteagency ;

with cteagency1 as (select personid ,matched_sourcekeys, UNNEST(STRING_TO_ARRAY(matched_sourcekeys,';',''))as sourcekey from prod.person where personid in (select personid from tempcteagency where rnt>1))

,cteagency2 as (select * ,replace(matched_sourcekeys,concat(sourcekey,';'),' ') as newmatched_sourcekeys from cteagency1 
where  sourcekey not like '%DSHS%' and sourcekey not like '%CDWA%' and sourcekey not like '%CRED%')

UPDATE prod.person p
   SET matched_sourcekeys = c.newmatched_sourcekeys,
   recordmodifieddate = delta_timestamp_to
FROM cteagency2 c
WHERE p.personid = c.personid
AND ( COALESCE (p.matched_sourcekeys, '') <> COALESCE (c.newmatched_sourcekeys,'') );

DELETE
FROM staging.personquarantine
WHERE sourcekey IN (SELECT DISTINCT sourcekey FROM tempcteagency WHERE rnt > 1);

DELETE
FROM prod.employmentrelationship
WHERE source IN (SELECT DISTINCT sourcekey FROM tempcteagency WHERE rnt > 1)
AND   personid IN (SELECT personid
                   FROM tempcteagency i
                   WHERE i.personid = prod.employmentrelationship.personid);

DELETE
FROM staging.employmentrelationshiphistory
WHERE source IN (SELECT DISTINCT sourcekey FROM tempcteagency WHERE rnt > 1)
AND   personid IN (SELECT personid
                   FROM tempcteagency i
                   WHERE i.personid = staging.employmentrelationshiphistory.personid);

UPDATE staging.personhistory p
   SET sourcekey = c.sourcekey,
   recordmodifieddate = delta_timestamp_to
        --,
       --dob = c.dob,
       --ssn = c.ssn
FROM tempcteagency c
WHERE c.personid = p.personid
AND   p.sourcekey LIKE concat('%',c.src,'%')
AND   p.personid IS NOT NULL
AND   rnt = 1
AND	  COALESCE( p.sourcekey,'') <> COALESCE( c.sourcekey,'');

INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
VALUES ('proc-clean-agency-sourcekey',delta_timestamp_to, '1');

END;
$BODY$;
