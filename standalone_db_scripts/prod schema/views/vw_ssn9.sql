-- View: prod.vw_ssn9

-- DROP VIEW prod.vw_ssn9;

CREATE OR REPLACE VIEW prod.vw_ssn9
 AS
 SELECT person.personid,
    person.firstname,
    person.lastname,
    person.middlename,
    person.dob,
    person.ssn
   FROM prod.person;

