-- PROCEDURE: raw.sp_qualtables_cleandata()

-- DROP PROCEDURE IF EXISTS "raw".sp_qualtables_cleandata();

CREATE OR REPLACE PROCEDURE "raw".sp_qualtables_cleandata(
	)
LANGUAGE 'plpgsql'
AS $BODY$

 BEGIN
 DELETE FROM raw.cg_qual_agency_person
 where finished ='0' or startdate in ('StartDate','Start Date','{"ImportId":"startDate","timeZone":"Z"}','{""ImportId"":""startDate"",""timeZone"":""Z""}');
 DELETE FROM raw.dshs_os_qual_agency_person
 where finished ='0' or startdate in ('StartDate','Start Date','{"ImportId":"startDate","timeZone":"Z"}','{""ImportId"":""startDate"",""timeZone"":""Z""}');
 DELETE FROM raw.os_qual_agency_person
 where finished ='0' or startdate in ('StartDate','Start Date','{"ImportId":"startDate","timeZone":"Z"}','{""ImportId"":""startDate"",""timeZone"":""Z""}');
 --DELETE FROM raw.cg_qual_agency_person
 --where terminated_person_id ='0' and cg_status='2';
 delete from raw.os_qual_agency_person
 where finished='1' and (person_id='0' or person_id is null);
 END;
 
$BODY$;

