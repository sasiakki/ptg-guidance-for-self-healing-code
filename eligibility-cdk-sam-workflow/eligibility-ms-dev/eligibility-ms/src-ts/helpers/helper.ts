import { Student, Student_training, Credential, Student_status_set } from '../models';
import { isNullOrUndefined } from 'util';
import { 
    Constants,
    Student_training_compliant_status_rule,
    Student_training_due_date_rule,
    Student_credential_rule,
    Student_training_bcdd_rule,
    Student_bt_rehire_rule,
    Student_ce_rehire_rule
} from './../bizlogics';
import * as _ from 'lodash';
import moment = require('moment');

export class Helper {
    public static get BT_CODES(): string[] {
        return [
            Constants.training_code.BT_7.CODE,
            Constants.training_code.BT_9.CODE,
            Constants.training_code.BT_30.CODE,
            Constants.training_code.BT_70.CODE,
            Constants.training_code.EXEMPT_BT70.CODE
        ]
    };

    //waived credentials from CE
    public static get CE_EXEMPT_CREDENTIAL_CODES(): string[] {
        return [
            Constants.credential_type.ARNP.CODE,
            Constants.credential_type.RN.CODE,
            Constants.credential_type.LPN.CODE
        ]
    };

    public static get NON_ACTIVE_CREDENTIAL_STATUSES(): string[]{
        return [
            Constants.credential_status.CLOSED,
            Constants.credential_status.EXPIRED,
            Constants.credential_status.NEGATIVE,
            Constants.credential_status.PENDING,
        ]
    }

    // Checks to see if credentials contain any of the credentials in any of the statuses provided
    // by default, checks against list of validcredentials: default being Active
    public static hasCredential(credentialCodes: string[],
        credentials: Credential[],
        validCredentialStatuses: string[]) {
        let ret = false;
        if (!isNullOrUndefined(credentials)) {
            if (_.some(credentials, tr => {
                return (credentialCodes.includes(tr.name)
                    && validCredentialStatuses.includes(tr.status));
            })) {
                ret = true;
            }
        }
        return ret;
    };

    // Checks to see if credentials contain any of the credentials in any of the statuses provided
    // by default, checks against ACTIVE only if a list of validCredentials is not provided
    public static hasActiveCredential(credentialCodes: string[],
        credentials: Credential[],
    ) {
        return this.hasCredential(credentialCodes, credentials, [Constants.credential_status.ACTIVE])
    };

    //check credential is expired or pending with a expiration date
    public static isCredentialExpired(credential: Credential) :boolean{
        return (credential && credential.status === Constants.credential_status.EXPIRED 
            || (credential.status === Constants.credential_status.PENDING && credential.expiration_date.length > 1));
    }

    //check if expired credential is renewable; set in constants file
    public static expiredCredentialIsRenewable(student: Student)
      : boolean {
        return (student.student_status_set.isCredentialExpired
            && moment(student.credentials[0].expiration_date).add(Constants.EXPIRED_CREDENTIAL_ISRENEABLE_TIMELIMIT, 'year').isSameOrAfter(moment().startOf('day')))
    }

    // Takes in array of categories to check
    public static hasCategory(categories: String[], category: string) {
        if (!isNullOrUndefined(category)) {
            if (categories.includes(category)) {
                return true;
            }
        }
        return false;
    };

    // Checks if student has employment status that might exempt from training
    public static hasEmployment(student: Student) {
        if (!isNullOrUndefined(student.num_active_emp)
            && student.num_active_emp > 0 ) {
                return true;
        }
        return false;
    };

    // Validates that student is compliant for training purposes
    public static isInCompliance(student: Student) {
        if (!isNullOrUndefined(student.student_status_set) 
            && student.student_status_set.complianceStatus === Constants.compliant_status.COMPLIANT) {
            return true;
        }
        return false;
    };

