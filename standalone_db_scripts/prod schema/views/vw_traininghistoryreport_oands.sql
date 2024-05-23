-- View: prod.vw_traininghistoryreport_oands

-- DROP VIEW prod.vw_traininghistoryreport_oands;

CREATE OR REPLACE VIEW prod.vw_traininghistoryreport_oands
 AS
 SELECT th.personid,
    emprel.employeeid AS provideroneid,
    person.language AS preferredlanguage,
    tr.trackingdate,
    tr.duedate,
    tr.duedateextension AS duedateoverride,
    person.firstname,
    person.lastname,
    person.mailingstreet1 AS mailingaddr1,
    person.mailingstreet2 AS mailingaddr2,
    person.mailingcity,
    person.mailingstate,
    person.mailingzip,
    person.mailingcountry,
    person.email1 AS email,
    person.mobilephone,
    person.homephone AS phone,
    person.workercategory,
    emp.employername AS activeemployers,
    emp.empstatus AS workstatus,
    th.completed_modules AS completedmodules,
    tr.hourscompleted,
        CASE
            WHEN th.completed_modules = 0 THEN 'Not Started'::text
            WHEN th.completed_modules = 12 THEN 'Completed'::text
            ELSE 'In Progress'::text
        END AS trainingstatus,
        CASE
            WHEN tr.trackingdate >= '2019-08-17 00:00:00'::timestamp without time zone AND tr.trackingdate <= '2020-09-30 00:00:00'::timestamp without time zone THEN 'Cohort1'::text
            WHEN tr.trackingdate >= '2020-10-01 00:00:00'::timestamp without time zone AND tr.trackingdate <= '2021-04-30 00:00:00'::timestamp without time zone THEN 'Cohort2'::text
            WHEN tr.trackingdate >= '2021-05-01 00:00:00'::timestamp without time zone AND tr.trackingdate <= '2022-03-31 00:00:00'::timestamp without time zone THEN 'Cohort3'::text
            WHEN tr.trackingdate > '2022-03-31 00:00:00'::timestamp without time zone THEN 'Cohort4'::text
            ELSE NULL::text
        END AS cohort,
        CASE
            WHEN legacy.personid IS NULL THEN 'FALSE'::text
            ELSE 'TRUE'::text
        END AS istrainingcompletedinlegacy,
    person.type
   FROM ( SELECT transcript_1.personid,
            transcript_1.courseid,
            count(*) AS completed_modules
           FROM prod.transcript transcript_1
          WHERE "left"(transcript_1.courseid::text, 3) = '100'::text
          GROUP BY transcript_1.personid, transcript_1.courseid) th
     LEFT JOIN prod.person person ON th.personid = person.personid
     LEFT JOIN prod.employmentrelationship emprel ON th.personid = emprel.personid AND emprel.empstatus::text = 'Active'::text
     LEFT JOIN ( SELECT trainingrequirement.personid,
            trainingrequirement.trainingprogramcode,
            trainingrequirement.duedate,
            trainingrequirement.duedateextension,
            trainingrequirement.trackingdate,
            sum(trainingrequirement.earnedhours) AS hourscompleted
           FROM prod.trainingrequirement
          WHERE trainingrequirement.trainingprogramcode::text = '100'::text
          GROUP BY trainingrequirement.personid, trainingrequirement.trainingprogramcode, trainingrequirement.trackingdate, trainingrequirement.duedate, trainingrequirement.duedateextension) tr ON th.personid = tr.personid AND tr.trainingprogramcode::text = '100'::text
     LEFT JOIN ( SELECT person_1.personid,
            string_agg(DISTINCT emp_1.employername::text, ';'::text) AS employername,
            emprel_1.empstatus
           FROM prod.person person_1
             LEFT JOIN prod.employmentrelationship emprel_1 ON person_1.personid = emprel_1.personid
             LEFT JOIN prod.employer emp_1 ON emp_1.employerid::text = emprel_1.employerid::text
          WHERE emprel_1.empstatus::text = 'Active'::text
          GROUP BY person_1.personid, emprel_1.empstatus) emp ON emp.personid = th.personid
     LEFT JOIN prod.transcript transcript ON th.personid = transcript.personid AND "left"(transcript.courseid::text, 3) = '100'::text
     LEFT JOIN ( SELECT transcript_1.transcriptid,
            transcript_1.personid,
            transcript_1.coursename,
            transcript_1.courseid,
            transcript_1.completeddate,
            transcript_1.credithours,
            transcript_1.coursetype,
            transcript_1.trainingprogram,
            transcript_1.trainingprogramcode,
            transcript_1.instructorname,
            transcript_1.instructorid,
            transcript_1.dshscourseid,
            transcript_1.trainingsource,
            transcript_1.recordmodifieddate,
            transcript_1.recordcreateddate
           FROM prod.transcript transcript_1
          WHERE transcript_1.completeddate::date < '2020-12-17'::date) legacy ON th.personid = legacy.personid AND transcript.courseid::text = legacy.courseid::text
  WHERE tr.trackingdate IS NOT NULL;

