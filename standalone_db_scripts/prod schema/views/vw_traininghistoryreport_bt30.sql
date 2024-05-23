-- View: prod.vw_traininghistoryreport_bt30

-- DROP VIEW prod.vw_traininghistoryreport_bt30;

CREATE OR REPLACE VIEW prod.vw_traininghistoryreport_bt30
 AS
 SELECT DISTINCT th.personid,
    emprel.employeeid AS provideroneid,
    person.language AS preferredlanguage,
    tr.trackingdate,
    th.coremod1,
    th.coremod2,
    th.coremod3,
    th.coremod4,
    th.coremod5,
    th.coremod6,
    th.coremod7,
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
    th.coremod1 + th.coremod2 + th.coremod3 + th.coremod4 + th.coremod5 + th.coremod6 AS completedmodules,
    6 - (th.coremod1 + th.coremod2 + th.coremod3 + th.coremod4 + th.coremod5 + th.coremod6) AS pendingmodules,
    tr.hourscompleted,
    tr.reqhours::double precision - tr.hourscompleted AS remaininghours,
        CASE
            WHEN (th.coremod1 + th.coremod2 + th.coremod3 + th.coremod4 + th.coremod5 + th.coremod6) = 0 THEN 'Not Started'::text
            WHEN (th.coremod1 + th.coremod2 + th.coremod3 + th.coremod4 + th.coremod5 + th.coremod6) = 6 THEN 'Completed'::text
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
   FROM ( SELECT a.personid,
            sum(a.coremod1) AS coremod1,
            sum(a.coremod2) AS coremod2,
            sum(a.coremod3) AS coremod3,
            sum(a.coremod4) AS coremod4,
            sum(a.coremod5) AS coremod5,
            sum(a.coremod6) AS coremod6,
            sum(a.coremod7) AS coremod7
           FROM ( SELECT transcript.personid,
                    transcript.courseid,
                        CASE
                            WHEN transcript.coursename::text ~~ 'Providing Care Using a Person-Centered Approach%'::text THEN 1
                            ELSE 0
                        END AS coremod1,
                        CASE
                            WHEN transcript.coursename::text ~~ 'Reducing the Spread of Infection Through Standard Precautions%'::text THEN 1
                            ELSE 0
                        END AS coremod2,
                        CASE
                            WHEN transcript.coursename::text ~~ 'Recognizing and Reporting Consumer Abuse, Neglect, and Financial Exploitation%'::text THEN 1
                            ELSE 0
                        END AS coremod3,
                        CASE
                            WHEN transcript.coursename::text ~~ 'BT 30 Skills Preparation%'::text THEN 1
                            ELSE 0
                        END AS coremod4,
                        CASE
                            WHEN transcript.coursename::text ~~ 'The Caregiver & Client Experience%'::text THEN 1
                            ELSE 0
                        END AS coremod5,
                        CASE
                            WHEN transcript.coursename::text ~~ 'Medication Assistance%'::text THEN 1
                            ELSE 0
                        END AS coremod6,
                        CASE
                            WHEN transcript.coursename::text ~~ 'Skills Lab: Mobility, including Bed-based Mobility Care with SEIU 775 Union Time%'::text THEN 1
                            ELSE 0
                        END AS coremod7
                   FROM prod.transcript
                  WHERE "left"(transcript.courseid::text, 3) = '202'::text
                  GROUP BY transcript.personid, transcript.courseid, transcript.coursename) a
          GROUP BY a.personid) th
     LEFT JOIN prod.person person ON th.personid = person.personid
     LEFT JOIN prod.employmentrelationship emprel ON th.personid = emprel.personid AND emprel.empstatus::text = 'Active'::text
     LEFT JOIN ( SELECT trainingrequirement.personid,
            trainingrequirement.trainingprogramcode,
            trainingrequirement.trackingdate,
            sum(trainingrequirement.earnedhours) AS hourscompleted,
            sum(trainingrequirement.requiredhours) AS reqhours
           FROM prod.trainingrequirement
          WHERE trainingrequirement.trainingprogramcode::text = '202'::text
          GROUP BY trainingrequirement.personid, trainingrequirement.trainingprogramcode, trainingrequirement.trackingdate) tr ON th.personid = tr.personid AND tr.trainingprogramcode::text = '202'::text
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
          WHERE transcript.completeddate::date < '2020-12-17'::date) legacy ON th.personid = legacy.personid AND "left"(legacy.courseid::text, 3) = '202'::text
  WHERE tr.trackingdate IS NOT NULL;

