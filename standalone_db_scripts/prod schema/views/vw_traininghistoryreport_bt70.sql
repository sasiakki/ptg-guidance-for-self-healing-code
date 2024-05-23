-- View: prod.vw_traininghistoryreport_bt70

-- DROP VIEW prod.vw_traininghistoryreport_bt70;

CREATE OR REPLACE VIEW prod.vw_traininghistoryreport_bt70
 AS
 SELECT DISTINCT th.personid,
    emprel.employeeid AS provideroneid,
    person.language AS preferredlanguage,
    tr.trackingdate,
    th.mod1,
    th.mod2,
    th.mod3,
    th.mod4,
    th.mod5,
    th.mod6,
    th.mod7,
    th.mod8,
    th.mod9,
    th.mod10,
    th.mod11,
    th.mod12,
    th.mod13,
    th.mod14,
    th.mod15,
    th.mod16,
    th.mod17,
    th.mod18,
    th.mod19,
    th.mod20,
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
    th.mod1 + th.mod2 + th.mod3 + th.mod4 + th.mod5 + th.mod6 + th.mod7 + th.mod8 + th.mod9 + th.mod10 + th.mod11 + th.mod12 + th.mod13 + th.mod14 + th.mod15 + th.mod16 + th.mod17 + th.mod18 + th.mod19 + th.mod20 AS completedmodules,
    20 - (th.mod1 + th.mod2 + th.mod3 + th.mod4 + th.mod5 + th.mod6 + th.mod7 + th.mod8 + th.mod9 + th.mod10 + th.mod11 + th.mod12 + th.mod13 + th.mod14 + th.mod15 + th.mod16 + th.mod17 + th.mod18 + th.mod19 + th.mod20) AS pendingmodules,
        CASE
            WHEN (th.mod1 + th.mod2 + th.mod3 + th.mod4 + th.mod5 + th.mod6 + th.mod7 + th.mod8 + th.mod9 + th.mod10 + th.mod11 + th.mod12 + th.mod13 + th.mod14 + th.mod15 + th.mod16 + th.mod17 + th.mod18 + th.mod19 + th.mod20) = 0 THEN 'Not Started'::text
            WHEN (th.mod1 + th.mod2 + th.mod3 + th.mod4 + th.mod5 + th.mod6 + th.mod7 + th.mod8 + th.mod9 + th.mod10 + th.mod11 + th.mod12 + th.mod13 + th.mod14 + th.mod15 + th.mod16 + th.mod17 + th.mod18 + th.mod19 + th.mod20) = 20 THEN 'Completed'::text
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
            sum(a.mod1) AS mod1,
            sum(a.mod2) AS mod2,
            sum(a.mod3) AS mod3,
            sum(a.mod4) AS mod4,
            sum(a.mod5) AS mod5,
            sum(a.mod6) AS mod6,
            sum(a.mod7) AS mod7,
            sum(a.mod8) AS mod8,
            sum(a.mod9) AS mod9,
            sum(a.mod10) AS mod10,
            sum(a.mod11) AS mod11,
            sum(a.mod12) AS mod12,
            sum(a.mod13) AS mod13,
            sum(a.mod14) AS mod14,
            sum(a.mod15) AS mod15,
            sum(a.mod16) AS mod16,
            sum(a.mod17) AS mod17,
            sum(a.mod18) AS mod18,
            sum(a.mod19) AS mod19,
            sum(a.mod20) AS mod20
           FROM ( SELECT transcript.personid,
                    transcript.courseid,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) ~~ '2010421ILT'::text THEN 1
                            ELSE 0
                        END AS mod1,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010422ILT'::text THEN 1
                            ELSE 0
                        END AS mod2,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010423ILT'::text THEN 1
                            ELSE 0
                        END AS mod3,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010424ILT'::text THEN 1
                            ELSE 0
                        END AS mod4,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010425ILT'::text THEN 1
                            ELSE 0
                        END AS mod5,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010426ILT'::text THEN 1
                            ELSE 0
                        END AS mod6,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010427ILT'::text THEN 1
                            ELSE 0
                        END AS mod7,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010428ILT'::text THEN 1
                            ELSE 0
                        END AS mod8,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010429ILT'::text THEN 1
                            ELSE 0
                        END AS mod9,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010430ILT'::text THEN 1
                            ELSE 0
                        END AS mod10,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010431ILT'::text THEN 1
                            ELSE 0
                        END AS mod11,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010432ILT'::text THEN 1
                            ELSE 0
                        END AS mod12,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010433ILT'::text THEN 1
                            ELSE 0
                        END AS mod13,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010434ILT'::text THEN 1
                            ELSE 0
                        END AS mod14,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010435ILT'::text THEN 1
                            ELSE 0
                        END AS mod15,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010436ILT'::text THEN 1
                            ELSE 0
                        END AS mod16,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010437ILT'::text THEN 1
                            ELSE 0
                        END AS mod17,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010438ILT'::text THEN 1
                            ELSE 0
                        END AS mod18,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010439ILT'::text THEN 1
                            ELSE 0
                        END AS mod19,
                        CASE
                            WHEN "left"(transcript.courseid::text, 10) = '2010440ILT'::text THEN 1
                            ELSE 0
                        END AS mod20
                   FROM prod.transcript
                  WHERE "left"(transcript.courseid::text, 3) = '201'::text
                  GROUP BY transcript.personid, transcript.courseid) a
          GROUP BY a.personid) th
     LEFT JOIN prod.person person ON th.personid = person.personid
     LEFT JOIN prod.employmentrelationship emprel ON th.personid = emprel.personid AND emprel.empstatus::text = 'Active'::text
     LEFT JOIN prod.trainingrequirement tr ON th.personid = tr.personid AND tr.trainingprogramcode::text = '201'::text
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
          WHERE transcript.completeddate::date < '2020-12-17'::date) legacy ON th.personid = legacy.personid AND "left"(legacy.courseid::text, 3) = '201'::text
  WHERE tr.trackingdate IS NOT NULL;

