import {
  Student
} from '../models';
import { Helper } from '../helpers/helper';
import { Constants } from './consts';

export class Student_training_ahcas_rule {

  constructor() {

  }
  
  public static isAhcasEligible(student: Student) :  string {
    let isEligible = false;
    const requiresEmployment = false;
    let ret = Constants.eligible_training_status.CLOSE;
    if(!Helper.studentValuesNullOrUndefined([student.student_status_set])
        && student.student_status_set.ahcas_eligible) {
      isEligible = true;
    }
    ret = Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
    console.log(`studentid: ${student.id}; isAhcasEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
    return ret;
  }
}
