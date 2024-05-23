import {
  Student,
  Student_training
} from '../models'
import { isNullOrUndefined } from 'util';
import { Constants } from './consts';
import { Helper } from '../helpers/helper';
import moment = require('moment');
import * as _ from 'lodash';

export class Student_training_compliant_status_rule {
  
  constructor() {}
  
  public static isCompliant(student: Student, trainings?: Student_training[])
    : boolean {
      let ret: boolean = false;
      if(isNullOrUndefined(student.trainings)) student.trainings=trainings;
      let rule: Student_training_compliant_status_rule 
          = new Student_training_compliant_status_rule();
      const isEmployed = Helper.hasEmployment(student);

      if(isEmployed || rule.hasTraining(student.trainings)) {
        if(rule.isTrainingNeedCredential(student)){
          if(((rule.isCredentialActive(student))
          || Helper.isGrandFathered(student))
          && !rule.isTrainingOverdue(student.trainings)) {
            ret = true;
          } else if(Helper.hasCredential(Helper.CE_EXEMPT_CREDENTIAL_CODES, student.credentials, Helper.NON_ACTIVE_CREDENTIAL_STATUSES)
            && isEmployed) {
              //is working
              //has a CE_EXEMPT_CREDENTIAL that is not active
              ret = true;
          } else if(isNullOrUndefined(student.credentials)
             && !Helper.isGrandFathered(student)) {
              if (Helper.isPendingDOHExam(student)
              && isEmployed){
                /* Compliant
                 * Employment status => Actively working
                 * Training status => Learners are actively working or compliant\
                 * with their training.  Waiting to take their credential
                 */
                ret = true;
              } else if(!rule.hasActiveCETraining(student.trainings)
                      && !rule.isTrainingOverdue(student.trainings)) {
                ret = true;
              }
          }
        } else {
          if(!rule.isTrainingOverdue(student.trainings)) {
            ret = true;
          }
        }    
      }
      console.log(`studentid: ${student.id}; isCompliant ${ret}`);
      return ret;
  }
  
  private hasTraining(trainings: Student_training[])
    : boolean {
      let ret: boolean = false;
      if(!isNullOrUndefined(trainings)
      &&(_.filter(trainings, 
          tr => tr.status === Constants.training_status.ACTIVE)
          .length > 0))
        ret = true;
      return ret;
  }
  /**
   * check if any active trainings with due_date before today 
   * and if benefit_continuation_due_date(bcdd) is available, today isAfter bcdd
   */
  private isTrainingOverdue(trainings: Student_training[])
    : boolean {
      let ret: boolean = false;
      if(!isNullOrUndefined(trainings)
        &&(_.filter(trainings, 
          tr => (tr.status === Constants.training_status.ACTIVE
                && tr.training_code !== Constants.training_code.OS.CODE //O&S no due date
                && (moment(tr.due_date).isBefore(moment().startOf('day')) 
                  && (isNullOrUndefined(tr.benefit_continuation_due_date) 
                      || moment().isAfter(tr.benefit_continuation_due_date)))))
          .length > 0))
        ret = true;
      return ret;
  }
  
  private isTrainingNeedCredential(student: Student)
    : boolean {
      let ret: boolean = false;
      if(_.includes([Constants.work_category.STANDARD_HCA,
                     Constants.work_category.DDD_STANDARD],
                     student.assigned_category)) {
                       ret = true;
                     }
      return ret;
  }
  
  private isCredentialActive(student: Student)
    : boolean {
      let ret: boolean = false;
      if(!isNullOrUndefined(student.credentials)
      &&(_.filter(student.credentials, 
          cred => (cred.status === Constants.credential_status.ACTIVE))
          .length > 0))
        ret = true;
      return ret;
  }
  
  private hasActiveCETraining(trainings: Student_training[])
    : boolean {
      let ret = false;
      let activeTrainings = _.filter(trainings, 
          tr => (tr.status === Constants.training_status.ACTIVE));
      if(!isNullOrUndefined(activeTrainings)) {
        if(_.some(activeTrainings, tr=>{
          return tr.training_code === Constants.training_code.CE_12.CODE;
        })) {
          ret = true;
        }
      }
      return ret;
  }
}