    // Takes in array of trainings and sets status to 'closed'
    public static closeAllOpenTrainings(trainings: Student_training[]) {
        if(!isNullOrUndefined(trainings)) {
            for (let training of trainings) {
                training.status = Constants.training_status.CLOSED;
            }
        }
        return trainings;
    }

    public static isGrandFathered(student: Student) {
        if (!isNullOrUndefined(student.student_status_set.isGrandFathered) 
            && student.student_status_set.isGrandFathered) {
            return true;
        }
        return false;
    }

    public static determineBtType(
        trainingCategory: string
    ): string {
        switch (trainingCategory) {
            case Constants.work_category.STANDARD_HCA:
                return Constants.training_code.BT_70.CODE;
            case Constants.work_category.PARENT_PROVIDER_DDD:
                return Constants.training_code.BT_7.CODE
            case Constants.work_category.ADULT_CHILD:
                return Constants.training_code.BT_30.CODE;
            case Constants.work_category.LIMITED_SERVICE_PROVIDER:
                return Constants.training_code.BT_30.CODE;
            case Constants.work_category.DDD_NDDD:
                return Constants.training_code.BT_30.CODE;
            case Constants.work_category.PARENT_NON_DDD:
                return Constants.training_code.BT_30.CODE;
            case Constants.work_category.FAMILY_CARE_PROVIDER:
                return Constants.training_code.BT_30.CODE;
            case Constants.work_category.RESPITE:
                return Constants.training_code.BT_9.CODE;
            default:
                return undefined;
        }
    }
    //returns true if training array contains both OS AND BT trainings with COMPLETD status
    public static hasTakenOSAndBT(btCode: string, trainings: Student_training[]) {
        const requiredTrainings: string[] = [
            Constants.training_code.OS.CODE,
            btCode
        ]
        if(this.hasCompletedTrainings(requiredTrainings, trainings)) {
            return true;
        }
        return false;
    }
    
    public static hasCompletedTraining(trainingCode: string, trainings: Student_training[]) {
        if(!isNullOrUndefined(trainings)) {
            for (const training of trainings) {
                if (trainingCode === training.training_code 
                    && (this.trainingIsClosedByComplete(training))) {
                    return true
                }
            }
            if(this.hasCompletedHigherOrEquTraining(trainings, trainingCode)) {
                return true
            }
        }
        return false;
    }

    // Takes in array of training codes to check
    public static hasCompletedTrainings(trainingCodes: string[], trainings: Student_training[]) {
        if(!isNullOrUndefined(trainingCodes)) {
            for (const trainingCode of trainingCodes) {
                if (!this.hasCompletedTraining(trainingCode, trainings)){
                    return false;
                }
            }
        }
        return true;
    };

    public static trainingIsClosed(training: Student_training) {
        if (training.status === Constants.training_status.CLOSED
            && isNullOrUndefined(training.archived)) {
            return true;
        }
        return false;
    }
    
    public static trainingIsClosedByComplete(training: Student_training) {
        if (training.status === Constants.training_status.CLOSED 
        && !isNullOrUndefined(training.completed_date)
        && isNullOrUndefined(training.archived)) {
            return true;
        }
        return false;
    }

    /**
     * 
     * @param student 
     * 
     * Students can be exempted from OS and BT when they have credential. This method
     * takes in a student object and validates whether or not they qualify for exemption.
     * Qualifying credentials are HCA, NAC, OSPI or employment
     */
    public static isExemptFromOSAndBTByCredential(student: Student) {
        const qualifyingCredentials: string[] = [
            Constants.credential_type.ARNP.CODE,
            Constants.credential_type.LPN.CODE,
            Constants.credential_type.RN.CODE,
            Constants.credential_type.HCA.CODE,
            Constants.credential_type.NAC.CODE,
            Constants.credential_type.OSPI.CODE  //added OSPI credential as the part of MDL-570
        ]
        if (
            this.hasActiveCredential(qualifyingCredentials, student.credentials)
            ||
            this.isGrandFathered(student)
        ) {
            return true;
        }
        return false;
    }

