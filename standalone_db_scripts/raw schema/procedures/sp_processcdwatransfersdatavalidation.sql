-- PROCEDURE: raw.sp_processcdwatransfersdatavalidation()

-- DROP PROCEDURE IF EXISTS "raw".sp_processcdwatransfersdatavalidation();

CREATE OR REPLACE PROCEDURE raw.sp_processcdwatransfersdatavalidation()
 LANGUAGE plpgsql
AS $procedure$

DECLARE 
      in_isvalid BOOLEAN := TRUE;
      in_issoftError BOOLEAN := FALSE;
      in_hardError VARCHAR := ' Errortype: Hard,';
      in_softError VARCHAR := ' Errortype: Soft,';
      in_ruleno TEXT := ' Ruleno: ';
      in_errormsg TEXT := '';
      in_message TEXT := ' ErrMessage: ';
      row_countid INTEGER := 1;
      ROW record;
      cur_cdwatransfers CURSOR
      FOR 
        SELECT * from raw.fn_gettrainingtransfersbymodifiedate();
BEGIN

OPEN cur_cdwatransfers;    

LOOP

FETCH cur_cdwatransfers INTO  row;

EXIT WHEN NOT found ;

in_errormsg ='BEGIN VALIDATION   ';

      --employeeid
      IF (row.employeeid IS NULL OR CAST(row.employeeid AS TEXT) !~ '^(\d{9})?$' OR CAST(row.employeeid AS TEXT) ~ '^([0-9])\1*$') THEN 
          in_isvalid := FALSE; 
          in_errormsg := CONCAT(in_ruleno,1,in_hardError ,in_message , 'Employeeid is not valid :' ,row.employeeid);
      END IF;
      --employeeid -- 
      IF (row.employeeid IS NOT NULL AND NOT EXISTS (SELECT DISTINCT 1 FROM prod.employmentrelationship WHERE employeeid = row.employeeid)) THEN 
          in_isvalid := FALSE; 
          in_errormsg := CONCAT(in_ruleno,1,in_hardError ,in_message , 'Employeeid does not exists in Employment Relationship :' ,row.employeeid);
      END IF;
      --personid
      IF(row.personid IS NULL OR  CAST(row.personid AS TEXT) ~'^([0-9])\1*$') THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg,' ',in_ruleno,2,in_hardError,in_message,'Personid is not valid :',row.personid);
      END IF; 
      --personid -- 
      IF(row.personid IS NOT NULL AND NOT EXISTS( SELECT DISTINCT 1 FROM prod.person  WHERE cdwaid = row.personid)) THEN
        in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg,' ',in_ruleno,2,in_softError,in_message,'CDWAID is Not Available in Prod.Person (Retry) :',row.personid);
      END IF; 

      --trainingprogram
      IF(row.trainingprogram IS NULL OR LENGTH(row.trainingprogram::TEXT)>150 ) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ', in_ruleno,3,in_hardError,in_message,'Trainingprogram is not valid :',row.trainingprogram);
      END IF; 
      --trainingprogram
       IF(row.trainingprogram IS NOT NULL AND NOT EXISTS (SELECT DISTINCT 1 FROM prod.transfers_trainingprogram WHERE trainingprogram = row.trainingprogram))
        THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ', in_ruleno,3,in_hardError,in_message,'Trainingprogram does not exists :',row.trainingprogram);
      END IF;
      --classname
      IF(row.classname IS NOT NULL AND (LENGTH(row.classname::TEXT) > 150 OR row.classname !~'^[A-Za-z\d&+\- ]+$')) THEN
        in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ', in_ruleno,4,in_softError,in_message,'Classname is not valid :',row.classname);
      END IF;
      --classname
      IF(row.trainingprogram ='Continuing Education' AND row.classname IS NULL) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ', in_ruleno,4,in_hardError,in_message,'Classname is empty for CE trainingprogram :',row.classname);
      END IF;
      --dshscoursecode
      IF(row.dshscoursecode IS NOT NULL AND (LENGTH(row.dshscoursecode::TEXT) >100 OR row.dshscoursecode !~'^[A-Za-z\d]+$') )THEN
        in_issoftError := TRUE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,5,in_softError,in_message,'dshscoursecode is not valid :',row.dshscoursecode);
      END IF;
      --dshscoursecode
      IF(row.trainingprogram ='Continuing Education' AND row.dshscoursecode IS NULL) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,5,in_hardError,in_message,'dshscoursecode is empty for CE trainingprogram :',row.dshscoursecode);
      END IF;
     --credithours
    IF(row.credithours IS NOT NULL AND row.credithours <> '5' AND row.trainingprogram like 'Orientation%') THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,6,in_hardError,in_message,'Credithours for trainingprogram: ', row.trainingprogram ,' is not valid :',row.credithours);
    END IF;
    
    IF(row.credithours IS NOT NULL AND row.credithours <> '70' AND row.trainingprogram like 'Basic Training 70%') THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,6,in_hardError,in_message,'Credithours for trainingprogram: ', row.trainingprogram ,' is not valid :',row.credithours);
    END IF;
    
     IF(row.credithours IS NOT NULL AND row.credithours <> '30' AND row.trainingprogram like 'Basic Training 30%') THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,6,in_hardError,in_message,'Credithours for trainingprogram: ', row.trainingprogram ,' is not valid :',row.credithours);
    END IF;
    
     IF(row.credithours IS NOT NULL AND row.credithours <> '9' AND row.trainingprogram like 'Basic Training 9%') THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,6,in_hardError,in_message,'Credithours for trainingprogram: ', row.trainingprogram ,' is not valid :',row.credithours);
    END IF;
    
     IF(row.credithours IS NOT NULL AND (row.credithours::float not between 0 and 13) AND row.trainingprogram like 'Continuing Education%') THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,6,in_hardError,in_message,'Credithours for trainingprogram: ', row.trainingprogram ,' is not valid :',row.credithours);
    END IF;

    
       --completeddate
     IF(row.completeddate IS NOT NULL AND (LENGTH(row.completeddate::TEXT) <> 10 
                                           --OR (CAST(row.completeddate AS TEXT) !~'^[\d]+$' OR CAST(row.completeddate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$')
                                          )) THEN
        in_issoftError := TRUE;
      in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,7,in_softError,in_message,'Completeddate is not valid :',row.completeddate);
    END IF; 
    IF (row.completeddate IS NOT NULL AND date(row.completeddate::TEXT) > current_date) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,7,in_hardError,in_message,'Completion Date cannot be a future date :',row.completeddate);   
     END IF;
    --trainingentity
    IF(row.trainingentity IS NULL OR LENGTH(row.trainingentity::TEXT) >150 OR  row.trainingentity !~'^[A-Za-z\d _.]+$') THEN
        in_issoftError := TRUE;
      in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,8,in_softError,in_message,'Trainingentity is not valid :',row.trainingentity);
    END IF;
    IF (row.trainingentity IS NOT NULL AND (row.trainingprogram <> 'Orientation & Safety' AND UPPER(row.trainingentity) = 'CDWA') ) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,8,in_hardError,in_message,'Training Entity is not valid :',row.trainingentity); 
     END IF;
    --reason_for_transfer
    IF(row.reasonfortransfer IS NULL OR row.reasonfortransfer !~'^[A-Za-z\d _/.&\)\(]+$')  THEN 
        in_issoftError := TRUE;
      in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,9,in_softError,in_message,'Reasonfortranfer is not valid :',row.reasonfortransfer);
    END IF; 
    --employerstaff
    IF(row.employerstaff IS NOT NULL AND (LENGTH(row.employerstaff::TEXT) > 150  OR row.employerstaff !~'^[A-Za-z\d _.@]+$') ) THEN
        in_issoftError := TRUE;
      in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,10,in_softError,in_message,'Employerstaff is not valid :',row.employerstaff);
    END IF; 
    --createddate
    IF(row.createddate IS  NULL OR LENGTH(row.createddate::TEXT) <> 10) THEN
        in_issoftError := TRUE;
      in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,11,in_softError,in_message,'Createddate is not valid :',row.createddate);
    END IF; 
    --filename
    IF(row.filename IS NULL OR (row.filename not like 'CDWA-O-BG-TrainingTrans%' and row.filename not like '%.csv' )) THEN
    in_isvalid := FALSE;
    in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,12,in_hardError,in_message,'Filename is not valid :',row.filename);
    END IF; 
    --file date
     IF(row.filedate IS  NULL OR LENGTH(row.filedate::TEXT) <> 10)  THEN
        in_issoftError := TRUE;
      in_errormsg := CONCAT (in_errormsg , ' ', in_ruleno,13,in_softError,in_message,'filedate is not valid :',row.filedate);
    END IF; 
    
    in_errormsg := CONCAT ('RowId: ' ,row_countid,' ', in_errormsg , '  END VALIDATION        ');

 --If all rows are valid then mark record as valid
    IF(in_isvalid and row.trainingprogram like 'Orientation%') THEN
        RAISE NOTICE 'Passed all data validation';
        UPDATE raw.cdwaoandstransfers
          SET isvalid = TRUE,
            error_message = NULL
        WHERE employeeid = row.employeeid
        AND   personid = row.personid
         AND   trainingprogram = CASE WHEN row.trainingprogram IS NOT NULL  AND row.trainingprogram = 'Orientation and Safety' THEN 'Orientation & Safety' 
                                          WHEN row.trainingprogram IS NOT NULL AND row.trainingprogram = 'Advanced Training' THEN 'AHCAS (Advanced Training)' 
                                          ELSE row.trainingprogram 
                                    END
        AND   filename = row.filename;
    END IF;

     RAISE NOTICE ' % ',in_errormsg;
         
    IF ((in_isvalid = FALSE or in_issoftError) AND row.trainingprogram like 'Orientation%') THEN
                        
             UPDATE raw.cdwaoandstransfers
              SET isvalid = in_isvalid, error_message = in_errormsg
            WHERE employeeid = row.employeeid
            AND   personid = row.personid
            AND   trainingprogram = CASE WHEN row.trainingprogram IS NOT NULL  AND row.trainingprogram = 'Orientation and Safety' THEN 'Orientation & Safety' 
                                          WHEN row.trainingprogram IS NOT NULL AND row.trainingprogram = 'Advanced Training' THEN 'AHCAS (Advanced Training)' 
                                          ELSE row.trainingprogram 
                                    END
            AND   filename = row.filename;

      -- Insert a error message details into log table 
          INSERT INTO logs.trainingtransferslogs
          (
            employeeid,
            personid,
            trainingprogram,
            credithours, 
            completeddate,
            classname,
            trainingentity,
            reasonfortransfer,
            employerstaff,
            createddate,
            filename,
            filedate,        
            isvalid,
            error_message            
          )   
          VALUES
          (
            row.employeeid,
            row.personid,
            row.trainingprogram,
            row.credithours,
            row.completeddate,
            row.classname,
            row.trainingentity,
            row.reasonfortransfer,
            row.employerstaff,
            row.createddate,
            row.filename,
            row.filedate,            
            in_isvalid,
            in_errormsg         
          );        
      END IF;
      
  IF(in_isvalid and row.trainingprogram not like 'Orientation%') THEN
        RAISE NOTICE 'Passed all data validation';
        UPDATE raw.cdwatrainingtransfers
          SET isvalid = TRUE,
            error_message = NULL
        WHERE employeeid = row.employeeid
        AND   personid = row.personid
         AND   trainingprogram = CASE WHEN row.trainingprogram IS NOT NULL  AND row.trainingprogram = 'Orientation and Safety' THEN 'Orientation & Safety' 
                                          WHEN row.trainingprogram IS NOT NULL AND row.trainingprogram = 'Advanced Training' THEN 'AHCAS (Advanced Training)' 
                                          ELSE row.trainingprogram 
                                    END
        AND   filename = row.filename;
    END IF;

     RAISE NOTICE ' % ',in_errormsg;
         
    IF ((in_isvalid = FALSE or in_issoftError) AND row.trainingprogram not like 'Orientation%') THEN
           

         UPDATE raw.cdwatrainingtransfers
              SET isvalid = in_isvalid, error_message = in_errormsg
            WHERE employeeid = row.employeeid
            AND   personid = row.personid
            AND   trainingprogram = CASE WHEN row.trainingprogram IS NOT NULL  AND row.trainingprogram = 'Orientation and Safety' THEN 'Orientation & Safety' 
                                          WHEN row.trainingprogram IS NOT NULL AND row.trainingprogram = 'Advanced Training' THEN 'AHCAS (Advanced Training)' 
                                          ELSE row.trainingprogram 
                                    END
            AND   filename = row.filename;
--select * from logs.trainingtransferslogs
      -- Insert a error message details into log table 
          INSERT INTO logs.trainingtransferslogs
          (
            employeeid,
            personid,
            trainingprogram,
            credithours, 
            completeddate,
            classname,
            trainingentity,
            reasonfortransfer,
            employerstaff,
            createddate,
            filename,
            filedate,        
            isvalid,
            error_message            
          )   
          VALUES
          (
            row.employeeid,
            row.personid,
            row.trainingprogram,
            row.credithours,
            row.completeddate,
            row.classname,
            row.trainingentity,
            row.reasonfortransfer,
            row.employerstaff,
            row.createddate,
            row.filename,            
            row.filedate,            
            in_isvalid,
            in_errormsg
          );          
      END IF;     

      
    in_isvalid := TRUE;
    in_issoftError := FALSE;
    in_errormsg := ' ';
    row_countid := row_countid + 1;
    
END LOOP ;

CLOSE cur_cdwatransfers;
END;
$procedure$
;


    