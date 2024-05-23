-- View: outbound.cdwa_trainingstatus

-- DROP VIEW outbound.cdwa_trainingstatus;

CREATE OR REPLACE VIEW outbound.cdwa_trainingstatus
 AS
 WITH ctestartdate AS (
         SELECT
                CASE
                    WHEN max(traineestatuslogs.recordcreateddate) IS NULL THEN ( SELECT min(transcript.completeddate::text)::date AS min
                       FROM prod.transcript)
                    ELSE max(traineestatuslogs.recordcreateddate)::date
                END AS maxprocessdate
           FROM logs.traineestatuslogs
        ), ctetrainingids AS (
         SELECT ltr.trainingid
           FROM prod.trainingrequirement ltr
          WHERE ltr.completeddate >= (( SELECT ctestartdate.maxprocessdate
                   FROM ctestartdate)) AND ltr.completeddate <= CURRENT_DATE OR
                CASE
                    WHEN lower(ltr.trainingprogram::text) = 'continuing education'::text AND lower(ltr.status::text) = 'active'::text AND ltr.duedateextension IS NULL AND ltr.duedate::date >= '2020-03-01'::date AND ltr.duedate::date <= '2022-12-31'::date THEN '2022-12-31 00:00:00'::timestamp without time zone
                    WHEN lower(ltr.trainingprogram::text) = 'continuing education'::text AND lower(ltr.status::text) = 'active'::text AND ltr.duedateextension IS NOT NULL THEN ltr.duedateextension::date::timestamp without time zone
                    WHEN lower(ltr.trainingprogram::text) ~~ '%basic%training%'::text AND lower(ltr.status::text) = 'active'::text AND ltr.duedateextension IS NULL AND ltr.trackingdate::date >= '2019-08-17'::date AND ltr.trackingdate::date <= '2020-09-30'::date THEN '2022-10-31 00:00:00'::timestamp without time zone
                    WHEN lower(ltr.trainingprogram::text) ~~ '%basic%training%'::text AND lower(ltr.status::text) = 'active'::text AND ltr.duedateextension IS NULL AND ltr.trackingdate::date >= '2020-10-01'::date AND ltr.trackingdate::date <= '2021-04-30'::date THEN '2023-01-31 00:00:00'::timestamp without time zone
                    WHEN lower(ltr.trainingprogram::text) ~~ '%basic%training%'::text AND lower(ltr.status::text) = 'active'::text AND ltr.duedateextension IS NULL AND ltr.trackingdate::date >= '2021-05-01'::date AND ltr.trackingdate::date <= '2022-03-31'::date THEN '2023-04-30 00:00:00'::timestamp without time zone
                    WHEN lower(ltr.trainingprogram::text) ~~ '%basic%training%'::text AND lower(ltr.status::text) = 'active'::text AND ltr.duedateextension IS NULL AND ltr.trackingdate::date >= '2022-04-01'::date AND ltr.trackingdate::date <= '2022-09-30'::date THEN '2023-08-31 00:00:00'::timestamp without time zone
                    ELSE COALESCE(ltr.duedateextension, ltr.duedate)
                END >= (( SELECT ctestartdate.maxprocessdate
                   FROM ctestartdate)) AND ltr.completeddate IS NULL
        UNION
         SELECT t.trainingid
           FROM prod.transcript t
          WHERE t.recordmodifieddate::date >= (( SELECT ctestartdate.maxprocessdate
                   FROM ctestartdate)) AND t.recordmodifieddate::date <= CURRENT_DATE AND t.trainingid IS NOT NULL
        ), cte AS (
         SELECT tr.personid,
                CASE
                    WHEN COALESCE(tr.duedateextension, tr.duedate) >= CURRENT_DATE OR COALESCE(tr.duedateextension, tr.duedate) IS NULL THEN 'Compliant'::text
                    WHEN lower(tr.status::text) = 'active'::text AND COALESCE(tr.duedateextension, tr.duedate) < CURRENT_DATE THEN 'Non-Compliant'::text
                    ELSE 'Compliant'::text
                END AS compliance_status,
            person.exempt AS training_exempt,
            person.cdwaid,
                CASE
                    WHEN tr.trainingprogram::text = 'Basic Training 70'::text THEN 'Basic Training 70 Hours'::character varying
                    WHEN tr.trainingprogram::text = 'Basic Training 30'::text THEN 'Basic Training 30 Hours'::character varying
                    WHEN tr.trainingprogram::text = 'Basic Training 9'::text THEN 'Basic Training 9 Hours'::character varying
                    WHEN tr.trainingprogram::text = 'Basic Training 7'::text THEN 'Basic Training 7 Hours'::character varying
                    WHEN tr.trainingprogram::text = 'Orientation and Safety'::text THEN 'Orientation & Safety'::character varying
                    WHEN tr.trainingprogram::text = 'Advanced Training'::text THEN 'AHCAS (Advanced Training)'::character varying
                    ELSE tr.trainingprogram
                END AS trainingprogram,
                CASE
                    WHEN tr.trainingprogramcode::text = '500'::text THEN 'Enrolled'::text
                    WHEN tr.earnedhours = tr.requiredhours::double precision OR tr.completeddate IS NOT NULL THEN 'Completed'::text
                    WHEN COALESCE(tr.duedateextension, tr.duedate) < CURRENT_DATE AND COALESCE(tr.earnedhours, 0::real) < tr.requiredhours::double precision THEN 'Past Due'::text
                    WHEN COALESCE(tr.duedateextension, tr.duedate) > CURRENT_DATE AND COALESCE(tr.earnedhours, 0::real) >= 0::double precision THEN 'In Progress'::text
                    ELSE NULL::text
                END AS trainingprogram_status,
            trn.coursename AS classname,
            trn.dshscourseid,
            person.dshsid,
            trn.credithours,
            to_char(to_date(trn.completeddate::text, 'YYYY-MM-DD'::text)::timestamp with time zone, 'YYYYMMDD'::text) AS completeddate
           FROM prod.trainingrequirement tr
             JOIN ctetrainingids ctetrng ON ctetrng.trainingid::text = tr.trainingid::text
             JOIN prod.person person ON tr.personid = person.personid
             LEFT JOIN prod.transcript trn ON tr.personid = trn.personid AND tr.trainingid::text = trn.trainingid::text AND (trn.recordmodifieddate::date >= (( SELECT ctestartdate.maxprocessdate
                   FROM ctestartdate)) AND trn.recordmodifieddate::date <= CURRENT_DATE OR trn.completeddate::date >= (( SELECT ctestartdate.maxprocessdate
                   FROM ctestartdate)) AND trn.completeddate::date <= CURRENT_DATE)
          WHERE tr.trainingprogramcode::text !~~ '200'::text AND NOT (EXISTS ( SELECT 1
                   FROM prod.trainingrequirement l
                  WHERE tr.trainingid::text = l.trainingid::text AND lower(l.status::text) = 'closed'::text AND l.completeddate IS NULL))
        )
 SELECT tp.employeeid AS "Employee ID",
    tp.personid AS "Person ID",
    tp.compliance_status AS "Compliance Status",
    tp.training_exempt AS "Training Exempt",
    tp.trainingprogram AS "Training Program",
    tp.trainingprogram_status AS "Training Program Status",
    tp.classname AS "Class Name",
    tp.dshscourseid AS "DSHS Course Code",
    tp.credithours AS "Credit Hours",
    tp.completeddate AS "Completed Date"
   FROM ( SELECT a.dshsid AS employeeid,
            a.cdwaid AS personid,
            a.compliance_status,
            a.training_exempt,
            a.trainingprogram,
            a.trainingprogram_status,
            a.classname,
            a.dshscourseid,
            a.credithours,
            a.completeddate
           FROM cte a) tp
  WHERE tp.trainingprogram_status IS NOT NULL AND tp.personid IS NOT NULL AND ((tp.trainingprogram_status = ANY (ARRAY['Completed'::text, 'In Progress'::text])) AND tp.classname IS NOT NULL OR (tp.trainingprogram_status = ANY (ARRAY['Enrolled'::text, 'Past Due'::text]))) AND NOT (EXISTS ( SELECT 1
           FROM logs.traineestatuslogs lg
          WHERE lg.isvalid = true AND ((tp.trainingprogram_status = ANY (ARRAY['Completed'::text, 'In Progress'::text])) AND (lg.employeeid::text = tp.employeeid::text OR lg.employeeid IS NULL OR tp.employeeid IS NULL) AND (lg.personid = tp.personid OR lg.personid IS NULL OR tp.personid IS NULL) AND lg.trainingprogram::text = tp.trainingprogram::text AND lg.classname::text = tp.classname::text OR (tp.trainingprogram_status = ANY (ARRAY['Past Due'::text, 'Enrolled'::text])) AND (lg.employeeid::text = tp.employeeid::text OR lg.employeeid IS NULL OR tp.employeeid IS NULL) AND (lg.personid = tp.personid OR lg.personid IS NULL OR tp.personid IS NULL) AND lg.trainingprogram::text = tp.trainingprogram::text)))
  ORDER BY tp.trainingprogram_status, tp.completeddate, tp.employeeid;

