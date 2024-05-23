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
  
  export class Student_bt_rehire_rule {
  
    constructor() {}
  
    public static processTrainings(student: Student, btTrainings?: Student_training[])
      : Student_training[] {
        let rule = new Student_bt_rehire_rule();
        let invalidBtTrainings: Student_training[] = [];
        // only if you are rehire and rehire date is after min rehire dates otherwise no bcdd; 
        if (student.student_status_set.isRehire 
          && student.employments
          && moment(Constants.BT_REHIRE_MIN).utc().startOf('day').isSameOrBefore(moment(student.employments[0].rehire_date).utc().startOf('day'))){
          if (!isNullOrUndefined(btTrainings)){
            _.forEach(btTrainings, tr=>{
              // bts where active and before the min date and no bcdd
              if(_.includes(Helper.BT_CODES, tr.training_code)
                && tr.status === Constants.training_status.ACTIVE
                && isNullOrUndefined(tr.benefit_continuation_due_date) 
                && tr.tracking_date
                && moment(tr.tracking_date).utc().startOf('day').isBefore(moment(Constants.BT_REHIRE_MIN).utc().startOf('day'))) {
                //close 
                tr.status = Constants.training_status.CLOSED;
                invalidBtTrainings.push(tr);
              }
            });
          }
        }
        return invalidBtTrainings;
    } 
  }
  
