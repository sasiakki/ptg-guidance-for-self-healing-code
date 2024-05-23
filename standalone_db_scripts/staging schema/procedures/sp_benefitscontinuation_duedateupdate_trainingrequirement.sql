-- PROCEDURE: staging.sp_benefitscontinuation_duedateupdate_trainingrequirement()

-- DROP PROCEDURE IF EXISTS staging.sp_benefitscontinuation_duedateupdate_trainingrequirement();

CREATE OR REPLACE PROCEDURE staging.sp_benefitscontinuation_duedateupdate_trainingrequirement(
	)
LANGUAGE 'plpgsql'
AS $BODY$


BEGIN 
CREATE TEMP TABLE all_mappings AS 
with active_trainings as (
	select tr.trainingid,tr.personid from prod.trainingrequirement tr where tr.status = 'active' 
	and  tr.trainingprogramcode not in ('100','200','500') 
	-- O&S/Refresher/Advanced Training will never have tracking and due dates so dont apply the benefits continution
),bc_eligible_persons as (
	select sbc.personid,sbc.employerrequested,sbc.duedateoverride,sbc.duedateoverridereason,
	firstname,lastname,email,trainingname,bcapproveddate
	from  staging.benefitscontinuation sbc 
	 where sbc.recordcreateddate > (select coalesce(max(cast(recordcreateddate as date)),current_date-1) from prod.duedateextension)
)select bcep.*,atr.trainingid, 
Row_number() OVER(partition BY bcep.personid) trainingsrank from bc_eligible_persons bcep 
left join active_trainings atr on atr.personid = bcep.personid;

CREATE TEMP TABLE error_personids AS
select personid,employerrequested,duedateoverride,firstname,lastname,email,trainingname,bcapproveddate,duedateoverridereason
,case 
	when trainingid is null then 'No Active Training Requirement' 
	when trainingsrank > 1 then 'Multiple Active Training Requirement' end as errormsg  
from all_mappings where trainingid is null or trainingsrank > 1;

CREATE TEMP TABLE valid_personids as
select trainingid, personid,employerrequested,duedateoverride,firstname,lastname,email,trainingname
,bcapproveddate,duedateoverridereason from all_mappings 
where personid not in (select personid from error_personids);

update   prod.trainingrequirement   tr
set duedateoverridereason=vpid.duedateoverridereason,
recordmodifieddate = CURRENT_TIMESTAMP,
duedateextension = vpid.duedateoverride
from  valid_personids  vpid
where vpid.personid=tr.personid
and vpid.trainingid=tr.trainingid ;

INSERT INTO prod.duedateextension (personid,employerrequested,trainingid,duedateoverride,duedateoverridereason,recordcreateddate,recordmodifieddate,bcapproveddate 
									  )
SELECT 
  tr.personid,
  tr.employerrequested,
  tr.trainingid,
  tr.duedateoverride,
  tr.duedateoverridereason,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
  ,tr.bcapproveddate 
   FROM valid_personids tr;

INSERT INTO
  logs.benefitscontinuation (
    personid,
    employerrequested,
    duedateoverride,
    duedateoverridereason,
	  error_reason,
    bcapproveddate 
  )
SELECT
  tr.personid,
  tr.employerrequested,
  tr.duedateoverride,
  tr.duedateoverridereason,
  tr.errormsg,
  tr.bcapproveddate 
FROM
   error_personids tr;
   
DROP TABLE all_mappings;
DROP TABLE error_personids;
DROP TABLE valid_personids;
   
END;
  
$BODY$;

