import {
  Student,
  Student_training
} from '../models'
import { isNullOrUndefined } from 'util';
import * as _ from 'lodash';

// Caregiver Best Practices
export class Student_training_cbp_rule {

  constructor() {

  }

  public static isCBPEligible(student: Student,
    trainings: Student_training[])
    : boolean {
    var ret: boolean = false;
    console.log(`Start isCBPEligible ${ret}`);
    /*
      Training Code: 301
      Display CBP Eligibility Card
      IF
      Student Status contains Compliant
      AND
      Active Training Requirement equals Continuing Education
      AND
      My Preferred Language Is? equals English
      AND
      Student has not taken course name “HCA Best Practices in Infection Control and Blood Borne Pathogens SEIU 775 UT”
    */
    if (!isNullOrUndefined(student.student_status_set)) {
      console.log(`student.student_status_set.complianceStatus ${student.student_status_set.complianceStatus}`);
    }
    console.log(`student.active_training ${student.active_training}`);
    if (!isNullOrUndefined(student.student_status_set)
      && !isNullOrUndefined(student.student_status_set.complianceStatus)) {
      if ((student.student_status_set.complianceStatus === 'Compliant')
        && (!isNullOrUndefined(student.active_training)
          && student.active_training === 'Continuing Education')
        && (!isNullOrUndefined(student.prefer_language)
          && student.prefer_language === 'English')
        && !isNullOrUndefined(student.course_completions)) {
        var number = _.filter(_.uniqBy(student.course_completions, 'name'), function (val, key, obj) {

          return val.name === 'HCA Best Practices in Infection Control and Blood Borne Pathogens SEIU 775 UT';

        });
        if (number.length === 0) ret = true;
      }
    }

    console.log(`End isCBPEligible ${ret}`);
    return ret;
  }
}
