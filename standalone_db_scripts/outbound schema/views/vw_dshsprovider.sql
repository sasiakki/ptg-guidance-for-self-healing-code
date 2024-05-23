-- View: outbound.vw_dshsprovider

-- DROP VIEW outbound.vw_dshsprovider;

CREATE OR REPLACE VIEW outbound.vw_dshsprovider
 AS
 SELECT DISTINCT btrim(p.sfcontactid::text) AS contactid,
    btrim(p.personid::text) AS studentid,
        CASE
            WHEN e.employerid IS NOT NULL THEN btrim(e.employeeid::text)
            ELSE NULL::text
        END AS dshsid,
    btrim(p.firstname::text) AS firstname,
    "left"(p.middlename::text, 1) AS middleinitial,
    btrim(p.lastname::text) AS lastname,
        CASE
            WHEN p.dob IS NOT NULL AND p.dob::text <> ''::text THEN btrim(to_char(to_date(p.dob::text, 'YYYY-MM-DD'::text)::timestamp with time zone, 'MM/DD/YYYY'::text))
            ELSE NULL::text
        END AS dob,
    btrim(p.ssn::text) AS ssnlast4,
    ''::text AS providertype,
    ''::text AS primaryemployername,
    ''::text AS activetrainingrequirement,
    ''::text AS trainingrequirementid,
    ''::text AS trainingrequirement,
    ''::text AS trackingdate,
    ''::text AS requiredhours,
    ''::text AS duedate,
    ''::text AS completedon,
    ''::text AS earnedhours,
    ''::text AS totalhours,
    ''::text AS transferredhours,
    ''::text AS closed,
    ''::text AS closedwithtermination,
    ''::text AS requirementclosedprematurelyon,
        CASE
            WHEN upper(p.exempt::text) = 'TRUE'::text THEN '1'::text
            ELSE '0'::text
        END AS exemptbasedworkhistory,
    ''::text AS studentstatus,
    ''::text AS sspsid
   FROM prod.person p
     LEFT JOIN prod.employmentrelationship e ON e.personid = p.personid AND (e.employerid::integer = ANY (ARRAY[103, 426])) AND upper(e.role::text) = 'CARE'::text AND length(e.employeeid::text) = 9;


