-- PROCEDURE: eligibility.sp_addto_student_training()

-- DROP PROCEDURE IF EXISTS eligibility.sp_addto_student_training();

CREATE OR REPLACE PROCEDURE eligibility.sp_addto_student_training(
	)
LANGUAGE 'plpgsql'
AS $BODY$




DECLARE
    var_max_date timestamptz := NULL::timestamptz; -- lower bound.
    -- NOW() will be upper bound
BEGIN
    --select max(recordmodifieddate) into var_max_date from prod.trainingrequirement;
    CREATE temp TABLE eligibilitytrainings
(
    personid bigint,
    trainingprogramcode character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    duedate timestamp without time zone,
    trackingdate timestamp without time zone,
    completeddate timestamp without time zone,
    datearchived timestamp without time zone,
    trainingcategory character varying COLLATE pg_catalog."default",
    requiredhours numeric(5,2),
    earnedhours numeric(5,2),
    transferhours numeric(5,2),
    totalhours numeric(5,2),
    duedateextension timestamp without time zone,
    isrequired boolean,
    trainingid character varying COLLATE pg_catalog."default",
    duedateoverridereason character varying COLLATE pg_catalog."default"
);
    insert into eligibilitytrainings
    select distinct * from
    (
    select tr.personid, tr.trainingprogramcode, tr.status, tr.duedate, tr.trackingdate,tr.completeddate,tr.archived,  tr.trainingprogram, tr.requiredhours, tr.earnedhours,tr.transferredhours,
    coalesce(tr.transferredhours,0) + tr.earnedhours  as totalhours ,tr.duedateextension, tr.isrequired, tr.trainingid,tr.duedateoverridereason
    from prod.trainingrequirement tr
    where tr.personid is not null
    and tr.personid in (select distinct personid from eligibility.check_person)) s;
    alter table eligibilitytrainings ALTER isrequired TYPE bool USING isrequired::boolean;
   
   
    INSERT INTO eligibility.student_training("studentId", training_code, status, due_date, tracking_date,completed_date,archived, training_category, required_hours, earned_hours,transfer_hours,total_hours, benefit_continuation_due_date, is_required, train_id,reasoncode)
    select distinct personid, trainingprogramcode, status, duedate, trackingdate,completeddate,datearchived, trainingcategory, requiredhours, earnedhours,transferhours, totalhours,duedateextension, isrequired, trainingid,duedateoverridereason
    from eligibilitytrainings;
    DROP TABLE IF EXISTS eligibilitytrainings;
END
$BODY$;


