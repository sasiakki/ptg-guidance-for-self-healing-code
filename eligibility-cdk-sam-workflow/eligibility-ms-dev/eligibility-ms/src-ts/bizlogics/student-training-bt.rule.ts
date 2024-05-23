import { Student, Student_training } from '../models';
import { isNullOrUndefined } from 'util';
import { Constants } from './consts';
import * as _ from 'lodash';
import { Helper } from '../helpers/helper';
import moment = require('moment');

export class Student_training_bt_rule {
    constructor() { }

    public static isBtEligible(
        student: Student,
        trainings: Student_training[],
        courseCode: string
    ): string{
        let isEligible = false;
        const requiresEmployment = true;
        const isOSCompleted =  Helper.hasCompletedTraining(Constants.training_code.OS.CODE, trainings);
        const isBTCompleted =  Helper.hasCompletedTraining(courseCode, trainings);
        const isRenewableCredential = Helper.expiredCredentialIsRenewable(student);

        console.log(`studentid: ${student.id}; has completed ${Constants.training_code.OS.CODE} ${isOSCompleted}`)
        console.log(`studentid: ${student.id}; has completed ${courseCode} ${isBTCompleted}`)

        if (!Helper.studentValuesNullOrUndefined([
                    student.student_status_set,
                    trainings])
            && student.assigned_category !== Constants.work_category.ORIENTATION_SAFETY
            && !Helper.isExemptFromOSAndBTByCredential(student)
            && ( !isRenewableCredential || 
                    (isRenewableCredential && !_.includes([Constants.work_category.STANDARD_HCA, Constants.work_category.ADULT_CHILD], student.assigned_category)))// isrenewable and not SHCA or ADCH
            && isOSCompleted
            && (!isBTCompleted || (courseCode == Constants.training_code.BT_70.CODE 
                && (_.includes([Constants.work_category.STANDARD_HCA], student.assigned_category))
                && isNullOrUndefined(student.credentials)
                && !Helper.hasCompletedBT70Training(courseCode, student))) // MDL-479: if SHCA, no credential and completed either RFOC or MFOC (no other BT70 or equivalent) then eligible for BT70 training.
            ) {
            isEligible = true;
        }

        const ret = Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isBTEligible: ${isEligible}; eligibleTrainingStatus: ${ret}; courseCode: ${courseCode}`);
        return ret;
    }
}
