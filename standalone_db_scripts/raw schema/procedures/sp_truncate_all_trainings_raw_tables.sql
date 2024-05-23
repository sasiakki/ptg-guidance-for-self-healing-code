-- PROCEDURE: raw.sp_truncate_all_trainings_raw_tables()

-- DROP PROCEDURE IF EXISTS "raw".sp_truncate_all_trainings_raw_tables();

CREATE OR REPLACE PROCEDURE "raw".sp_truncate_all_trainings_raw_tables(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN
truncate table raw.dshs_os_qual_agency_person;
truncate table raw.os_qual_agency_person;
truncate table raw.ss_course_completion;
truncate table raw.traininghistory;
END;
$BODY$;

