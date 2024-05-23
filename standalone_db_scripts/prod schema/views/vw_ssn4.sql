-- View: prod.vw_ssn4

-- DROP VIEW prod.vw_ssn4;

CREATE OR REPLACE VIEW prod.vw_ssn4
 AS
 SELECT person.personid,
    person.firstname,
    person.lastname,
    person.middlename,
    person.dob,
    "right"(person.ssn::text, 4) AS ssn
   FROM prod.person;

