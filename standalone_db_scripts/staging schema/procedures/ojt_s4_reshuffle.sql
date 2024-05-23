-- PROCEDURE: staging.ojt_s4_reshuffle()

-- DROP PROCEDURE IF EXISTS staging.ojt_s4_reshuffle();

CREATE OR REPLACE PROCEDURE staging.ojt_s4_reshuffle(
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
var_tr_reasonfortransfer character varying;
var_tr_comments character varying;
-- variables used
var_totalhours double precision := 0::double precision;
var_istrainingvalid integer;
var_tr_finalmaxcompleteddate date;
var_istrainingmapped character varying;
cur_coursecompletions cursor for SELECT transcriptid, personid, coursename, courseid, completeddate, credithours, trainingprogramcode,trainingprogram,coursetype, instructorname, instructorid, trainingsource, recordmodifieddate, recordcreateddate, dshscourseid
	FROM staging.ojt_transcript_s4;
cur_trainingreq_cc cursor (personidd bigint) for SELECT requiredhours, earnedhours, transferredhours, trainingprogram, trainingprogramcode, status, trainingid, trainreq_id, completeddate, isrequired, trackingdate, duedate, isoverride, duedateextension, created, personid, recordcreateddate,recordmodifieddate, reasonfortransfer, comments
	FROM staging.ojt_trainingrequirement_s4 where personid=personidd;
	
cur_coursetransfers cursor for SELECT transferid, personid, classname, courseid, completeddate, transferhours, trainingprogramcode,trainingprogram,  transfersource, recordmodifieddate, recordcreateddate, dshscoursecode
	FROM staging.ojt_trainingtransfers_s4;

cur_trainingreq_tf cursor (personidd bigint) for SELECT requiredhours, coalesce(earnedhours,0) as earnedhours, coalesce(transferredhours,0) as transferredhours, trainingprogram, trainingprogramcode, status, trainingid, trainreq_id, completeddate, isrequired, trackingdate, duedate, isoverride, duedateextension, created, personid, recordcreateddate,recordmodifieddate, reasonfortransfer, comments
	FROM staging.ojt_trainingrequirement_s4 where personid=personidd;

-- Looping for earned hours
BEGIN
	RAISE NOTICE 'Starting Execution';
	open cur_coursecompletions;
	LOOP
		fetch cur_coursecompletions into var_th_traininghistoryid, var_th_personid, var_th_coursename, var_th_courseid, var_th_completeddate, var_th_credithours, var_th_traningprogramcode,
		var_th_trainingprogramtype,	var_th_coursetype, var_th_instructorname, var_th_instructorid, var_th_trainingsource, var_th_recordmodifieddate, var_th_recordcreateddate, var_th_dshscourseid;
		EXIT WHEN NOT FOUND;
 		open cur_trainingreq_cc(var_th_personid);
		LOOP
			fetch cur_trainingreq_cc into var_tr_requiredhours, var_tr_earnedhours, var_tr_transferredhours, var_tr_trainingprogram, var_tr_trainingprogramcode, var_tr_status,
			var_tr_trainingid, var_tr_trainreq_id, var_tr_completeddate, var_tr_isrequired, var_tr_trackingdate, var_tr_duedate, var_tr_isoverride, var_tr_duedateextension,
			var_tr_created, var_tr_personid, var_tr_recordcreateddate, var_tr_recordmodifieddate, var_tr_reasonfortransfer, var_tr_comments;
			EXIT WHEN NOT FOUND;
			--IF (var_th_personid = var_tr_personid) Then
				RAISE NOTICE 'Learner/Person found.';
				select trainingid into var_istrainingmapped  from staging.ojt_transcript_s4 tr WHERE tr.transcriptid = var_th_traininghistoryid;
				select * into var_istrainingvalid from staging.fn_checktrainingcode(var_tr_trainingprogramcode :: character varying, var_th_traningprogramcode::character varying);
					IF (var_tr_status = 'active' and var_istrainingvalid = 1 and var_th_completeddate >= var_tr_trackingdate::date and var_th_completeddate <= var_tr_duedate::date and var_istrainingmapped is null) Then
						RAISE NOTICE 'Active training found';
						var_totalhours = var_tr_earnedhours + var_th_credithours;
								IF (var_totalhours >= var_tr_requiredhours) THEN
									RAISE NOTICE 'Update Training. Closed';

                                    UPDATE staging.ojt_trainingrequirement_s4 tr
									SET status= 'closed',
										completeddate= var_th_completeddate,
										recordmodifieddate= CURRENT_TIMESTAMP,
										earnedhours= var_tr_requiredhours
									WHERE tr.trainreq_id = var_tr_trainreq_id::uuid;
								ELSE
									RAISE NOTICE 'Update Training. Active';
									UPDATE staging.ojt_trainingrequirement_s4 tr
									SET status= 'active',
										completeddate= NULL,
										recordmodifieddate= CURRENT_TIMESTAMP,
										earnedhours= var_totalhours
									WHERE tr.trainreq_id = var_tr_trainreq_id::uuid;
								END IF;
                        UPDATE staging.ojt_transcript_s4 tr SET trainingid = var_tr_trainingid, recordmodifieddate= CURRENT_TIMESTAMP WHERE tr.transcriptid = var_th_traininghistoryid;
				    END IF;
			--END IF;
		END LOOP;
		close cur_trainingreq_cc;
	END LOOP;
	CLOSE cur_coursecompletions;

-- Looping for transfered hours
open cur_coursetransfers;
	LOOP
		fetch cur_coursetransfers into var_th_traininghistoryid, var_th_personid, var_th_coursename, var_th_courseid, var_th_completeddate, var_th_credithours, var_th_traningprogramcode,
		var_th_trainingprogramtype,	var_th_trainingsource, var_th_recordmodifieddate, var_th_recordcreateddate, var_th_dshscourseid;
		EXIT WHEN NOT FOUND;
 		open cur_trainingreq_tf(var_th_personid);
		LOOP
			fetch cur_trainingreq_tf into var_tr_requiredhours, var_tr_earnedhours, var_tr_transferredhours, var_tr_trainingprogram, var_tr_trainingprogramcode, var_tr_status,
			var_tr_trainingid, var_tr_trainreq_id, var_tr_completeddate, var_tr_isrequired, var_tr_trackingdate, var_tr_duedate, var_tr_isoverride, var_tr_duedateextension,
			var_tr_created, var_tr_personid, var_tr_recordcreateddate, var_tr_recordmodifieddate, var_tr_reasonfortransfer, var_tr_comments;
			EXIT WHEN NOT FOUND;
			--IF (var_th_personid = var_tr_personid) Then
				RAISE NOTICE 'Learner/Person found.';
				select trainingid into var_istrainingmapped  from staging.ojt_trainingtransfers_s4 tr WHERE tr.transferid = var_th_traininghistoryid;
				select * into var_istrainingvalid from staging.fn_checktrainingcode(var_tr_trainingprogramcode :: character varying, var_th_traningprogramcode::character varying);
					IF (var_tr_status = 'active' and var_istrainingvalid = 1 and var_th_completeddate >= var_tr_trackingdate::date and var_th_completeddate <= var_tr_duedate::date and var_istrainingmapped is null) Then
						RAISE NOTICE 'Active training found';
						var_totalhours = var_tr_transferredhours +var_th_credithours;
								IF (var_totalhours + var_tr_earnedhours >= var_tr_requiredhours) THEN
									RAISE NOTICE 'Update Training. Closed';

                                    UPDATE staging.ojt_trainingrequirement_s4 tr
									SET status= 'closed',
										completeddate= var_th_completeddate,
										recordmodifieddate= CURRENT_TIMESTAMP,
										transferredhours = var_totalhours
									WHERE tr.trainreq_id = var_tr_trainreq_id::uuid;
								ELSE
									RAISE NOTICE 'Update Training. Active';
									UPDATE staging.ojt_trainingrequirement_s4 tr
									SET status= 'active',
										completeddate= NULL,
										recordmodifieddate= CURRENT_TIMESTAMP,
										transferredhours= var_totalhours
									WHERE tr.trainreq_id = var_tr_trainreq_id::uuid;
								END IF;
                        UPDATE staging.ojt_trainingtransfers_s4 tr SET trainingid = var_tr_trainingid, recordmodifieddate= CURRENT_TIMESTAMP WHERE tr.transferid = var_th_traininghistoryid;
				    END IF;
			--END IF;
		END LOOP;
		close cur_trainingreq_tf;
	END LOOP;
	CLOSE cur_coursetransfers;

END;
$BODY$;

