-- PROCEDURE: staging.sp_process_ojt_transfers()

-- DROP PROCEDURE IF EXISTS staging.sp_process_ojt_transfers();

CREATE OR REPLACE PROCEDURE staging.sp_process_ojt_transfers(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE
	var_max_date timestamptz := NULL::timestamptz; -- lower bound.
	-- NOW() will be upper bound
	
BEGIN
-- This will be an place holder
DROP TABLE IF EXISTS staging.applyojtperson cascade;
DROP TABLE IF EXISTS staging.applyojtcatgrization_scenario1 cascade;
DROP TABLE IF EXISTS staging.applyojtcatgrization_scenario3 cascade;
DROP TABLE IF EXISTS staging.applyojtcatgrization_scenario4 cascade;
DROP TABLE IF EXISTS staging.ojt_trainingrequirement_s4 cascade;
DROP TABLE IF EXISTS staging.ojt_trainingtransfers_s4 cascade;
DROP TABLE IF EXISTS staging.ojt_transcript_s4 cascade;
CREATE TABLE staging.applyojtperson as select personid from staging.traininghistory where recordcreateddate > (select max(recordcreateddate) from prod.transcript ) and
completeddate::date >= '2020-03-01'::date AND completeddate::date <= '2021-12-31'::date AND trainingprogramcode::text = '300'::text
order by recordcreateddate;
CREATE OR REPLACE VIEW staging.applyojtcatgrization as
WITH ojteligible AS (
SELECT ptr.personid,
       ptr.appliedhours,
       ptr.pendinghours,
       CASE WHEN ptr.appliedhours = 12::numeric AND ptr.pendinghours = 0::numeric THEN true ELSE false END AS is_all_ojt_hours_exhausted
    FROM prod.ojteligible ptr
), ojtcatgrization AS (
SELECT DISTINCT ojt.personid,
    ojt.appliedhours,
    ojt.pendinghours,
    ojt.is_all_ojt_hours_exhausted,
    lt.requiredhours,
    COALESCE(lt.transferredhours,0) as transferredhours,
    lt.completeddate,
    COALESCE(lt.earnedhours,0) as earnedhours,
    lt.duedate,
    lt.trainingprogram,
    lt.trainingprogramcode,
    lt.trainingid,
    CASE
        WHEN ojt.is_all_ojt_hours_exhausted = true THEN '0'::text
        WHEN ojt.is_all_ojt_hours_exhausted = false AND ((COALESCE(lt.earnedhours,0) + COALESCE(lt.transferredhours,0))>=lt.requiredhours AND (lt.completeddate IS NULL OR lt.completeddate <= lt.duedate)) THEN '1'::text
        WHEN ojt.is_all_ojt_hours_exhausted = false AND ((COALESCE(lt.earnedhours,0) + COALESCE(lt.transferredhours,0)) >= '0'::real AND (COALESCE(lt.earnedhours,0) + COALESCE(lt.transferredhours,0)) < lt.requiredhours) THEN '3'::text
        WHEN ojt.is_all_ojt_hours_exhausted = false AND ((COALESCE(lt.earnedhours,0) + COALESCE(lt.transferredhours,0))>=lt.requiredhours AND (lt.completeddate IS NULL OR lt.completeddate > lt.duedate)) THEN '4'::text
        ELSE NULL::text
    END AS scenario,
    EXTRACT(YEAR FROM lt.duedate)::int as ceyear
FROM ojteligible ojt
    LEFT JOIN prod.trainingrequirement lt ON lt.personid = ojt.personid
    JOIN staging.applyojtperson aojt ON aojt.personid = ojt.personid
WHERE lt.duedate::date >= '2020-03-01'::date AND lt.duedate::date <= '2021-12-31'::date AND lt.trainingprogramcode::text = '300'::text
        )
SELECT ojtcatgrization.personid,
    ojtcatgrization.appliedhours,
    ojtcatgrization.pendinghours,
    ojtcatgrization.is_all_ojt_hours_exhausted,
    ojtcatgrization.requiredhours,
    ojtcatgrization.transferredhours,
    ojtcatgrization.completeddate,
    ojtcatgrization.earnedhours,
    ojtcatgrization.duedate,
    ojtcatgrization.trainingprogram,
    ojtcatgrization.trainingprogramcode,
    ojtcatgrization.scenario,
    ojtcatgrization.trainingid,
    ojtcatgrization.ceyear,
    rank() over (partition by ojtcatgrization.personid,ojtcatgrization.scenario order by ojtcatgrization.ceyear) as priority_ce
FROM ojtcatgrization;
CREATE TABLE staging.applyojtcatgrization_scenario4 as  Select * from staging.applyojtcatgrization where scenario='4' and priority_ce = 1;
CREATE TABLE  staging.ojt_trainingrequirement_s4  as
SELECT ptr.* from prod.trainingrequirement ptr
    join staging.applyojtcatgrization_scenario4 ojts4
    on ptr.personid = ojts4.personid
    and ptr.trainingprogramcode = ojts4.trainingprogramcode
    where ptr.duedate >= ojts4.duedate ;
CREATE TABLE  staging.ojt_trainingtransfers_s4 as select * from prod.trainingtransfers where trainingid in (select trainingid from staging.ojt_trainingrequirement_s4);
CREATE TABLE  staging.ojt_transcript_s4 as select * from prod.transcript where trainingid in (select trainingid from staging.ojt_trainingrequirement_s4);
UPDATE staging.ojt_trainingrequirement_s4 SET earnedhours = 0, transferredhours = 0, completeddate = NULL, status = 'active';
UPDATE staging.ojt_transcript_s4 SET trainingid = NULL;
UPDATE staging.ojt_trainingtransfers_s4 SET trainingid = NULL;
CALL staging.ojt_s4_reshuffle();
UPDATE prod.trainingrequirement
    SET earnedhours=S4.earnedhours
    ,transferredhours=S4.transferredhours
    ,completeddate=S4.completeddate
    ,status=S4.status
    ,recordmodifieddate = CURRENT_TIMESTAMP
    FROM staging.ojt_trainingrequirement_s4 S4
    where trainingrequirement.trainingid= S4.trainingid;
UPDATE prod.transcript
    SET trainingid=t4.trainingid
    ,recordmodifieddate = CURRENT_TIMESTAMP
    FROM staging.ojt_transcript_s4 t4
    where transcript.transcriptid=t4.transcriptid;
UPDATE prod.trainingtransfers
    SET trainingid=tr4.trainingid
    ,recordmodifieddate = CURRENT_TIMESTAMP
    FROM staging.ojt_trainingtransfers_s4 tr4
    where trainingtransfers.transferid=tr4.transferid;
CREATE TABLE staging.applyojtcatgrization_scenario3 as
Select *,
case
    when requiredhours - (earnedhours+transferredhours)  = pendinghours then pendinghours
    when requiredhours - (earnedhours+transferredhours)  < pendinghours then (requiredhours - (earnedhours+transferredhours))
    when requiredhours - (earnedhours+transferredhours)  > pendinghours then pendinghours
END as calcuatedhours
from staging.applyojtcatgrization where scenario='3' and priority_ce = 1;
--applying remaining ojt pending & updating transfer hours
UPDATE prod.trainingrequirement
   SET transferredhours = trainingrequirement.transferredhours + ojts3.calcuatedhours,
       recordmodifieddate = CURRENT_TIMESTAMP
FROM staging.applyojtcatgrization_scenario3 ojts3
WHERE trainingrequirement.trainingid = ojts3.trainingid;
--update trainingstatus
UPDATE prod.trainingrequirement
   SET status = CASE WHEN (trainingrequirement.earnedhours + trainingrequirement.transferredhours)>=trainingrequirement.requiredhours THEN 'closed' ELSE 'active' END ,
       recordmodifieddate = CURRENT_TIMESTAMP
FROM staging.applyojtcatgrization_scenario3 ojts3
WHERE trainingrequirement.trainingid = ojts3.trainingid;
--Updating training completed date
UPDATE prod.trainingrequirement
   SET completeddate = CASE WHEN trainingrequirement.status='closed' then trainingrequirement.duedate ELSE null END,
       recordmodifieddate = CURRENT_TIMESTAMP
FROM staging.applyojtcatgrization_scenario3 ojts3
WHERE trainingrequirement.trainingid = ojts3.trainingid;
--Insert OJT transfer record with pendinghours as credit hours
INSERT INTO prod.trainingtransfers(
	personid, trainingid, trainingprogram, trainingprogramcode, classname, dshscoursecode, transferhours, completeddate, transfersource, reasonfortransfer, courseid)
    select personid,trainingid,trainingprogram,trainingprogramcode,
    'COVID-19 On-The-Job Training Protocols (Unpaid)' as classname,
    case WHEN ceyear::int = 2020 then 'CE2135218-2020'
         WHEN ceyear::int = 2021 then 'CE2135218-2021' END AS dshscoursecode,
    calcuatedhours as transferhours, duedate as completeddate, 'OJT' as transfersource,
    'OJT' as reasonfortransfer,
    case WHEN ceyear::int = 2020 then '3000501OTJEN01'
         WHEN ceyear::int = 2021 then '3000501OTJEN02' END AS courseid
    FROM staging.applyojtcatgrization_scenario3 ojts3 ;
UPDATE prod.ojteligible
    SET appliedhours = ojts3.appliedhours+ojts3.calcuatedhours
        ,pendinghours = ojts3.pendinghours-ojts3.calcuatedhours
        ,recordcreateddate = CURRENT_TIMESTAMP
        ,recordmodifieddate = CURRENT_TIMESTAMP
FROM staging.applyojtcatgrization_scenario3 ojts3
WHERE ojteligible.personid = ojts3.personid;
--Drop table Scenario 1
CREATE TABLE staging.applyojtcatgrization_scenario1 as  Select * from staging.applyojtcatgrization where scenario in ('0','1');
INSERT INTO logs.trainingtransferslogs(personid,error_message)
SELECT DISTINCT ojts1.personid,
                CASE
                    WHEN ojts1.is_all_ojt_hours_exhausted = true THEN 'OJT Eligible  Hours Are Already Applied'::text
                    WHEN ojts1.is_all_ojt_hours_exhausted = false AND  (ojts1.earnedhours + ojts1.transferredhours) >= ojts1.requiredhours AND (ojts1.completeddate IS NULL OR ojts1.completeddate <= ojts1.duedate)
                        THEN 'Training Requirement Closed Before Due Date'::text
                    ELSE NULL::text
                END AS error_message
           FROM staging.applyojtcatgrization_scenario1 ojts1;
DROP TABLE IF EXISTS staging.applyojtcatgrization_scenario1 cascade;
DROP TABLE IF EXISTS staging.applyojtcatgrization_scenario3 cascade;
DROP TABLE IF EXISTS staging.applyojtcatgrization_scenario4 cascade;
DROP TABLE IF EXISTS staging.ojt_trainingrequirement_s4 cascade;
DROP TABLE IF EXISTS staging.ojt_trainingtransfers_s4 cascade;
DROP TABLE IF EXISTS staging.ojt_transcript_s4 cascade;
END;
$BODY$;

