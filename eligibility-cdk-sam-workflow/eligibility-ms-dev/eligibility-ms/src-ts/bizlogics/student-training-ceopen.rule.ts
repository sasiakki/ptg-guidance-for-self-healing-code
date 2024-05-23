import { Student, Student_training } from '../models';
import { isNullOrUndefined } from 'util';
import * as _ from 'lodash';
import { Constants } from './consts';
import { Student_training_due_date_rule } from './student-training-due-date.rule';
import { Helper } from '../helpers/helper';

//Juhye.An, 2020.05.15
export class Student_training_ceopen_rule {
  constructor() {}

  /* 
  - Checks to see is the learner is eligible for Caregiver Learning Library
    Case 1: SHCA/ADCH && Compliant && ARNP,RN, or LPN Credentials => return true
    Case 2: Respite/LSP/DDPP/PPPP && Compliant 
      - If credential, return true
      - Else completed required training, return true
   */
  public static isOpenCEEligible(
    student: Student,
    trainings: Student_training[]
  ): boolean {
    console.log(`Start isOpenCEEligible ${ret}`);
    var ret: boolean = false;
    if (
      Helper.isInCompliance(student) &&
      Helper.hasEmployment(student) &&
      !Helper.studentValuesNullOrUndefined([
        student.assigned_category,
        student.student_status_set.complianceStatus,
      ])
    ) {
      if (
        (student.assigned_category == Constants.work_category.STANDARD_HCA ||
          student.assigned_category == Constants.work_category.ADULT_CHILD) &&
        !isNullOrUndefined(student.credentials) &&
        Helper.hasActiveCredential(
          [
            Constants.credential_type.ARNP.CODE,
            Constants.credential_type.RN.CODE,
            Constants.credential_type.LPN.CODE,
          ],
          student.credentials
        )
      ) {
        ret = true;
      }
    }
    if (
      student.assigned_category ==
        Constants.work_category.PARENT_PROVIDER_DDD ||
      student.assigned_category == Constants.work_category.DDD_NDDD ||
      student.assigned_category == Constants.work_category.RESPITE ||
      student.assigned_category ==
        Constants.work_category.LIMITED_SERVICE_PROVIDER
    ) {
      if (Helper.isExemptFromOSAndBTByCredential(student) === true) {
        ret = true;
      }
      else {
        if (
          Helper.hasTakenOSAndBT(
            Helper.determineBtType(student.assigned_category), 
            trainings
          ) === true
        ) {
          ret = true;
        }
      }
    }
    console.log(`End isOpenCEEligible ${ret}`);
    return ret;
  }

  /* 
    - Creates a new training to students who are eligible for CLL
    - Closes CLL if the student already has a training that's opened
    */
  public static createOrUpdateTraining(
    student: Student,
    trainings: Student_training[],
    status: boolean
  ): Student_training {
    let training: Student_training = null;
    // looks for the CE course in a list of trainings
    let CLLTrains = _.filter(trainings, {
      training_code: Constants.training_code.CE_OPEN_LIB.CODE,
    });
    // if training already exists, check the status
    // else create a new training
    if (CLLTrains.length > 0) {
      CLLTrains[0].status =
        status === true
          ? Constants.training_status.ACTIVE
          : Constants.training_status.CLOSED;
      training = CLLTrains[0];
    } else if (CLLTrains.length == 0 && status) {
      training = Student_training_due_date_rule.createNewTraining(
        student,
        Constants.training_code.CE_OPEN_LIB.CODE
      );
    }
    return training;
  }
}
