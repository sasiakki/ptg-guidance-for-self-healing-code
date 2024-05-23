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
import { Console } from 'console';
import { constants } from 'os';
  
  export class Student_ce_rehire_rule {
  
    constructor() {}
  
    public static processTrainings(student: Student, ceTrainings?: Student_training[])
      : Student_training[] {
        let invalidCETrainings: Student_training[] = [];
        // only if you are rehire and rehire date is after min rehire dates otherwise no bcdd; 
        if (student.student_status_set.isRehire 
          && student.employments
          && ((student.employments[0].training_category === Constants.work_category.ADULT_CHILD || student.student_status_set.isGrandFathered)
          || ((student.employments[0].training_category === Constants.work_category.STANDARD_HCA && student.credentials && student.credentials[0].status === Constants.credential_status.ACTIVE)))){
          if (!isNullOrUndefined(ceTrainings)){
            _.forEach(ceTrainings, tr=>{
              if( tr.training_code === Constants.training_code.CE_12.CODE
                && tr.status === Constants.training_status.ACTIVE ) {
                const dueDate = moment(tr.due_date).utc().startOf('day');
                const rehireYear = moment(student.employments[0].rehire_date).utc().startOf('day').year();
                const terminationDateYear = moment(student.employments[0].terminate_date).utc().startOf('day').year();
                //close non-work year CE
                if(dueDate.year() < rehireYear && dueDate.year() > terminationDateYear) {
                    //close 
                    tr.status = Constants.training_status.CLOSED;
                    invalidCETrainings.push(tr);
                }
              }
            });
          }
        }
        return invalidCETrainings;
    } 
  }
  
