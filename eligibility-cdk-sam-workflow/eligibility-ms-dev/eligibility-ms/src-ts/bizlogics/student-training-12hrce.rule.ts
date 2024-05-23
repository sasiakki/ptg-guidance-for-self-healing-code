import { 
    Student, 
    Student_training 
} from '../models';
import { isNullOrUndefined } from 'util';
import * as _ from 'lodash';
import { Constants } from './consts';
import { Student_training_due_date_rule } from './student-training-due-date.rule';
import { Helper } from '../helpers/helper';

// Juhye.An, 04/16/2020:
export class Student_training_12hrce_rule {
    constructor() { }

    /*
    - Checks to see if the learner is eligible for 12 hour CE
    */
    public static is12hrCEEligible( student: Student,
        trainings: Student_training[]
    ): string {
        let isEligible = false;
        let isGrandFathered = false;
        const requiresEmployment = true;

        //NOT requiring previous training credentials 
        const previousTrainingNotReqCredentials: string[] = [
            Constants.credential_type.NAC.CODE,
            Constants.credential_type.HCA.CODE,
            Constants.credential_type.OSPI.CODE //MDL-570: added OSPI credential
        ];

        const validCredentialStatuses: string[] = [
            Constants.credential_status.ACTIVE,
            Constants.credential_status.EXPIRED,
            Constants.credential_status.PENDING
        ]
        // requires the learner to be compliant, and be of SHCA or ADCH category
        if (Helper.hasCategory([Constants.work_category.STANDARD_HCA, Constants.work_category.ADULT_CHILD], student.assigned_category) //ONLY SHCA || ADCH are eligible
            && !Helper.hasActiveCredential(Helper.CE_EXEMPT_CREDENTIAL_CODES, student.credentials)) { //no active exempt student.credentials (AP, RN, LN)
            if (Helper.isGrandFathered(student)) {
                isEligible = true;
                isGrandFathered = true;
            } else if (student.assigned_category === Constants.work_category.ADULT_CHILD) { //explicitly calling out ADCH
                if (Helper.hasCredential(previousTrainingNotReqCredentials, student.credentials ,validCredentialStatuses)
                    || Helper.hasTakenOSAndBT(Constants.training_code.BT_30.CODE, trainings)) {
                    isEligible = true;
                }
            } else if (student.assigned_category === Constants.work_category.STANDARD_HCA //explicitly calling out SHCA
                && Helper.hasCredential(previousTrainingNotReqCredentials, student.credentials, validCredentialStatuses)) { //must have credentials
                if (student.credentials[0].status === Constants.credential_status.ACTIVE) { // active credential
                    isEligible = true;
                } else if (Helper.expiredCredentialIsRenewable(student)) { // expired <= 5 yrs ;
                    isEligible = true;
                }
            }
        }

        const ret = (isGrandFathered) 
            ? Constants.eligible_training_status.ACTIVATE 
            : Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);

        console.log(`studentid: ${student.id}; is12hrCEEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