    public static studentValuesNullOrUndefined(values: any[]) {
        if(!isNullOrUndefined(values)){
            for (const value of values) {
                if (isNullOrUndefined(value)) {
                    return true;
                }
            }
        }
        return false;
    }

    public static validateStudentObject(student: Student, trainings: Student_training[])
        : [Student_status_set, Student_training[], Student_training[]] {
        let ss: Student_status_set = new Student_status_set();
        let validTrainings: Student_training[] = trainings ?? [];
        let permanentTrainingUpdates: Student_training[] = [];

        if (!isNullOrUndefined(student.student_status_set)) {
            ss = student.student_status_set;
        }
        Object.assign(ss, { studentId: student.id, learnerId: student.id });

        if(!isNullOrUndefined(student.credentials) && student.credentials.length > 0) {
            [ss, validTrainings, permanentTrainingUpdates] = Student_credential_rule.processExistingTrainings(student, trainings);
        }

        ss.isCompliant = Student_training_compliant_status_rule
            .isCompliant(student, validTrainings);
        ss.complianceStatus = ss.isCompliant
            ? Constants.compliant_status.COMPLIANT
            : Constants.compliant_status.NONCOMPLIANT;

        student.student_status_set = ss;
        return [ss, validTrainings, permanentTrainingUpdates];
    }
    
    public static bcddExistingTraining(stu: Student, tr: Student_training)
        : Student_training | null {
        const curBCDD = isNullOrUndefined(tr.benefit_continuation_due_date)? '' : tr.benefit_continuation_due_date;
        if(tr.is_required) {
            const processedTR: Student_training = Student_training_bcdd_rule.processTrainingBcdd(stu, tr);
            const newBCDD = isNullOrUndefined(processedTR.benefit_continuation_due_date)? '' : processedTR.benefit_continuation_due_date;
            console.log(`studentid: ${stu.id}; curBCDD is ${curBCDD}, newBCDD is ${newBCDD}`);
            if(curBCDD !== newBCDD) {
                return processedTR;
            }
        }
        return null;
    }
    
