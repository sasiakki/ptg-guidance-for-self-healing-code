-- PROCEDURE: staging.sp_updatetrainingrequirement()

-- DROP PROCEDURE IF EXISTS staging.sp_updatetrainingrequirement();

CREATE OR REPLACE PROCEDURE staging.sp_updatetrainingrequirement(
	)
LANGUAGE 'plpgsql'
AS $BODY$



-- course_comp cols from staging.traininghistory
declare var_th_traininghistoryid bigint;
var_th_personid bigint;
var_th_coursename character varying;
var_th_courseid character varying;
var_th_completeddate date;
var_th_credithours double precision;
var_th_traningprogramcode bigint;
var_th_trainingprogramtype character varying;
var_th_courselangulage character varying;
var_th_coursetype character varying;
var_th_instructorname character varying;
var_th_instructorid character varying;
var_th_trainingsource character varying;
var_th_recordmodifieddate timestamp without time zone;
var_th_recordcreateddate timestamp without time zone;
var_th_dshscourseid character varying;
var_th_learningpath character varying;
var_th_islearningpathchanged boolean;
var_th_filename character varying;
var_th_filedate date;

-- train_req cols from prod.trainingrequirement
var_tr_requiredhours real;
var_tr_earnedhours real;
var_tr_transferredhours real;
var_tr_trainingprogram character varying;
var_tr_trainingprogramcode character varying;
var_tr_status character varying;
var_tr_trainingid character varying;
var_tr_trainreq_id character varying;
var_tr_completeddate timestamp without time zone;
var_tr_isrequired boolean;
var_tr_trackingdate timestamp without time zone;
var_tr_duedate timestamp without time zone;
var_tr_isoverride boolean;
var_tr_duedateextension timestamp without time zone;
var_tr_created timestamp without time zone;
var_tr_personid bigint;
var_tr_recordcreateddate timestamp without time zone;
var_tr_recordmodifieddate timestamp without time zone;
var_tr_training_rank_by_createddate integer;
var_tr_maxcompleteddate date;
var_tr_learningpath character varying;
-- variables used
var_totalhours double precision := 0::double precision;
var_istrainingvalid integer;
var_tr_finalmaxcompleteddate date;
var_tr_finalstatus character varying;
var_tr_finalearnedhours real;
var_tr_found boolean;
var_record_type character varying;

-- ONLY PROCESS TO CREATE TRANSCRIPTS; IF THIS CHANGES, WILL NEED TO STORE THE LASTRUNTIME
cur_coursecompletions cursor for select * from staging.traininghistory where recordcreateddate > (select max(recordcreateddate) from prod.transcript ) order by recordcreateddate; --Add columns
cur_trainingreq cursor (personidd bigint) for select COALESCE(requiredhours,0) as requiredhours,COALESCE(earnedhours, 0) as earnedhours ,transferredhours, trainingprogram,trainingprogramcode :: bigint as trainingprogramcode,status,trainingid,trainreq_id,completeddate,isrequired,
			trackingdate,duedate,isoverride,duedateextension,created,personid,recordcreateddate,recordmodifieddate
			, ROW_NUMBER() OVER ( PARTITION BY personid ORDER BY isrequired DESC, created ASC) training_rank_by_createddate,learningpath
			from prod.trainingrequirement 
			where lower(status) = 'active'
			and personid = personidd
			and (trackingdate::date <= current_date 
				-- TODO: remove hardcoded - unique trainingcodes should be held in a table with a column tracking_date_nullable::boolean
				OR trainingprogramcode in ('100', '200', '500', '602')) -- training codes w/o tracking dates
			order by personid ,trainingprogramcode;

