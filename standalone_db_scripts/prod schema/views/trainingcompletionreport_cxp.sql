-- View: prod.trainingcompletionreport_cxp

-- DROP VIEW prod.trainingcompletionreport_cxp;

CREATE OR REPLACE VIEW prod.trainingcompletionreport_cxp
 AS
 SELECT a.name,
    a.personid,
    a.provideroneid,
    a.completedtime,
    a.coursename,
    a.coursecode,
    a.shortprogname,
    a.hours,
    a.employername,
    a.mailingcity,
    a.branch_name,
    a.instructor
   FROM ( SELECT concat(person.firstname, ' ', person.lastname) AS name,
            trn.personid,
            emprel.employeeid AS provideroneid,
            trn.completeddate AS completedtime,
            trn.coursename,
            trn.courseid AS coursecode,
                CASE
                    WHEN "left"(trn.courseid::text, 3) = '300'::text THEN 'CE'::text
                    WHEN "left"(trn.courseid::text, 3) = '202'::text THEN 'BT30'::text
                    WHEN "left"(trn.courseid::text, 3) = '203'::text THEN 'BT9'::text
                    WHEN "left"(trn.courseid::text, 3) = '400'::text THEN 'CE'::text
                    WHEN "left"(trn.courseid::text, 3) = '201'::text THEN 'BT70'::text
                    WHEN "left"(trn.courseid::text, 3) = '100'::text THEN 'O&S'::text
                    WHEN "left"(trn.courseid::text, 3) = '204'::text THEN 'BT7'::text
                    ELSE NULL::text
                END AS shortprogname,
            trn.credithours AS hours,
            emp.employername,
            person.mailingcity,
            branch.branchname AS branch_name,
            trn.instructorname AS instructor,
            row_number() OVER (PARTITION BY (trn.courseid::text), 10::integer, trn.personid, emp.employername ORDER BY trn.completeddate) AS rn
           FROM prod.transcript trn
             LEFT JOIN prod.person person ON trn.personid = person.personid
             LEFT JOIN prod.employmentrelationship emprel ON trn.personid = emprel.personid
             LEFT JOIN prod.branch branch ON branch.employerid::text = emprel.employerid::text
             LEFT JOIN prod.employer emp ON emp.employerid::text = emprel.employerid::text) a
  WHERE a.rn = 1;

