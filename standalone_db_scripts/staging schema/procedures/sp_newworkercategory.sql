-- PROCEDURE: staging.sp_newworkercategory()

-- DROP PROCEDURE IF EXISTS staging.sp_newworkercategory();

CREATE OR REPLACE PROCEDURE staging.sp_newworkercategory(
	)
LANGUAGE 'plpgsql'
AS $BODY$

declare var_workercategory character varying;
var_tccode character varying;
var_workercode character varying;
var_filesource character varying;
var_employeeid numeric; 
var_safetyandorientation character varying;
var_authtermflag character varying;
var_priority integer;
var_branch1 character varying;
var_branch2 character varying; 
var_branch3 character varying; 
var_branch4 character varying; 
var_trackingdate character varying;
var_processeddate timestamp without time zone;
var_modifieddate timestamp without time zone;
var_employerid integer;
var_counter int :=1;
var_classification character varying;
var_code character varying;
var_restclassification character varying;
var_restcode character varying;
var_sourcekey character varying;
prev_priority INTEGEr;
prev_authend character varying;
prev_classification character varying;
var_trackingdatediff boolean;
fn_branchid character varying;
var_checkcount integer:=0;
prev_orientationandsafety date;
row_classificationstaging record;
rec_icd12 record;
var_max_filedate date;

cur_icd12 cursor for select * from staging.fn_getClassification('DSHS'); --Add columns

