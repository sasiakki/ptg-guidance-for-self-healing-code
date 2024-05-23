-- View: prod.vw_personid_crosswalk

-- DROP VIEW prod.vw_personid_crosswalk;

CREATE OR REPLACE VIEW prod.vw_personid_crosswalk
 AS
 SELECT DISTINCT person.personid,
    person.firstname,
    person.lastname,
    person.middlename,
    person.dob,
    person.mailingstreet1,
    person.mailingstreet2,
    person.mailingcity,
    person.mailingstate,
    person.mailingzip,
    person.workercategory,
    tr.status,
    tr.trainingprogram,
    tr.trackingdate,
    tr.duedate,
    tr.isoverride,
    tr.duedateextension,
    person.mobilephone,
    person.homephone,
    person.email1,
    person.email2,
    person.exempt,
    emprelationship.employeeid,
    emp.employername,
        CASE
            WHEN emp.number_of_employers > 1 THEN 'Yes'::text
            ELSE 'No'::text
        END AS mulitple_employers,
    emp.empstatus
   FROM prod.person person
     LEFT JOIN prod.trainingrequirement tr ON tr.personid = person.personid
     LEFT JOIN prod.employmentrelationship emprelationship ON emprelationship.personid = person.personid
     LEFT JOIN ( SELECT person_1.personid,
            count(DISTINCT emp_1.employername) AS number_of_employers,
            string_agg(DISTINCT emp_1.employername::text, ';'::text) AS employername,
            emprel_1.empstatus
           FROM prod.person person_1
             LEFT JOIN prod.employmentrelationship emprel_1 ON person_1.personid = emprel_1.personid
             LEFT JOIN prod.employer emp_1 ON emp_1.employerid::text = emprel_1.employerid::text
          WHERE emprel_1.empstatus::text = 'Active'::text
          GROUP BY person_1.personid, emprel_1.empstatus) emp ON emp.personid = emprelationship.personid;