    public static createOrUpdateTraining(student: Student, training_code: string, status: string)
        : Student_training[] {
        let trainings: Student_training[] = [];
        const sameActiveTrainings = _.filter(student.trainings,
            tr => (tr.status === Constants.training_status.ACTIVE
                && tr.training_code === training_code));
        let hasSameActiveTraining = (!isNullOrUndefined(sameActiveTrainings)
            && sameActiveTrainings.length > 0)
            ? true
            : false;

        //BT ONLY; 
        //close out all other active btCode trainings (train up or train down)
        if(Helper.hasCategory(Helper.BT_CODES, training_code)){
            //close any btTrainings that are not the current_code;
            const otherBtTrainings: Student_training[] = Helper.getActiveBTTrainings(student.trainings, [training_code]);
            if (!isNullOrUndefined(otherBtTrainings) && otherBtTrainings.length > 0)
                trainings.push(...Helper.closeAllOpenTrainings(otherBtTrainings));

            // evaluation bt trackingdate
            // close and activate a new one
            if (hasSameActiveTraining && student.student_status_set.isRehire) {
                let invalidBts: Student_training[] = [];
                invalidBts = Student_bt_rehire_rule.processTrainings(student, sameActiveTrainings);
                if(invalidBts.length > 0 ) {
                    trainings.push(...invalidBts);
                    hasSameActiveTraining = false;
                    // only activate if activate or remain_open is set
                    if (_.includes([Constants.eligible_training_status.ACTIVATE,Constants.eligible_training_status.REMAIN_OPEN],
                        status)) {
                        status = Constants.eligible_training_status.ACTIVATE;
                    }
                }
            }
        }

        // CE - Rehire, work year CE only
        if( training_code === Constants.training_code.CE_12.CODE
            && sameActiveTrainings
            &&  student.student_status_set.isRehire) {
            let invalidCEs: Student_training[] = [];
            invalidCEs = Student_ce_rehire_rule.processTrainings(student, sameActiveTrainings);
            if(invalidCEs.length > 0 ) {
                trainings.push(...invalidCEs);
                hasSameActiveTraining = false;
                // only activate if activate or remain_open is set
                if (_.includes([Constants.eligible_training_status.ACTIVATE,Constants.eligible_training_status.REMAIN_OPEN],
                    status)) {
                    status = Constants.eligible_training_status.ACTIVATE;
                }
            }
        }

        let activeTR : Student_training = null;
        let processedTR : Student_training = null;
        switch (status) {
            case Constants.eligible_training_status.ACTIVATE:
                if(!hasSameActiveTraining) {
                    activeTR = Student_training_due_date_rule.createNewTraining(student, training_code);
                    processedTR = Helper.bcddExistingTraining(student, activeTR);
                    if(!isNullOrUndefined(processedTR)) {
                        trainings.push(processedTR);
                    } else { trainings.push(activeTR); }
                }
                else {
                    if(!isNullOrUndefined(sameActiveTrainings[0])){
                        activeTR = sameActiveTrainings[0];
                        processedTR = Helper.bcddExistingTraining(student, activeTR);
                        if(!isNullOrUndefined(processedTR)) trainings.push(processedTR);
                    }
                }
                break;
            case Constants.eligible_training_status.REMAIN_OPEN: // NON-COMPLIANT || NO EMPLOYMENT 
                    //do nothing; keep active training open, but don't create a new one
                    activeTR = sameActiveTrainings[0];
                    if(!isNullOrUndefined(activeTR)) {
                        processedTR = Helper.bcddExistingTraining(student, activeTR);
                        if(!isNullOrUndefined(processedTR)) trainings.push(processedTR);
                    }
                break;
            case Constants.eligible_training_status.CLOSE:
                if(hasSameActiveTraining)
                    trainings.push(...Helper.closeAllOpenTrainings(sameActiveTrainings));
                break;
            default:
                break;
        }
        return (trainings.length > 0) ? trainings : null;
    }

    public static mergeTrainings(trainings: Student_training[], history: Student_training[])
        : Student_training[] {
        return _.concat(trainings, _.differenceBy(history, trainings, 'id'));
    }

    /**
     * get BT trainings that are not in the list of exclusionCodes
     * @param trainings 
     * @param exclusionCodes 
     */
    public static getActiveBTTrainings(trainings: Student_training[], exclusionCodes: String[] = [])
        : Student_training[] {
        //remove exclusion codes
        let btCodes = this.BT_CODES.filter(bt => {
            if (!_.includes(exclusionCodes, bt))
                return bt;
        });

        let activeTrainings: Student_training[] = [];
        if (!isNullOrUndefined(trainings) && trainings.length > 0) {
            activeTrainings = trainings.filter(tr => {
                if (_.includes(btCodes, tr.training_code)
                    && tr.status === Constants.training_status.ACTIVE
                    && isNullOrUndefined(tr.archived))
                    return tr;
            });
        }
        return activeTrainings;
    }

    /**
     * TP 11/30/2020: pulled from compliant-status.rule, leaving all requirements to
     * have backwards compatibility
     *
     * checks that user is in SHCA || DDST 
     * and no student credentials
     * and most recent completed training is BT_70 || BT_42
     * @param student 
     */
     public static isPendingDOHExam(student: Student)
        : boolean {
        let ret: boolean = false;
        if (_.includes([Constants.work_category.STANDARD_HCA, Constants.work_category.DDD_STANDARD], student.assigned_category)
                && isNullOrUndefined(student.credentials)) {
                if (!isNullOrUndefined(student.trainings)) {
                    let completedTrainings = _.filter(student.trainings, tr => (tr.status === Constants.training_status.CLOSED
                                                                                && isNullOrUndefined(tr.archived)));
                    if (!isNullOrUndefined(completedTrainings) && completedTrainings.length > 0) {
                        let sorted = _.sortBy(completedTrainings, 'completed_date').reverse();
                        ret = (_.includes([Constants.training_code.BT_42.CODE, Constants.training_code.BT_70.CODE], _.head(sorted).training_code))
                        || (Helper.hasCompletedHigherOrEquTraining(student.trainings, Constants.training_code.BT_70.CODE))
                        || (Helper.hasCompletedHigherOrEquTraining(student.trainings, Constants.training_code.BT_42.CODE));
                }
            }
        }
        return ret;
    }