BEGIN

	RAISE NOTICE 'Starting Execution';
	open cur_icd12;
	LOOP
		fetch cur_icd12 into var_workercategory,var_tccode,var_workercode,var_filesource,var_employeeid,var_safetyandorientation,var_authtermflag,var_priority,var_branch1,var_branch2,var_branch3,var_branch4,var_trackingdate,var_processeddate,var_modifieddate,var_employerid;
		EXIT WHEN NOT FOUND;
	  
	    IF var_filesource = 'DSHSPatch' THEN
        	var_filesource = 'DSHS';
		END IF;
		
		IF var_branch1 = '' or var_branch1 is null THEN
			var_branch1 = '-9999';
		END IF;
		
		IF var_branch2 = '' or var_branch2 is null THEN
			var_branch2 = '-9999';
		END IF;
		
		IF var_branch3 = '' or var_branch3 is null THEN
			var_branch3 = '-9999';
		END IF;
		
		IF var_branch4 = '' or var_branch4 is null THEN
			var_branch4 = '-9999';
		END IF;
		
		--var_sourcekey = var_filesource || var_employeeid;
		var_sourcekey = var_filesource ||'-'|| var_employeeid;
		IF var_workercategory is NULL THEN
		
			RAISE NOTICE 'KeyError:ERROR_NO_worker_category, %', var_employeeid;
			
		  	var_classification = 'KeyError:ERROR_NO_worker_category';
		  	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_workercode is NULL THEN
		
			RAISE NOTICE 'KeyError:ERROR_NO_worker_code, %', var_employeeid;

		  	var_classification = 'KeyError:ERROR_NO_worker_code';
		  	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_safetyandorientation is NULL THEN
					
			RAISE NOTICE 'KeyError:ERROR_NO_safetyandorientation, %', var_employeeid;

		  	var_classification = 'KeyError:ERROR_NO_safetyandorientation';
		  	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_filesource = 'DSHSPatchIncorrect' THEN
		
			RAISE NOTICE 'ValidationError:ERROR_VOID_RECORD, %', var_employeeid;
			
        	var_classification = 'ValidationError:ERROR_VOID_RECORD';
        	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_safetyandorientation = '1' AND (var_authtermflag = '1' or var_workercode like '%1%') THEN
		
			RAISE NOTICE 'ValidationError:ERROR_MIXED_FLAGS_TRUE_SNO, %', var_employeeid;
			
		  	var_classification = 'ValidationError:ERROR_MIXED_FLAGS_TRUE_SNO';
		  	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_authtermflag = '1' and (var_safetyandorientation = '1' or var_workercode like '%1%') THEN
		
			RAISE NOTICE 'ValidationError:ERROR_MIXED_FLAGS_TRUE_TERM, %', var_employeeid;
			
			var_classification = 'ValidationError:ERROR_MIXED_FLAGS_TRUE_TERM';
        	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_trackingdate = '00000000' THEN
		
			RAISE NOTICE 'ValidationError:ERROR_NO_TRACKING_DATES, %', var_employeeid;
			
        	var_classification = 'ValidationError:ERROR_NO_TRACKING_DATES';
        	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		ELSIF var_safetyandorientation = '1' THEN
		
			RAISE NOTICE 'S&O is 1, %', var_employeeid;

			SELECT Count(*) into var_checkcount from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer));
			prev_authend := (SELECT prevauthend from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer)) limit 1);
			IF var_checkcount > 0 and prev_authend is NOT null THEN
			
				RAISE NOTICE 'COUNT>0/prev_authend not null, %', var_employeeid;
				
				prev_orientationandsafety := (SELECT prevorientationandsafetydate from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer)) limit 1);
				IF prev_orientationandsafety is NOT null THEN 
				
					RAISE NOTICE 'ValidationError:O&S already completed, %', var_employeeid;

					var_classification = 'ValidationError:O&S already completed';
                	var_code = '';
					
					INSERT INTO logs.workercategoryerrors(
					sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
					VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
				ELSE
					
					RAISE NOTICE 'prevorientation is null, %', var_employeeid;

					var_classification = 'Orientation & Safety';
					var_code = 'OSAF';
					IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;

							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
								(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;

							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
				    	END IF;
					END IF;
					
					IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
					
					UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;
						
				END IF;
			
			ELSIF var_checkcount > 0 and prev_authend is NULL THEN
			
				RAISE NOTICE 'ValidationError:No changes in classification, %', var_employeeid;

				var_classification = 'ValidationError:No changes in classification';
            	var_code = '';
				
				INSERT INTO logs.workercategoryerrors(
				sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
				VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
				
			ELSE
			
				RAISE NOTICE 'orientation is 1/count is 0, %, %, %, %, %', var_employeeid, var_branch1, var_branch2, var_branch3, var_branch4;

				var_classification = 'Orientation & Safety';
            	var_code = 'OSAF';
				IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
					
					RAISE NOTICE 'orientation is 1/count is 0, %, %', var_employeeid, var_branch1;

					IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
							(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;
					
				IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
							(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
			    	END IF;
				END IF;
					
				IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
							(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;
					
				IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
							(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;
				
				RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
				
				UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;

			END IF;
		
		ELSIF var_safetyandorientation = '0' and var_authtermflag = '0' and var_workercode like '%1%' THEN
						
			RAISE NOTICE 'orientation 0/authterm 0/workercode like 1, %', var_employeeid;

			SELECT Count(*) into var_checkcount from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer));
			IF var_checkcount > 0 THEN
			
				RAISE NOTICE 'count > 0, %', var_employeeid;

				prev_classification:= (SELECT prevclassification from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer))limit 1);
				var_trackingdatediff:= (SELECT case when count(distinct employeeid) > 1 THEN true else false end as isTrackingDatediff 
        							   FROM prod.employmentrelationship where employeeid = var_employeeid and workercategory = prev_classification and authend is null
        							   and CAST(trackingdate AS DATE) <> CAST(var_trackingdate AS DATE));
				prev_priority:= (SELECT prevpriority from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer)) limit 1);
				prev_authend := (SELECT prevauthend from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer)) limit 1);
				fn_branchid:= (SELECT fnbranchid from staging.fn_get_previous_categories(var_employeeid,cast(var_branch1 as integer),cast(var_branch2 as integer),cast(var_branch3 as integer),cast(var_branch4 as integer)) limit 1);
				
				IF var_trackingdatediff = true and var_filesource <> 'DSHSPatch' THEN
				
					RAISE NOTICE 'ValidationError:ERROR_TRACKING_DATES_DIFFER_FOR_SAME_CAT, %', var_employeeid;

					var_classification = 'ValidationError:ERROR_TRACKING_DATES_DIFFER_FOR_SAME_CAT';
                	var_code = '';
					
					INSERT INTO logs.workercategoryerrors(
					sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
					VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
				
				ELSIF prev_priority is not NULL and var_priority = prev_priority and var_filesource <> 'DSHSPatch' and prev_authend is NULL THEN
				
					RAISE NOTICE 'ValidationError:No changes in classification/but rest inserts are made, %', var_employeeid;

					var_classification = 'ValidationError:No changes in classification';
                	var_code = '';
					
					INSERT INTO logs.workercategoryerrors(
					sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
					VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
					var_restclassification = var_workercategory;
					var_code = var_tccode;
					
					IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <>fn_branchid and var_branch1 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
								(null,var_employeeid,cast(var_branch1 as integer),var_restclassification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <>fn_branchid and var_branch2 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch2 as integer),var_restclassification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <>fn_branchid and var_branch3 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch3 as integer),var_restclassification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <>fn_branchid and var_branch4 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch4 as integer),var_restclassification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
					
					UPDATE staging.personhistory SET WorkerCategory = var_restclassification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;
					
				ELSIF prev_priority is not NULL and var_priority = prev_priority and var_filesource <> 'DSHSPatch' and prev_authend is not NULL THEN
				
					RAISE NOTICE 'prevpri is not null-pri=prevpri-DSHSPatch file-authend is not null, %', var_employeeid;

					var_classification = var_workercategory;
					var_code = var_tccode;
					
					IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
								(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
					
					--UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;
					
				ELSIF prev_priority is not NULL and var_priority > prev_priority and var_filesource <> 'DSHSPatch' THEN
					
					RAISE NOTICE 'prevpri is not null- pri>prevpri -DSHSPatch file, %', var_employeeid;

					var_classification = var_workercategory;
                	var_code = var_tccode;
					
					IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
								(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
					
				--	UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;
					
				ELSIF prev_priority is not NULL and var_priority >= prev_priority and var_filesource = 'DSHSPatch' THEN
					
					RAISE NOTICE 'prevpri is not null- pri>=prevpri -DSHSPatch file, %', var_employeeid;

					var_classification = var_workercategory;
                	var_code = var_tccode;
					-- override is 1					
					IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch1, 1, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
								(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch2, 1, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch3, 1, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch4, 1, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
					
				--	UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;
					
				ELSE
					
					RAISE NOTICE 'prevpri is null or not null- pri<prevpri - DSHSPatch file or something, %', var_employeeid;

					var_classification = var_workercategory;
                	var_code = var_tccode;
					
					IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
								(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;

					IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
						IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
							
							RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
							
							INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
								relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
								(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
						END IF;
					END IF;
					
					RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;
					
				--	UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;

				END IF;
			
			ELSE
			
				RAISE NOTICE 'orientation 0/authterm 0/workercode like 1/ count is 0, %', var_employeeid;

				var_classification = var_workercategory;
             	var_code = var_tccode;
				
				IF var_branch1 <> '' and var_branch1 <> '00' and var_branch1 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch1, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role ) VALUES 
							(null,var_employeeid,cast(var_branch1 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;

				IF var_branch2 <> '' and var_branch2 <> '00' and var_branch2 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch2, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
							(null,var_employeeid,cast(var_branch2 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;

				IF var_branch3 <> '' and var_branch3 <> '00' and var_branch3 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch3, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
							(null,var_employeeid,cast(var_branch3 as integer),var_classification,var_modifieddate,null,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;
				
				IF var_branch4 <> '' and var_branch4 <> '00' and var_branch4 <> '-9999' THEN
					IF staging.fn_check_active_erh_update(var_branch4, 0, var_workercategory,var_employeeid,var_modifieddate) = TRUE THEN
						
						RAISE NOTICE 'active_update is true/make insert, %', var_employeeid;
						
						INSERT INTO prod.employmentrelationship (personid,employeeid,BranchId,workercategory,authstart,authend,trackingDate,
							relationship,empstatus,categoryCode,EmployerId,filedate,createdby,source,hiredate, priority, role) VALUES 
							(null,var_employeeid,cast(var_branch4 as integer),var_classification,var_modifieddate,NULL,var_trackingdate,null,'Active',var_code,var_employerid,var_modifieddate,'workercategorystoredproc',var_sourcekey,var_trackingdate::timestamp without time zone, var_priority,'CARE');
					END IF;
				END IF;
					
				RAISE NOTICE 'making update in personhistory , %, %, %', var_employeeid, var_sourcekey, var_modifieddate::date;

-- 				UPDATE staging.personhistory SET WorkerCategory = var_classification::character varying, categorycode = var_code::character varying, Status = 'Active', modified = current_timestamp, recordmodifieddate = current_timestamp WHERE sourcekey = var_sourcekey and filemodifieddate::date = var_modifieddate::date;
			
			END IF;
			
		ELSE
			
			RAISE NOTICE 'ValidationError: ERROR_NO_WORKER_CLASSIFICATION_FOUND, %', var_employeeid;

			var_classification = 'ValidationError: ERROR_NO_WORKER_CLASSIFICATION_FOUND';
        	var_code = '';
			
			INSERT INTO logs.workercategoryerrors(
			sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error)
			VALUES (var_sourcekey, var_employeeid, var_filesource, var_modifieddate, var_workercategory, var_code, var_classification);
			
		END IF;	   
		
		IF var_classification like '%ValidationError%' or var_classification like '%KeyError%' THEN
			-- code for adding to validation logs. TBD
			RAISE NOTICE 'ValidationErrors exist';
			
		END IF;

	END LOOP;
    
	CLOSE cur_icd12;	
	
	var_modifieddate:= (select modifieddate from staging.fn_getclassification('DSHS') limit 1);
	
-- 	WITH cte AS
-- 	(
-- 	  SELECT sourcekey,
-- 			 filemodifieddate
-- 	  FROM staging.personhistory
-- 	  WHERE sourcekey ilike 'DSHS%'
-- 	  AND   workercategory IS NULL
-- 	  AND   categorycode IS NULL
-- 	  AND   status IS NULL
-- 	  AND   filemodifieddate::date = var_modifieddate::date
-- 	),
-- 	cte2 AS
-- 	(
-- 	  SELECT m2.workercategory,
-- 			 m2.categorycode,
-- 			 m2.source,
-- 			 m2.empstatus,
-- 			 m2.rn,
-- 			 cte.*
-- 	  FROM (SELECT r.*,
-- 				   ROW_NUMBER() OVER (PARTITION BY source ORDER BY recordmodifieddate DESC) AS rn
-- 			FROM prod.employmentrelationship r
-- 			WHERE source LIKE 'DSHS%') m2
-- 		JOIN cte
-- 		  ON cte.sourcekey = m2.source
-- 		 AND m2.rn = 1
-- 	)
-- 	UPDATE staging.personhistory p
-- 	   SET workercategory = cte2.workercategory,
-- 		   categorycode = cte2.categorycode,
-- 		   status = cte2.empstatus,
-- 		   recordmodifieddate = current_timestamp
-- 	FROM cte2
-- 	WHERE cte2.sourcekey = p.sourcekey
-- 	AND   p.filemodifieddate::date = var_modifieddate::date;

END;
$BODY$;

