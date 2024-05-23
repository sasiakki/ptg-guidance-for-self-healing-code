import { Student, Student_training } from '../models';
import { Constants } from './consts';
import { Helper } from '../helpers/helper';
import * as _ from 'lodash';

export class Student_training_os_rule {
  constructor() { }

  public static isOsEligible(
    student: Student,
    trainings: Student_training[]
  ): string{
    let isEligible = false;
    const requiresEmployment = true;
    const isRenewableCredential = Helper.expiredCredentialIsRenewable(student);

    if (!Helper.isExemptFromOSAndBTByCredential(student)
      && !Helper.hasCompletedTraining(Constants.training_code.OS.CODE ,student.trainings)
      && !(student.student_status_set.isCredentialExpired && student.assigned_category === Constants.work_category.ADULT_CHILD)  // not adch with expired credentials (doesn't matter length of expiration)
      && (!isRenewableCredential // expired renewable credential
            || (isRenewableCredential && !_.includes([Constants.work_category.STANDARD_HCA, Constants.work_category.ADULT_CHILD], student.assigned_category)))) // isrenewable and not SHCA or ADCH
    {
      isEligible = true;
    }

    const ret = Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
    console.log(`studentid: ${student.id}; isOSEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);

    return ret;
  }
}
