import {
    Student,
    Student_training
} from '../models'
import { Helper } from '../helpers/helper';
import { Constants } from './consts';
import { Student_training_bt_rule } from './student-training-bt.rule';

export class Student_training_refresher_rule {

    constructor() { }

    /**
     * A student is eligible for the Refresher course:
     * Compliant
     * SHCA working category 
     * Completed BT70 or equivalent
     * isPendingDOHExam: checks prior trainings, no student credentials and validates (work_category of SHCA || DDST)
     * and not exempt
     * 
     * COMMENT:  No CE open... implicit if isPendingDOHExam is true
     * Students can retake Refresher multiple times.
     * @param student 
     * @param trainings 
     */
    public static isRefresherEligible(student: Student,
        trainings: Student_training[])
        : string {
        let isEligible = false;
        
        const requiresEmployment = false;
        const validWorkerCategories: string[] = [Constants.work_category.STANDARD_HCA];
        if (validWorkerCategories.includes(student.assigned_category)
            && Helper.isPendingDOHExam(student)
            && Helper.hasCompletedTraining(Constants.training_code.BT_70.CODE, trainings)
            && !Helper.isGrandFathered(student)
			&& (Student_training_bt_rule.isBtEligible(student, trainings, Constants.training_code.BT_70.CODE) === Constants.eligible_training_status.CLOSE)) 
		{
            isEligible = true;
        }

        const ret = Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isRefresherEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
