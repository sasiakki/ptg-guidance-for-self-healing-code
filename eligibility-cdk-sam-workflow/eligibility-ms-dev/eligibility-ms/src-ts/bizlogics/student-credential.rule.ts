import {
    Student,
    Student_training,
    Student_status_set
  } from '../models'
  import { isNullOrUndefined } from 'util';
  import { Constants } from './consts';
  import { Helper } from '../helpers/helper';
  import moment = require('moment');
  import * as _ from 'lodash';

  export class Student_credential_rule {
  
    constructor() {}
  
    public static processExistingTrainings(student: Student, trainings?: Student_training[])
      : [Student_status_set, Student_training[], Student_training[]] {
        const rule = new Student_credential_rule();
        let processed: Student_training[] = [];
        let permanentTrainingUpdates: Student_training[] = [];
        let ss: Student_status_set = new Student_status_set();
        const credential = student.credentials[0];  

        if (!isNullOrUndefined(student.student_status_set)) {
            ss = student.student_status_set;
        }

        //set credential expired; (expired || pending w/ exp date);
        ss.isCredentialExpired = Helper.isCredentialExpired(credential);

        // [processed, permanentTrainingUpdates] = rule.checkTrainings(student.assigned_category, isCredentialExpiredRestart, credential, trainings);
        [processed, permanentTrainingUpdates] = rule.checkTrainings(student, trainings);
        
        processed = processed.length === 0 ? (trainings ?? []) : processed
        return [ss, processed, permanentTrainingUpdates];
    }

    private isCredentialExpiredRestart(student: Student)
      : boolean { 
        return (!Helper.expiredCredentialIsRenewable(student)
          && _.includes([Constants.work_category.STANDARD_HCA, Constants.work_category.DDD_STANDARD], student.assigned_category))
    }

    //temporarily archive training for the eligibility run
    private archiveCompletedTraining(training: Student_training, isCredentialExpiredRestart: boolean, btTrainings: Student_training[], credentialIssueDate: string)
    : boolean {
      let archiveTraining = false; 
      if(isCredentialExpiredRestart){
        // archive completed CEs if cred is not renewable 
        if (training.training_code === Constants.training_code.CE_12.CODE
          && training.status === Constants.training_status.CLOSED
          && !(training.completed_date)) {
          archiveTraining = true; 
        //archive bt trainngs    
        } else if (_.includes(btTrainings, training) 
            && moment(training.completed_date).isSameOrBefore(moment(credentialIssueDate))){
          archiveTraining = true; 
        }
      }
      return archiveTraining;
    }

    // close training permantently in the db
    private closeTraining(training: Student_training, student: Student): boolean {
      let closeTraining = false;

    // close active CE if...
    // SHCA w/ HM|NC expired|pending(exp date required) credential
    // OR active HM|NC credential and learner is a rehire 
    // and due date is before the active|expired|pending credential expiration date;
      if (Helper.hasCategory([Constants.work_category.STANDARD_HCA], student.assigned_category)
        && training.training_code === Constants.training_code.CE_12.CODE 
        && training.status === Constants.training_status.ACTIVE
        && (
          (student.student_status_set.isCredentialExpired // expired or pending with a credential exp date
            && Helper.hasCredential([Constants.credential_type.HCA.CODE, Constants.credential_type.NAC.CODE], student.credentials, [Constants.credential_status.EXPIRED, Constants.credential_status.PENDING]))
          || 
          (Helper.hasCredential([Constants.credential_type.HCA.CODE, Constants.credential_type.NAC.CODE], student.credentials, [Constants.credential_status.ACTIVE]) 
          && student.student_status_set.isRehire))
        && moment(training.due_date).utc().startOf('day').isBefore(moment(student.credentials[0].expiration_date).utc().startOf('day')) 
        ){
          closeTraining = true;
        }
      return closeTraining;
    }

    //check trainings to temporarily archive or permanently close the training
    private checkTrainings(student: Student, trainings: Student_training[])
      : [Student_training[], Student_training[]] {
      let processedTrainings: Student_training[] = [];
      let permanentTrainingUpdates: Student_training[] = [];
      const isCredentialExpiredRestart = this.isCredentialExpiredRestart(student);
      const btTrainings = Helper.completedHigherOrEquTrainings(trainings, Constants.training_code.BT_70.CODE);

      if(!isNullOrUndefined(trainings)) {
        _.forEach(trainings, tr => {
          if (this.archiveCompletedTraining(tr, isCredentialExpiredRestart, btTrainings, student.credentials[0].firstIssuance_date)) {
            tr.archived = moment().utc().toISOString();
          } else if (this.closeTraining(tr, student)) {
            tr.status = Constants.training_status.CLOSED;
            permanentTrainingUpdates.push(tr); // update permanently
          }
          processedTrainings.push(tr); // add to temporary list for eligible checks
        });
      }
      return [processedTrainings, permanentTrainingUpdates];
    } 
  }
