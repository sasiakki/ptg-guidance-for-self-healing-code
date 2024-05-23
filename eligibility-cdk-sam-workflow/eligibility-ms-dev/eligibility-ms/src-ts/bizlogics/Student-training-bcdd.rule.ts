import {
    Student,
    Student_training,
    Student_status_set
  } from '../models'
  import { Employment } from '../models/employment.model';
  import { isNullOrUndefined } from 'util';
  import { Constants } from './consts';
  import { Helper } from '../helpers/helper';
  import moment = require('moment');
  import * as _ from 'lodash';
  
  export class Student_training_bcdd_rule {
  
    constructor() {}
  
    public static processTrainingBcdd(student: Student, training?: Student_training)
      : Student_training {
        let rule = new Student_training_bcdd_rule();
        return rule.updateBCDD(training, student);
    }
  
    private updateBCDD(training: Student_training, student: Student)
      : Student_training {
        const isRehire = student.student_status_set.isRehire;
        let bcddTR: Student_training = training;
        let bcdd = null;
        let bcddReasonCode = null;

        switch (bcddTR.training_code) {
            case Constants.training_code.BT_7.CODE:
            case Constants.training_code.BT_9.CODE:
            case Constants.training_code.BT_30.CODE:
            case Constants.training_code.BT_42.CODE:
            case Constants.training_code.BT_70.CODE:
                /* only look up bcdd if not assigned OR isRehire (this trumps any manual or previous run value) */ 
                if (!bcddTR.benefit_continuation_due_date || isRehire){
                    // use rehire date for bcdd lookup
                    const btDate = (isRehire)
                        ? moment(student.employments[0].rehire_date).utc().startOf('day')
                        : moment(bcddTR.tracking_date).utc().startOf('day');
                    [bcdd, bcddReasonCode] = this.getBTBenefitContinuationDueDate(btDate.toDate(), isRehire);
                }
                break;
            case Constants.training_code.CE_12.CODE:
                [bcdd, bcddReasonCode] = this.getCEBenefitContinuationDueDate(moment(bcddTR.due_date).toDate(), isRehire);
                break;
            default:
                break;
        }

        // set training bcdd and reasonCode;
        if (bcdd) {
            bcddTR.benefit_continuation_due_date = moment(bcdd).toISOString();
            bcddTR.reason_code = bcddReasonCode;
        }
        return bcddTR;
    }

    /*
    BT Benefit Continuation Due Date Override
    BT TrackingDate --> bcdd
    08/17/2019 to 09/30/2020 --> 01/31/2023
    10/01/2020 to 04/30/2021 --> 04/30/2023
    05/01/2021 to 03/31/2022 --> 07/31/2023
    04/01/2022 to 09/30/2022 --> 10/31/2023
    10/01/2022 to 06/30/2023 --> 11/30/2023
    07/01/2023 and after --> Regular 120 days
    */
    private getBTBenefitContinuationDueDate(trackingDate: Date, isRehire: boolean): [ Date | null | undefined, string | null | undefined ] {
        const mTrackingDate = moment(trackingDate).utc().startOf('day');
        let bcdd = null;
        let dueDateExtension = null;
        let reasonCode = null;
        // setting the second value to 'day', checks day, month and year;
        if (mTrackingDate.isSameOrAfter(moment('2019-08-17'), 'day') && mTrackingDate.isSameOrBefore(moment('2020-09-30'), 'day')) {
            bcdd = moment('2023-01-31').utc().startOf('day');
        } else if (mTrackingDate.isSameOrAfter(moment('2020-10-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2021-04-30'), 'day')) {
            bcdd = moment('2023-04-30').utc().startOf('day');
        } else if (mTrackingDate.isSameOrAfter(moment('2021-05-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2022-03-31'), 'day')) {
            bcdd = moment('2023-07-31').utc().startOf('day');
        } else if (mTrackingDate.isSameOrAfter(moment('2022-04-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2022-09-30'), 'day')) {
            bcdd = moment('2023-10-31').utc().startOf('day');
        } else if (mTrackingDate.isSameOrAfter(moment('2022-10-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2023-06-30'), 'day')) {
            bcdd = moment('2023-11-30').utc().startOf('day');
        // special legislation rehire
        } else if (mTrackingDate.isSameOrAfter(moment('2023-07-01'), 'day') && isRehire === true){
            bcdd = mTrackingDate.add(Constants.BT_REHIRE_EXTENSION_DAYS,'day');
            reasonCode = Constants.bcdd_reason_code.HB1694_REHIRE;
        }

        if (bcdd) {
            dueDateExtension = bcdd.toDate();
            if (isRehire===false ) 
                reasonCode = Constants.bcdd_reason_code.COVID19; 
            else if (!reasonCode) 
                reasonCode = Constants.bcdd_reason_code.ER_REHIRE; //isRehire and reasonCode has not been set
        }
            return [dueDateExtension, reasonCode];
    }

    /*
    CE Benefit Continuation Due Date Override
    CE Due Date --> bcdd
    < 02/24/2023 --> 02/24/23
    */
    private getCEBenefitContinuationDueDate(dueDate: Date, isRehire: boolean): [ Date | null | undefined, string | null | undefined ] {
        const mDueDate = moment(dueDate).utc().startOf('day');
        let bcdd = null;
        let reasonCode = null; 
        if (mDueDate.isBefore(moment(Constants.CE_BCDD).utc().startOf('day'), 'day')) {
            bcdd = moment(moment(Constants.CE_BCDD).utc().startOf('day')).toDate();
            reasonCode = (isRehire) ? Constants.bcdd_reason_code.ER_REHIRE : Constants.bcdd_reason_code.COVID19;
        }
        return [bcdd, reasonCode];
    }

}
  