    public static setEligibleTrainingStatus(student: Student, isEligible: boolean, requiresEmployment: boolean){
        let ret: string;
        if(isEligible) {
            if ((Helper.isInCompliance(student) && (!requiresEmployment || Helper.hasEmployment(student)))
            || student.student_status_set.isCredentialExpired)
                ret = Constants.eligible_training_status.ACTIVATE;
            else
                ret = Constants.eligible_training_status.REMAIN_OPEN;
        }
        else
            ret = Constants.eligible_training_status.CLOSE; // not eligible
        return ret;
    }

    public static completedHigherOrEquTrainings(trainings: Student_training[], training_code: string)
        : Student_training[] {
        let reqTrainings: Student_training[] = [];
        const higher_equ_trainings = _.filter(Constants.higher_equ_training_map, {'CODE': training_code})
        if(!isNullOrUndefined(higher_equ_trainings) && higher_equ_trainings.length > 0) {
            reqTrainings = _.filter(trainings,
                tr => (tr.status === Constants.training_status.CLOSED
                    && !isNullOrUndefined(tr.completed_date)
                    && isNullOrUndefined(tr.archived)
                    && _.includes(higher_equ_trainings[0].HIGHER_EQU_TRAINING, tr.training_code)));
        }
        return reqTrainings;
    }

    public static hasCompletedHigherOrEquTraining(trainings: Student_training[], training_code: string)
        : boolean {
        let ret = false;
        const reqTrainings = Helper.completedHigherOrEquTrainings(trainings, training_code);
        ret = (!isNullOrUndefined(reqTrainings)
                && reqTrainings.length > 0)
                ? true
                : false;
        return ret;
    }
    /* 
        * Get the credential data for the provided credential type
    */
    public static getCredentialByType(student: Student, cred_type: string) : Credential {
        if (!isNullOrUndefined(student.credentials)) {
            let credType: Credential = student.credentials
              .filter
              (
                c => c.name == cred_type
              )[0];
             return credType;
        }
    }


    /*
        MDL-479: check if the caregiver has completed BT70 or equivalent training except RFOC (911) & MFOC (912)
    */
    public static hasCompletedBT70Training(trainingCode: string, student: Student) {
        if (!isNullOrUndefined(student.trainings)) {
            const higher_equ_trainings = _.filter(Constants.higher_equ_training_map, {'CODE': trainingCode});
            let completedTrainings = _.filter(student.trainings, tr => (tr.status === Constants.training_status.CLOSED
                                                                            && isNullOrUndefined(tr.archived) && _.includes(higher_equ_trainings[0].HIGHER_EQU_TRAINING, tr.training_code)
                                                                            && !isNullOrUndefined(tr.completed_date)));
            if (!isNullOrUndefined(completedTrainings) && completedTrainings.length > 0) {
                for (let training of completedTrainings) {
                    if ( _.includes([Constants.training_code.BT_70.CODE, Constants.training_code.BT_42.CODE, Constants.training_code.EXEMPT_BT70.CODE], training.training_code)) {
                        return true;
                }
              }
            }
        }
        return false;
    }

    // check if a training is a specific code;
    public static isSpecificTraining(training: Student_training, expectedTraining: string): boolean {
        let ret = false;
        if (training?.training_code) {
            ret = _.includes([expectedTraining], training.training_code);
        }
        return ret;
    }
}
