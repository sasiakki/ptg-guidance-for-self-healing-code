"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Helper = void 0;
const models_1 = require("../models");
const util_1 = require("util");
const bizlogics_1 = require("./../bizlogics");
const _ = __importStar(require("lodash"));
const moment = require("moment");
class Helper {
    static get BT_CODES() {
        return [
            bizlogics_1.Constants.training_code.BT_7.CODE,
            bizlogics_1.Constants.training_code.BT_9.CODE,
            bizlogics_1.Constants.training_code.BT_30.CODE,
            bizlogics_1.Constants.training_code.BT_70.CODE,
            bizlogics_1.Constants.training_code.EXEMPT_BT70.CODE
        ];
    }
    ;
    static get CE_EXEMPT_CREDENTIAL_CODES() {
        return [
            bizlogics_1.Constants.credential_type.ARNP.CODE,
            bizlogics_1.Constants.credential_type.RN.CODE,
            bizlogics_1.Constants.credential_type.LPN.CODE
        ];
    }
    ;
    static get NON_ACTIVE_CREDENTIAL_STATUSES() {
        return [
            bizlogics_1.Constants.credential_status.CLOSED,
            bizlogics_1.Constants.credential_status.EXPIRED,
            bizlogics_1.Constants.credential_status.NEGATIVE,
            bizlogics_1.Constants.credential_status.PENDING,
        ];
    }
    static hasCredential(credentialCodes, credentials, validCredentialStatuses) {
        let ret = false;
        if (!(0, util_1.isNullOrUndefined)(credentials)) {
            if (_.some(credentials, tr => {
                return (credentialCodes.includes(tr.name)
                    && validCredentialStatuses.includes(tr.status));
            })) {
                ret = true;
            }
        }
        return ret;
    }
    ;
    static hasActiveCredential(credentialCodes, credentials) {
        return this.hasCredential(credentialCodes, credentials, [bizlogics_1.Constants.credential_status.ACTIVE]);
    }
    ;
    static isCredentialExpired(credential) {
        return (credential && credential.status === bizlogics_1.Constants.credential_status.EXPIRED
            || (credential.status === bizlogics_1.Constants.credential_status.PENDING && credential.expiration_date.length > 1));
    }
    static expiredCredentialIsRenewable(student) {
        return (student.student_status_set.isCredentialExpired
            && moment(student.credentials[0].expiration_date).add(bizlogics_1.Constants.EXPIRED_CREDENTIAL_ISRENEABLE_TIMELIMIT, 'year').isSameOrAfter(moment().startOf('day')));
    }
    static hasCategory(categories, category) {
        if (!(0, util_1.isNullOrUndefined)(category)) {
            if (categories.includes(category)) {
                return true;
            }
        }
        return false;
    }
    ;
    static hasEmployment(student) {
        if (!(0, util_1.isNullOrUndefined)(student.num_active_emp)
            && student.num_active_emp > 0) {
            return true;
        }
        return false;
    }
    ;
    static isInCompliance(student) {
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set)
            && student.student_status_set.complianceStatus === bizlogics_1.Constants.compliant_status.COMPLIANT) {
            return true;
        }
        return false;
    }
    ;
    static closeAllOpenTrainings(trainings) {
        if (!(0, util_1.isNullOrUndefined)(trainings)) {
            for (let training of trainings) {
                training.status = bizlogics_1.Constants.training_status.CLOSED;
            }
        }
        return trainings;
    }
    static isGrandFathered(student) {
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set.isGrandFathered)
            && student.student_status_set.isGrandFathered) {
            return true;
        }
        return false;
    }
    static determineBtType(trainingCategory) {
        switch (trainingCategory) {
            case bizlogics_1.Constants.work_category.STANDARD_HCA:
                return bizlogics_1.Constants.training_code.BT_70.CODE;
            case bizlogics_1.Constants.work_category.PARENT_PROVIDER_DDD:
                return bizlogics_1.Constants.training_code.BT_7.CODE;
            case bizlogics_1.Constants.work_category.ADULT_CHILD:
                return bizlogics_1.Constants.training_code.BT_30.CODE;
            case bizlogics_1.Constants.work_category.LIMITED_SERVICE_PROVIDER:
                return bizlogics_1.Constants.training_code.BT_30.CODE;
            case bizlogics_1.Constants.work_category.DDD_NDDD:
                return bizlogics_1.Constants.training_code.BT_30.CODE;
            case bizlogics_1.Constants.work_category.PARENT_NON_DDD:
                return bizlogics_1.Constants.training_code.BT_30.CODE;
            case bizlogics_1.Constants.work_category.FAMILY_CARE_PROVIDER:
                return bizlogics_1.Constants.training_code.BT_30.CODE;
            case bizlogics_1.Constants.work_category.RESPITE:
                return bizlogics_1.Constants.training_code.BT_9.CODE;
            default:
                return undefined;
        }
    }
    static hasTakenOSAndBT(btCode, trainings) {
        const requiredTrainings = [
            bizlogics_1.Constants.training_code.OS.CODE,
            btCode
        ];
        if (this.hasCompletedTrainings(requiredTrainings, trainings)) {
            return true;
        }
        return false;
    }
    static hasCompletedTraining(trainingCode, trainings) {
        if (!(0, util_1.isNullOrUndefined)(trainings)) {
            for (const training of trainings) {
                if (trainingCode === training.training_code
                    && (this.trainingIsClosedByComplete(training))) {
                    return true;
                }
            }
            if (this.hasCompletedHigherOrEquTraining(trainings, trainingCode)) {
                return true;
            }
        }
        return false;
    }
    static hasCompletedTrainings(trainingCodes, trainings) {
        if (!(0, util_1.isNullOrUndefined)(trainingCodes)) {
            for (const trainingCode of trainingCodes) {
                if (!this.hasCompletedTraining(trainingCode, trainings)) {
                    return false;
                }
            }
        }
        return true;
    }
    ;
    static trainingIsClosed(training) {
        if (training.status === bizlogics_1.Constants.training_status.CLOSED
            && (0, util_1.isNullOrUndefined)(training.archived)) {
            return true;
        }
        return false;
    }
    static trainingIsClosedByComplete(training) {
        if (training.status === bizlogics_1.Constants.training_status.CLOSED
            && !(0, util_1.isNullOrUndefined)(training.completed_date)
            && (0, util_1.isNullOrUndefined)(training.archived)) {
            return true;
        }
        return false;
    }
    static isExemptFromOSAndBTByCredential(student) {
        const qualifyingCredentials = [
            bizlogics_1.Constants.credential_type.ARNP.CODE,
            bizlogics_1.Constants.credential_type.LPN.CODE,
            bizlogics_1.Constants.credential_type.RN.CODE,
            bizlogics_1.Constants.credential_type.HCA.CODE,
            bizlogics_1.Constants.credential_type.NAC.CODE,
            bizlogics_1.Constants.credential_type.OSPI.CODE
        ];
        if (this.hasActiveCredential(qualifyingCredentials, student.credentials)
            ||
                this.isGrandFathered(student)) {
            return true;
        }
        return false;
    }
    static studentValuesNullOrUndefined(values) {
        if (!(0, util_1.isNullOrUndefined)(values)) {
            for (const value of values) {
                if ((0, util_1.isNullOrUndefined)(value)) {
                    return true;
                }
            }
        }
        return false;
    }
    static validateStudentObject(student, trainings) {
        let ss = new models_1.Student_status_set();
        let validTrainings = trainings !== null && trainings !== void 0 ? trainings : [];
        let permanentTrainingUpdates = [];
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set)) {
            ss = student.student_status_set;
        }
        Object.assign(ss, { studentId: student.id, learnerId: student.id });
        if (!(0, util_1.isNullOrUndefined)(student.credentials) && student.credentials.length > 0) {
            [ss, validTrainings, permanentTrainingUpdates] = bizlogics_1.Student_credential_rule.processExistingTrainings(student, trainings);
        }
        ss.isCompliant = bizlogics_1.Student_training_compliant_status_rule
            .isCompliant(student, validTrainings);
        ss.complianceStatus = ss.isCompliant
            ? bizlogics_1.Constants.compliant_status.COMPLIANT
            : bizlogics_1.Constants.compliant_status.NONCOMPLIANT;
        student.student_status_set = ss;
        return [ss, validTrainings, permanentTrainingUpdates];
    }
    static bcddExistingTraining(stu, tr) {
        const curBCDD = (0, util_1.isNullOrUndefined)(tr.benefit_continuation_due_date) ? '' : tr.benefit_continuation_due_date;
        if (tr.is_required) {
            const processedTR = bizlogics_1.Student_training_bcdd_rule.processTrainingBcdd(stu, tr);
            const newBCDD = (0, util_1.isNullOrUndefined)(processedTR.benefit_continuation_due_date) ? '' : processedTR.benefit_continuation_due_date;
            console.log(`studentid: ${stu.id}; curBCDD is ${curBCDD}, newBCDD is ${newBCDD}`);
            if (curBCDD !== newBCDD) {
                return processedTR;
            }
        }
        return null;
    }
    static createOrUpdateTraining(student, training_code, status) {
        let trainings = [];
        const sameActiveTrainings = _.filter(student.trainings, tr => (tr.status === bizlogics_1.Constants.training_status.ACTIVE
            && tr.training_code === training_code));
        let hasSameActiveTraining = (!(0, util_1.isNullOrUndefined)(sameActiveTrainings)
            && sameActiveTrainings.length > 0)
            ? true
            : false;
        if (Helper.hasCategory(Helper.BT_CODES, training_code)) {
            const otherBtTrainings = Helper.getActiveBTTrainings(student.trainings, [training_code]);
            if (!(0, util_1.isNullOrUndefined)(otherBtTrainings) && otherBtTrainings.length > 0)
                trainings.push(...Helper.closeAllOpenTrainings(otherBtTrainings));
            if (hasSameActiveTraining && student.student_status_set.isRehire) {
                let invalidBts = [];
                invalidBts = bizlogics_1.Student_bt_rehire_rule.processTrainings(student, sameActiveTrainings);
                if (invalidBts.length > 0) {
                    trainings.push(...invalidBts);
                    hasSameActiveTraining = false;
                    if (_.includes([bizlogics_1.Constants.eligible_training_status.ACTIVATE, bizlogics_1.Constants.eligible_training_status.REMAIN_OPEN], status)) {
                        status = bizlogics_1.Constants.eligible_training_status.ACTIVATE;
                    }
                }
            }
        }
        if (training_code === bizlogics_1.Constants.training_code.CE_12.CODE
            && sameActiveTrainings
            && student.student_status_set.isRehire) {
            let invalidCEs = [];
            invalidCEs = bizlogics_1.Student_ce_rehire_rule.processTrainings(student, sameActiveTrainings);
            if (invalidCEs.length > 0) {
                trainings.push(...invalidCEs);
                hasSameActiveTraining = false;
                if (_.includes([bizlogics_1.Constants.eligible_training_status.ACTIVATE, bizlogics_1.Constants.eligible_training_status.REMAIN_OPEN], status)) {
                    status = bizlogics_1.Constants.eligible_training_status.ACTIVATE;
                }
            }
        }
        let activeTR = null;
        let processedTR = null;
        switch (status) {
            case bizlogics_1.Constants.eligible_training_status.ACTIVATE:
                if (!hasSameActiveTraining) {
                    activeTR = bizlogics_1.Student_training_due_date_rule.createNewTraining(student, training_code);
                    processedTR = Helper.bcddExistingTraining(student, activeTR);
                    if (!(0, util_1.isNullOrUndefined)(processedTR)) {
                        trainings.push(processedTR);
                    }
                    else {
                        trainings.push(activeTR);
                    }
                }
                else {
                    if (!(0, util_1.isNullOrUndefined)(sameActiveTrainings[0])) {
                        activeTR = sameActiveTrainings[0];
                        processedTR = Helper.bcddExistingTraining(student, activeTR);
                        if (!(0, util_1.isNullOrUndefined)(processedTR))
                            trainings.push(processedTR);
                    }
                }
                break;
            case bizlogics_1.Constants.eligible_training_status.REMAIN_OPEN:
                activeTR = sameActiveTrainings[0];
                if (!(0, util_1.isNullOrUndefined)(activeTR)) {
                    processedTR = Helper.bcddExistingTraining(student, activeTR);
                    if (!(0, util_1.isNullOrUndefined)(processedTR))
                        trainings.push(processedTR);
                }
                break;
            case bizlogics_1.Constants.eligible_training_status.CLOSE:
                if (hasSameActiveTraining)
                    trainings.push(...Helper.closeAllOpenTrainings(sameActiveTrainings));
                break;
            default:
                break;
        }
        return (trainings.length > 0) ? trainings : null;
    }
    static mergeTrainings(trainings, history) {
        return _.concat(trainings, _.differenceBy(history, trainings, 'id'));
    }
    static getActiveBTTrainings(trainings, exclusionCodes = []) {
        let btCodes = this.BT_CODES.filter(bt => {
            if (!_.includes(exclusionCodes, bt))
                return bt;
        });
        let activeTrainings = [];
        if (!(0, util_1.isNullOrUndefined)(trainings) && trainings.length > 0) {
            activeTrainings = trainings.filter(tr => {
                if (_.includes(btCodes, tr.training_code)
                    && tr.status === bizlogics_1.Constants.training_status.ACTIVE
                    && (0, util_1.isNullOrUndefined)(tr.archived))
                    return tr;
            });
        }
        return activeTrainings;
    }
    static isPendingDOHExam(student) {
        let ret = false;
        if (_.includes([bizlogics_1.Constants.work_category.STANDARD_HCA, bizlogics_1.Constants.work_category.DDD_STANDARD], student.assigned_category)
            && (0, util_1.isNullOrUndefined)(student.credentials)) {
            if (!(0, util_1.isNullOrUndefined)(student.trainings)) {
                let completedTrainings = _.filter(student.trainings, tr => (tr.status === bizlogics_1.Constants.training_status.CLOSED
                    && (0, util_1.isNullOrUndefined)(tr.archived)));
                if (!(0, util_1.isNullOrUndefined)(completedTrainings) && completedTrainings.length > 0) {
                    let sorted = _.sortBy(completedTrainings, 'completed_date').reverse();
                    ret = (_.includes([bizlogics_1.Constants.training_code.BT_42.CODE, bizlogics_1.Constants.training_code.BT_70.CODE], _.head(sorted).training_code))
                        || (Helper.hasCompletedHigherOrEquTraining(student.trainings, bizlogics_1.Constants.training_code.BT_70.CODE))
                        || (Helper.hasCompletedHigherOrEquTraining(student.trainings, bizlogics_1.Constants.training_code.BT_42.CODE));
                }
            }
        }
        return ret;
    }
    static setEligibleTrainingStatus(student, isEligible, requiresEmployment) {
        let ret;
        if (isEligible) {
            if ((Helper.isInCompliance(student) && (!requiresEmployment || Helper.hasEmployment(student)))
                || student.student_status_set.isCredentialExpired)
                ret = bizlogics_1.Constants.eligible_training_status.ACTIVATE;
            else
                ret = bizlogics_1.Constants.eligible_training_status.REMAIN_OPEN;
        }
        else
            ret = bizlogics_1.Constants.eligible_training_status.CLOSE;
        return ret;
    }
    static completedHigherOrEquTrainings(trainings, training_code) {
        let reqTrainings = [];
        const higher_equ_trainings = _.filter(bizlogics_1.Constants.higher_equ_training_map, { 'CODE': training_code });
        if (!(0, util_1.isNullOrUndefined)(higher_equ_trainings) && higher_equ_trainings.length > 0) {
            reqTrainings = _.filter(trainings, tr => (tr.status === bizlogics_1.Constants.training_status.CLOSED
                && !(0, util_1.isNullOrUndefined)(tr.completed_date)
                && (0, util_1.isNullOrUndefined)(tr.archived)
                && _.includes(higher_equ_trainings[0].HIGHER_EQU_TRAINING, tr.training_code)));
        }
        return reqTrainings;
    }
    static hasCompletedHigherOrEquTraining(trainings, training_code) {
        let ret = false;
        const reqTrainings = Helper.completedHigherOrEquTrainings(trainings, training_code);
        ret = (!(0, util_1.isNullOrUndefined)(reqTrainings)
            && reqTrainings.length > 0)
            ? true
            : false;
        return ret;
    }
    static getCredentialByType(student, cred_type) {
        if (!(0, util_1.isNullOrUndefined)(student.credentials)) {
            let credType = student.credentials
                .filter(c => c.name == cred_type)[0];
            return credType;
        }
    }
    static hasCompletedBT70Training(trainingCode, student) {
        if (!(0, util_1.isNullOrUndefined)(student.trainings)) {
            const higher_equ_trainings = _.filter(bizlogics_1.Constants.higher_equ_training_map, { 'CODE': trainingCode });
            let completedTrainings = _.filter(student.trainings, tr => (tr.status === bizlogics_1.Constants.training_status.CLOSED
                && (0, util_1.isNullOrUndefined)(tr.archived) && _.includes(higher_equ_trainings[0].HIGHER_EQU_TRAINING, tr.training_code)
                && !(0, util_1.isNullOrUndefined)(tr.completed_date)));
            if (!(0, util_1.isNullOrUndefined)(completedTrainings) && completedTrainings.length > 0) {
                for (let training of completedTrainings) {
                    if (_.includes([bizlogics_1.Constants.training_code.BT_70.CODE, bizlogics_1.Constants.training_code.BT_42.CODE, bizlogics_1.Constants.training_code.EXEMPT_BT70.CODE], training.training_code)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    static isSpecificTraining(training, expectedTraining) {
        let ret = false;
        if (training === null || training === void 0 ? void 0 : training.training_code) {
            ret = _.includes([expectedTraining], training.training_code);
        }
        return ret;
    }
}
exports.Helper = Helper;
//# sourceMappingURL=helper.js.map