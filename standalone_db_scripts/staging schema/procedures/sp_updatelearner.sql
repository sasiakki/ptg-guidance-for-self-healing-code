CREATE OR REPLACE PROCEDURE staging.sp_updatelearner()
  LANGUAGE plpgsql
AS
$body$
DECLARE

    delta_timestamp_from TIMESTAMP WITH TIME ZONE;
    delta_timestamp_to TIMESTAMP WITH TIME ZONE;

BEGIN

--GET Learners who have completed O/S but staging.learner orientationandsafetycomplete is null
SELECT MAX(lastprocesseddate) INTO delta_timestamp_from 
    FROM logs.lastprocessed WHERE processname = 'proc-update_staging_learner' AND success = '1';
SELECT CURRENT_TIMESTAMP INTO delta_timestamp_to;


with t1 as (
    SELECT personid, max(completeddate) as completeddate
    FROM prod.trainingrequirement
            WHERE trainingprogramcode = '100' 
            AND completeddate is NOT NULL 
        and lower(status) = 'closed'
                    AND personid in ( select personid from staging.learner 
                                        WHERE orientationandsafetycomplete is NULL 
                        AND recordmodifieddate >  delta_timestamp_from AND recordmodifieddate <= delta_timestamp_to )
    group by personid
)                                   
Update staging.learner l
set orientationandsafetycomplete = t1.completeddate::date,
   recordmodifieddate = delta_timestamp_to
from t1
where l.personid = t1.personid
AND ( l.orientationandsafetycomplete IS NULL OR l.orientationandsafetycomplete <> t1.completeddate::date );
                            
-- grab all required active trainings for staging.learners to get trainingprogram and only those learners who need an update
-- only grab 1 training if multiple are found;
With t2 as (
    SELECT t.*, l.requiredtraining from
        ( select row_number() over ( partition by personid order by trainingprogramcode desc ) program_rank, personid, trainingprogram 
    FROM prod.trainingrequirement
            WHERE isrequired = 'true' and lower(status) = 'active' and trainingprogram is not null
                    AND personid in ( SELECT personid from staging.learner 
                        WHERE recordmodifieddate >  delta_timestamp_from 
                            AND recordmodifieddate <= delta_timestamp_to ) ) AS t
    INNER JOIN staging.learner l on l.personid = t.personid 
                        AND recordmodifieddate >  delta_timestamp_from 
                        AND recordmodifieddate <= delta_timestamp_to
        where program_rank = 1
        and coalesce(l.requiredtraining, 'null') <> coalesce(t.trainingprogram, 'null')
    )   
-- UPDATE training program in staging.learner
Update staging.learner l
set requiredtraining = t2.trainingprogram,
   recordmodifieddate = delta_timestamp_to
from t2
where l.personid = t2.personid
	AND COALESCE ( l.requiredtraining, '') <> COALESCE ( t2.trainingprogram, '') ;


-- queue those with multiple required active trainings for eligibility
with t3 as (
    select distinct l.personid from 
        (select row_number() over ( partition by personid order by trainingprogramcode desc ) program_rank, personid, trainingprogram 
        from prod.trainingrequirement
        where isrequired = 'true' and lower(status) = 'active' and trainingprogram is not null
        and personid in (select personid from staging.learner WHERE recordmodifieddate >  delta_timestamp_from 
                            AND recordmodifieddate <= delta_timestamp_to ) )as t
    inner join staging.learner l on l.personid = t.personid 
        AND  l.recordmodifieddate >  delta_timestamp_from AND l.recordmodifieddate <= delta_timestamp_to
    where program_rank > 1
)

-- UPDATE prod.person to queue for eligibility
update prod.person p
set recordmodifieddate = delta_timestamp_to
from t3
where p.personid = t3.personid;


-- prod.person compliant status is updated in eligibility lambda; sync the updates to staging.learner
with t4 as (
    select p.personid, p.trainingstatus, l.compliant from prod.person p
    inner join staging.learner l on l.personid = p.personid
    where coalesce(p.trainingstatus, 'NULL') <> coalesce(l.compliant, 'NULL') 
        AND  l.recordmodifieddate >  delta_timestamp_from 
    AND l.recordmodifieddate <= delta_timestamp_to
)

-- UPDATE compliant (aka: trainingstatus) in staging.learner
update staging.learner l
set compliant = t4.trainingstatus,
    recordmodifieddate = delta_timestamp_to
from t4
where l.personid = t4.personid
AND COALESCE( l.compliant , '') <> COALESCE ( t4.trainingstatus, '');


INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
VALUES ('proc-update_staging_learner',delta_timestamp_to, '1');

END;
$body$
;
