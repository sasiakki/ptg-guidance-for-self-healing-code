-- View: staging.vw_getcredentialsforgrid

-- DROP VIEW staging.vw_getcredentialsforgrid;

CREATE OR REPLACE VIEW staging.vw_getcredentialsforgrid
 AS
 WITH hmcreddohexists AS (
         SELECT p_1.personid,
            c_1.dateofhire
           FROM raw.credential_delta c_1
             JOIN staging.personhistory ps_1 ON c_1.credentialnumber::text = ps_1.credentialnumber::text
             JOIN prod.person p_1 ON p_1.personid::text = ps_1.personid::text
          WHERE c_1.credentialtype::text = 'HM'::text AND c_1.dateofhire IS NOT NULL
          GROUP BY p_1.personid, c_1.dateofhire
        )
 SELECT DISTINCT p.personid,
    c.credentialstatus,
    c.firstissuancedate,
    c.lastissuancedate,
    c.expirationdate,
    c.credentialnumber,
    c.dateofhire,
    p.hiredate,
        CASE
            WHEN c.credentialtype::text = 'HM'::text AND c.dateofhire IS NOT NULL AND to_date(c.dateofhire::text, 'MM/DD/YYYY'::text) < to_date(c.firstissuancedate::text, 'MM/DD/YYYY'::text) THEN 1
            WHEN hm.personid IS NOT NULL AND (c.credentialtype::text = ANY (ARRAY['RN'::character varying::text, 'AP'::character varying::text, 'LP'::character varying::text, 'NC'::character varying::text, 'OSPI'::character varying::text])) AND to_date(hm.dateofhire::text, 'MM/DD/YYYY'::text) >= to_date(c.firstissuancedate::text, 'MM/DD/YYYY'::text) AND to_date(hm.dateofhire::text, 'MM/DD/YYYY'::text) <= to_date(c.expirationdate::text, 'MM/DD/YYYY'::text) THEN 1
            WHEN hm.personid IS NULL AND (c.credentialtype::text = ANY (ARRAY['RN'::character varying::text, 'AP'::character varying::text, 'LP'::character varying::text, 'NC'::character varying::text, 'OSPI'::character varying::text])) AND ps.hiredate IS NOT NULL AND ps.hiredate >= to_date(c.firstissuancedate::text, 'MM/DD/YYYY'::text) AND ps.hiredate <= to_date(c.expirationdate::text, 'MM/DD/YYYY'::text) THEN 1
            ELSE 0
        END AS hiredateeligible,
        CASE
            WHEN (c.credentialtype::text = ANY (ARRAY['RN'::character varying::text, 'AP'::character varying::text, 'LP'::character varying::text, 'NC'::character varying::text, 'OSPI'::character varying::text, 'HM'::character varying::text])) AND c.credentialstatus::text = 'Active'::text THEN 1
            WHEN c.credentialtype::text = 'HM'::text AND c.lepprovisionalcredential::text = 'False'::text AND c.dateofhire IS NOT NULL AND c.credentialstatus::text = 'Pending'::text AND (CURRENT_TIMESTAMP - to_date(c.dateofhire::text, 'MM/DD/YYYY'::text)::timestamp with time zone) <= '200 days'::interval THEN 1
            WHEN c.credentialtype::text = 'HM'::text AND c.lepprovisionalcredential::text = 'True'::text AND c.dateofhire IS NOT NULL AND c.credentialstatus::text = 'Pending'::text AND to_date(c.lepprovisionalcredentialexpirationdate::text, 'MM/DD/YYYY'::text) > CURRENT_DATE THEN 1
            WHEN (c.credentialtype::text = ANY (ARRAY['NC'::character varying::text, 'OSPI'::character varying::text])) AND p.hiredate IS NOT NULL AND c.credentialstatus::text = 'Pending'::text AND (CURRENT_TIMESTAMP - to_date(c.dateofhire::text, 'MM/DD/YYYY'::text)::timestamp with time zone) <= '200 days'::interval THEN 1
            ELSE 0
        END AS eligiblestatus,
        CASE
            WHEN c.credentialtype::text = 'AP'::text THEN 1
            WHEN c.credentialtype::text = 'RN'::text THEN 2
            WHEN c.credentialtype::text = 'LP'::text THEN 3
            WHEN c.credentialtype::text = 'HM'::text THEN 4
            WHEN c.credentialtype::text = 'NC'::text THEN 5
            WHEN c.credentialtype::text = 'OSPI'::text THEN 6
            ELSE 99
        END AS rank,
    c.credentialtype
   FROM raw.credential_delta c
     JOIN staging.personhistory ps ON c.credentialnumber::text = ps.credentialnumber::text
     JOIN prod.person p ON p.personid::text = ps.personid::text
     LEFT JOIN hmcreddohexists hm ON p.personid::text = hm.personid::text;