BEGIN
	RAISE NOTICE 'Starting Execution';
	OPEN cur_coursecompletions;
	LOOP
		FETCH cur_coursecompletions INTO var_th_traininghistoryid, var_th_personid, var_th_coursename, var_th_courseid, var_th_completeddate, var_th_credithours, var_th_traningprogramcode,
		var_th_trainingprogramtype,	var_th_courselangulage, var_th_coursetype, var_th_instructorname, var_th_instructorid, var_th_trainingsource, var_th_recordmodifieddate, var_th_recordcreateddate, 
		var_th_dshscourseid,var_th_learningpath, var_th_islearningpathchanged, var_th_filename, var_th_filedate;
		EXIT WHEN NOT FOUND;

		--check if this traininghistory is a duplicate transcript (based on core id or dshscourseid if available);
		IF EXISTS ( SELECT 1 FROM prod.transcript WHERE personid = var_th_personid 
			and ( courseid  like left(var_th_courseid, length(var_th_courseid)-7) || '%' OR dshscourseid = coalesce(var_th_dshscourseid, 'NA')) limit 1) THEN
			RAISE NOTICE 'DUPLICATE TRANSCRIPT FOUND: personid %, courseid %, dshscourseid %, completeddate %', var_th_personid, var_th_courseid, var_th_dshscourseid, var_th_completeddate;

			-- add error record
			INSERT INTO logs.traininghistorylog("personid","completeddate","credithours","coursename","courseid","coursetype","courselanguage","trainingprogramcode","trainingprogramtype","instructorname","instructorid","trainingsource","dshscourseid","filename","filedate","error_message")
			VALUES(var_th_personid,var_th_completeddate,var_th_credithours,var_th_coursename,var_th_courseid,var_th_coursetype,var_th_courselangulage,var_th_traningprogramcode,var_th_trainingprogramtype,var_th_instructorname,var_th_instructorid,var_th_trainingsource,var_th_dshscourseid,var_th_filename,var_th_filedate,'Course was previously Completed; error thrown in sp_updatetrainingrequirement');
		ELSE
			-- grab all active trainings for person
			OPEN cur_trainingreq(var_th_personid);
			LOOP
				FETCH cur_trainingreq INTO var_tr_requiredhours, var_tr_earnedhours, var_tr_transferredhours, var_tr_trainingprogram, var_tr_trainingprogramcode, var_tr_status,
				var_tr_trainingid, var_tr_trainreq_id, var_tr_completeddate, var_tr_isrequired, var_tr_trackingdate, var_tr_duedate, var_tr_isoverride, var_tr_duedateextension,
				var_tr_created, var_tr_personid, var_tr_recordcreateddate, var_tr_recordmodifieddate, var_tr_training_rank_by_createddate,var_tr_learningpath;
				
				-- reset
				var_tr_found = false;
				var_record_type = 'ORPHAN';

				IF (COALESCE(var_tr_status, 'closed') = 'active') THEN
					SELECT * INTO var_istrainingvalid FROM staging.fn_checktrainingcode(var_tr_trainingprogramcode::character varying, var_th_traningprogramcode::character varying);
					-- check if completed date fits or programcode 
					IF (var_istrainingvalid = 1 
						AND ((var_th_completeddate >= var_tr_trackingdate::date 
								AND var_th_completeddate <= coalesce(var_tr_duedateextension::date, var_tr_duedate::date))
							-- TODO: remove hardcoded - all unique trainingcodes should be held in a table with a column tracking_date_nullable::boolean
							OR (var_tr_trainingprogramcode in ('100', '200', '500', '602')))
						AND coalesce(var_th_islearningpathchanged,false) = false
						) THEN

						-- FOUND Training
						var_tr_found = true;
						var_record_type = 'RELATED';

						var_tr_finalstatus = 'active';
						var_tr_finalearnedhours = coalesce(var_tr_earnedhours, 0) + var_th_credithours;
						var_tr_finalmaxcompleteddate = NULL;
						-- check if training gets closed;
						IF ((var_tr_finalearnedhours + coalesce(var_tr_transferredhours, 0)) >= coalesce(var_tr_requiredhours, 0)) THEN
							var_tr_finalstatus = 'closed';

							--get maxcompleteddate;
							var_tr_maxcompleteddate = coalesce(prod.fn_get_training_requirement_max_completeddate(var_tr_personid, var_tr_trainingid), var_th_completeddate);

							IF(var_tr_maxcompleteddate IS NOT NULL AND var_tr_maxcompleteddate >= var_th_completeddate) THEN
								var_tr_finalmaxcompleteddate = var_tr_maxcompleteddate;
							ELSE
								var_tr_finalmaxcompleteddate = var_th_completeddate;
							END IF;
						END IF;

						-- update training requirement
						RAISE NOTICE 'UPDATE trainingid %, learningpath %, status %, earnedhrs %, completeddate %, trackingdate %, duedate %, extensiondate %', var_tr_trainingid, var_th_learningpath, var_tr_finalstatus, var_tr_finalearnedhours, var_tr_finalmaxcompleteddate, var_tr_trackingdate, var_tr_duedate, var_tr_duedateextension;
						UPDATE prod.trainingrequirement tr
						SET status = var_tr_finalstatus,
							completeddate = var_tr_finalmaxcompleteddate,
							recordmodifieddate = CURRENT_TIMESTAMP,
							earnedhours = var_tr_finalearnedhours,
							learningpath = var_th_learningpath
						WHERE tr.trainreq_id = var_tr_trainreq_id::uuid;
					END IF;
				END IF;

				-- insert transcript if a training was found or run out of trainings;
				IF (var_tr_found OR NOT FOUND) THEN
					RAISE NOTICE 'CREATE % Record personid %, courseid %, complededdate %, trainingid %', var_record_type, var_th_personid, var_th_courseid, var_th_completeddate, var_tr_trainingid;

					-- all training history records get inserted; only insert if tr has been processed or NOT FOUND ()
					INSERT INTO prod.transcript(trainingid, personid, coursename, completeddate, instructorname, credithours, coursetype, trainingprogram, trainingprogramcode,courseid, instructorid, trainingsource, recordcreateddate, recordmodifieddate, dshscourseid, learningpath)
					VALUES (var_tr_trainingid, var_th_personid,var_th_coursename,var_th_completeddate,var_th_instructorname,var_th_credithours,var_th_coursetype,var_th_trainingprogramtype,var_th_traningprogramcode,var_th_courseid,var_th_instructorid,var_th_trainingsource,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,var_th_dshscourseid,var_th_learningpath);

					-- exit loop
					EXIT;
				END IF;

			END LOOP;
			CLOSE cur_trainingreq;
		END IF;
	END LOOP;
	CLOSE cur_coursecompletions;
END;
$BODY$;

