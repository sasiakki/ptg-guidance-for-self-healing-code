-- View: prod.vw_traininghistoryreport_bt7

-- DROP VIEW prod.vw_traininghistoryreport_bt7;

CREATE OR REPLACE VIEW prod.vw_traininghistoryreport_bt7
 AS
 SELECT DISTINCT th.personid,
    emprel.employeeid AS provideroneid,
    person.language AS preferredlanguage,
    tr.trackingdate,
    th.mod1,
    th.mod2,
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
    th.mod1 + th.mod2 AS completedmodules,
    2 - (th.mod1 + th.mod2) AS pendingmodules,
        CASE
            WHEN (th.mod1 + th.mod2) = 0 THEN 'Not Started'::text
            WHEN (th.mod1 + th.mod2) = 2 THEN 'Completed'::text
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
        END AS istrainingcompletedinlegacy
   FROM ( SELECT a.personid,
            sum(a.mod1) AS mod1,
            sum(a.mod2) AS mod2
           FROM ( SELECT transcript.personid,
                    transcript.courseid,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) ~~ '2040377%'::text THEN 1
                            ELSE 0
                        END AS mod1,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2040376%'::text THEN 1
                            ELSE 0
                        END AS mod2
                   FROM prod.transcript
                  WHERE "left"(transcript.courseid::text, 3) = '204'::text
                  GROUP BY transcript.personid, transcript.courseid) a
          GROUP BY a.personid) th
     LEFT JOIN prod.person person ON th.personid = person.personid
     LEFT JOIN prod.employmentrelationship emprel ON th.personid = emprel.personid AND emprel.empstatus::text = 'Active'::text
     LEFT JOIN prod.trainingrequirement tr ON th.personid = tr.personid AND tr.trainingprogramcode::text = '204'::text
     LEFT JOIN ( SELECT person_1.personid,
            string_agg(DISTINCT emp_1.employername::text, ';'::text) AS employername,
            emprel_1.empstatus
           FROM prod.person person_1
             LEFT JOIN prod.employmentrelationship emprel_1 ON person_1.personid = emprel_1.personid
             LEFT JOIN prod.employer emp_1 ON emp_1.employerid::text = emprel_1.employerid::text
          WHERE emprel_1.empstatus::text = 'Active'::text
          GROUP BY person_1.personid, emprel_1.empstatus) emp ON emp.personid = th.personid
     LEFT JOIN ( SELECT transcript.transcriptid,
            transcript.personid,
            transcript.coursename,
            transcript.courseid,
            transcript.completeddate,
            transcript.credithours,
            transcript.coursetype,
            transcript.trainingprogram,
            transcript.trainingprogramcode,
            transcript.instructorname,
            transcript.instructorid,
            transcript.dshscourseid,
            transcript.trainingsource,
            transcript.recordmodifieddate,
            transcript.recordcreateddate
           FROM prod.transcript
          WHERE transcript.completeddate::date < '2020-12-17'::date) legacy ON th.personid = legacy.personid AND "left"(legacy.courseid::text, 3) = '204'::text
  WHERE tr.trackingdate IS NOT NULL;

