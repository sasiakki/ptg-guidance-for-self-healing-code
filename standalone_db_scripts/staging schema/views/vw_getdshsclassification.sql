-- View: staging.vw_getdshsclassification

-- DROP VIEW staging.vw_getdshsclassification;

CREATE OR REPLACE VIEW staging.vw_getdshsclassification
 AS
 SELECT fn_getclassification.workercategory,
    fn_getclassification.tccode,
    fn_getclassification.workercode,
    fn_getclassification.filesource,
    fn_getclassification.employeeid,
    fn_getclassification.safetyandorientation,
    fn_getclassification.authtermflag,
    fn_getclassification.priority,
    fn_getclassification.branch1,
    fn_getclassification.branch2,
    fn_getclassification.branch3,
    fn_getclassification.branch4,
    fn_getclassification.trackingdate,
    fn_getclassification.processeddate,
    fn_getclassification.modifieddate,
    fn_getclassification.employerid
   FROM staging.fn_getclassification('DSHS'::character varying) fn_getclassification(workercategory, tccode, workercode, filesource, employeeid, safetyandorientation, authtermflag, priority, branch1, branch2, branch3, branch4, trackingdate, processeddate, modifieddate, employerid);
