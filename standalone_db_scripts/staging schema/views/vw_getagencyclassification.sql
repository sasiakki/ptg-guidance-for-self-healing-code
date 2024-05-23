CREATE OR REPLACE VIEW staging.vw_getagencyclassification
AS 
 SELECT employmentrelationshiphistory.relationshipid,
    employmentrelationshiphistory.personid,
    employmentrelationshiphistory.employeeid,
    employmentrelationshiphistory.workercategory,
    employmentrelationshiphistory.categorycode,
    employmentrelationshiphistory.role,
    employmentrelationshiphistory.source,
    employmentrelationshiphistory.priority,
    employmentrelationshiphistory.modifieddate,
    employmentrelationshiphistory.createdby,
    employmentrelationshiphistory.filedate,
    employmentrelationshiphistory.relationship,
    employmentrelationshiphistory.branchid,
    employmentrelationshiphistory.hiredate,
    employmentrelationshiphistory.authstart,
    employmentrelationshiphistory.authend,
    employmentrelationshiphistory.terminationdate,
    employmentrelationshiphistory.empstatus,
    employmentrelationshiphistory.trackingdate,
    employmentrelationshiphistory.modified,
    employmentrelationshiphistory.employerid,
    employmentrelationshiphistory.recordmodifieddate,
    employmentrelationshiphistory.recordcreateddate,
    employmentrelationshiphistory.sfngrecordid,
    employmentrelationshiphistory.isignored,
    employmentrelationshiphistory.isoverride,
    employmentrelationshiphistory.agencyid
   FROM staging.employmentrelationshiphistory
 WHERE UPPER(employmentrelationshiphistory.source::TEXT) !~~ '%DSHS%'::TEXT
AND   UPPER(employmentrelationshiphistory.source::TEXT) !~~ '%DOH%'::TEXT
AND   UPPER(employmentrelationshiphistory.source::TEXT) !~~ '%CDWA%'::TEXT
AND   UPPER(employmentrelationshiphistory.source::TEXT) !~~ '%SFLegacy%'::TEXT
AND   UPPER(employmentrelationshiphistory.source::TEXT) !~~ '%PORTAL%'::TEXT
AND   employmentrelationshiphistory.filedate > (SELECT CASE
                                                        WHEN MAX(lastprocesseddate) IS NULL THEN (CURRENT_DATE -1)
                                                        ELSE MAX(lastprocesseddate)
                                                      END AS MAXPROCESSDATE
                                               FROM logs.lastprocessed
                                               WHERE processname = 'glue-ap-to-employmentrelationship'
                                               AND   success = '1');
