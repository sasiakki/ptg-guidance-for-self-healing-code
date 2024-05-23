-- PROCEDURE: staging.sp_processingtrainingtransfers()

-- DROP PROCEDURE IF EXISTS staging.sp_processingtrainingtransfers();

CREATE OR REPLACE PROCEDURE staging.sp_processingtrainingtransfers(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN
--creating temp table for update prod.trainingrequirement table and insert the data into prod.trainingtransfers
create temp table dailytransfers as
---get the recent records which are not presented in prod.trainingtransfers
with get_latest_training_transfers as (select *from staging.trainingtransfers tt where recordmodifieddate >
(select  max(coalesce (recordmodifieddate,current_timestamp ))from prod.trainingtransfers))
--get the active active training requirements to upadate prod trainingrequirement table
select tr.* , pr.trainingid
from 	
  get_latest_training_transfers tr
  join prod.trainingrequirement pr   ON tr.personid  =pr.personid
   and (tr.trainingprogramcode = pr.trainingprogramcode) and lower(pr.status) = 'active';
   
--Use group by get sum of transfer hours for single trainingid
create temp table dailytransfers_update
as
Select trainingid, sum(transferhours) as total_transfers
from dailytransfers
group by trainingid;

----valid hours update & status update
 update  prod.trainingrequirement pr
 set transferredhours= case when pr.transferredhours is null then tr.total_transfers else pr.transferredhours+tr.total_transfers end,
	 	status = CASE WHEN (requiredhours <= earnedhours+tr.total_transfers+pr.transferredhours) THEN 'closed' ELSE 'active' END,
     recordmodifieddate=now() at time zone 'utc'
  from
  dailytransfers_update tr
where tr.trainingid=pr.trainingid;

 Insert into prod.trainingtransfers
 (
	 employeeid,
	 personid,
	 trainingid,
	 trainingprogram,
	 trainingprogramcode,
	 classname,
	 dshscoursecode,
	 transferhours, 
	 completeddate,
	 transfersource,
	 reasonfortransfer
 )
 select
 			employeeid,
            personid,
			trainingid,
			trainingprogram,
			trainingprogramcode,
			classname,
			dshscoursecode,
			transferhours,
			completeddate,
			transfersource,
			reasonfortransfer
			
  from dailytransfers  ;
  drop table dailytransfers;
  drop table dailytransfers_update;
END;
$BODY$;

