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
exports.Student_training_due_date_rule = void 0;
const models_1 = require("../models");
const util_1 = require("util");
const consts_1 = require("./consts");
const moment = require("moment");
const _ = __importStar(require("lodash"));
const helper_1 = require("../helpers/helper");
class Student_training_due_date_rule {
    constructor() { }
    static createNewTraining(student, training_code) {
        let newTraining = new models_1.Student_training();
        const cTrs = _.filter(student.trainings, {
            training_code
        });
        let ind = cTrs.length > 0 ? _.max(_.map(cTrs, x => Number(x.id.split('-')[2]))) + 1 : 1;
        newTraining.id = student.id + '-' + training_code + '-' + ind;
        newTraining.training_code = training_code;
        newTraining.status = consts_1.Constants.training_status.ACTIVE;
        let required_hours = _.find(consts_1.Constants.training_code, ['CODE', training_code]).HOURS;
        if (required_hours !== '') {
            newTraining.required_hours = Number(required_hours);
        }
        newTraining.name = _.find(consts_1.Constants.training_code, ['CODE', training_code]).NAME;
        let benefitContinuationDueDate = undefined;
        let dueDate = undefined;
        let trackingDate = undefined;
        let trkDate = (!(0, util_1.isNullOrUndefined)(student.employments) &&
            student.employments.length > 0)
            ? moment(student.employments[0].tc_tracking_date).toDate()
            : moment().toDate();
        [trackingDate, dueDate] = Student_training_due_date_rule
            .getTrackingDateAndDueDate(student, newTraining, student.assigned_category, trkDate);
        newTraining.tracking_date = trackingDate != undefined
            ? moment(trackingDate).toISOString()
            : undefined;
        newTraining.due_date = dueDate != undefined
            ? moment(dueDate).toISOString()
            : undefined;
        newTraining.benefit_continuation_due_date = null;
        newTraining.created = moment().utc().toISOString();
        newTraining.is_required = _.find(consts_1.Constants.training_code, ['CODE', training_code]).REQUIRED;
        newTraining.studentId = student.id;
        console.log(`studentid: ${student.id}; new training created: ${JSON.stringify(newTraining)}`);
        return newTraining;
    }
    static getTrackingDateAndDueDate(student, training, category, trkDate) {
        let trackingDate = trkDate;
        let dueDate = undefined;
        switch (training.training_code) {
            case consts_1.Constants.training_code.BT_7.CODE:
            case consts_1.Constants.training_code.BT_9.CODE:
            case consts_1.Constants.training_code.BT_30.CODE:
            case consts_1.Constants.training_code.BT_42.CODE:
            case consts_1.Constants.training_code.BT_70.CODE:
                dueDate = new Student_training_due_date_rule()
                    .getBasicTrainingDueDate(trackingDate);
                break;
            case consts_1.Constants.training_code.CE_12.CODE:
                dueDate = new Student_training_due_date_rule()
                    .getContinuingEducationDueDate(student, category);
                trackingDate = moment(dueDate).add(-1, 'years').toDate();
                break;
            default:
                dueDate = undefined;
                trackingDate = undefined;
        }
        return [trackingDate, dueDate];
    }
    getBasicTrainingDueDate(trackingDate) {
        return moment(trackingDate).add(119, 'days').toDate();
    }
    getContinuingEducationDueDate(student, category) {
        let lastCompletedTraining = this.getLastCompletedTraining(student);
        let isFirstCE = !(this.isContinuingEducation(lastCompletedTraining));
        let nextDOB = this.getNextBirthDate(student);
        let nextDOBplusOne = moment(nextDOB).add(1, 'years').toDate();
        let lastCompletedDateYrDOBplusOne = (lastCompletedTraining) ? moment(nextDOB).year(moment(lastCompletedTraining.completed_date).add(1, 'years').year()).utc().startOf('day').toDate() : null;
        if (process.env.IS_LOCAL) {
            console.log('\n**************************');
            console.log('lastCompletedTraining: ', lastCompletedTraining);
            console.log('isFirstCE: ', isFirstCE);
            console.log('nextDOB: ', nextDOB);
            console.log('nextDOB + 1 yr: ', nextDOBplusOne);
            console.log('lastCompletedDateYrDOB + 1 yr: ', lastCompletedDateYrDOBplusOne);
            console.log('lastCompletedDateYrDOB + 1 yr difference with lastCompletedDate:', (lastCompletedTraining && lastCompletedDateYrDOBplusOne) ? moment(lastCompletedDateYrDOBplusOne).diff(moment(lastCompletedTraining.completed_date), 'days') : 0, 'days');
            console.log('**************************\n');
        }
        if (isFirstCE) {
            switch (category) {
                case consts_1.Constants.work_category.ADULT_CHILD:
                    if (lastCompletedTraining && helper_1.Helper.isSpecificTraining(lastCompletedTraining, consts_1.Constants.training_code.BT_30.CODE)) {
                        return lastCompletedDateYrDOBplusOne;
                    }
                    else {
                        return nextDOB;
                    }
                case consts_1.Constants.work_category.STANDARD_HCA:
                    if (!(0, util_1.isNullOrUndefined)(student.credentials)) {
                        const credential = student.credentials[0];
                        if (credential) {
                            const credentialExpirationDate = moment(credential.expiration_date).utc().startOf('day');
                            if (process.env.IS_LOCAL) {
                                console.log('\n**************************');
                                console.log('Credential \t', credential.name);
                                console.log('CredentialStatus \t', credential.status);
                                console.log('CredentialExpiration \t', credentialExpirationDate.toDate());
                                console.log('**************************\n');
                            }
                            if (credential.status === consts_1.Constants.credential_status.ACTIVE) {
                                if (_.includes([consts_1.Constants.credential_type.HCA.CODE, consts_1.Constants.credential_type.NAC.CODE], credential.name)) {
                                    if (process.env.IS_LOCAL)
                                        console.log('!!! FirstCE, SHCA with HM|NC credential, assign to the expiration date !!!\n');
                                    return credentialExpirationDate.toDate();
                                }
                                else if (credential.name === consts_1.Constants.credential_type.OSPI.CODE) {
                                    if (process.env.IS_LOCAL)
                                        console.log('!!! OSPI credential, providers next birthday !!!\n');
                                    return nextDOB;
                                }
                                else {
                                    if (process.env.IS_LOCAL)
                                        console.log('!!! possible exempt user with invalid credentials, providers next birthday !!!\n');
                                    return nextDOB;
                                }
                            }
                            else if (_.includes([consts_1.Constants.credential_status.EXPIRED, consts_1.Constants.credential_status.PENDING], credential.status)) {
                                if (_.includes([consts_1.Constants.credential_type.HCA.CODE, consts_1.Constants.credential_type.NAC.CODE], credential.name)) {
                                    if (process.env.IS_LOCAL)
                                        console.log('!!! expired | pending HM|NC credential, use credential expiration date as due date !!!\n');
                                    return credentialExpirationDate.toDate();
                                }
                                else {
                                    if (process.env.IS_LOCAL)
                                        console.log('!!! expired | pending NON-(HM|NC) credential, use birthday of expiration date year as due date !!!\n');
                                    return this.getCredentialExpirationCEDueDate(student, credential.expiration_date);
                                }
                            }
                            else {
                                return undefined;
                            }
                        }
                    }
                    else if (!(0, util_1.isNullOrUndefined)(student.student_status_set) && student.student_status_set.isGrandFathered) {
                        if (process.env.IS_LOCAL)
                            console.log('!!! no credentials but exempt by employment, is next birthday !!!\n');
                        return nextDOB;
                    }
                    else {
                        if (process.env.IS_LOCAL)
                            console.log('!!! no credentials and not exempt, set to undefined !!!\n');
                        return undefined;
                    }
                    break;
                default:
                    if (process.env.IS_LOCAL)
                        console.log('!!! only adch and shca are valid working types, set to undefined !!!\n');
                    return undefined;
            }
        }
        else {
            let dueDate = (lastCompletedTraining.due_date)
                ? moment(lastCompletedTraining.due_date).add(1, 'years').toDate()
                : nextDOB;
            if (category === consts_1.Constants.work_category.STANDARD_HCA
                && student.credentials
                && _.includes([consts_1.Constants.credential_type.HCA.CODE, consts_1.Constants.credential_type.NAC.CODE], student.credentials[0].name)) {
                if (student.student_status_set.isCredentialExpired === true
                    || (student.credentials[0].status === consts_1.Constants.credential_status.ACTIVE
                        && (student.student_status_set.isRehire === true))) {
                    const credentialExpDate = moment(student.credentials[0].expiration_date).utc().startOf('day');
                    const lastcompletedTrainingDueDate = moment(lastCompletedTraining.due_date).utc().startOf('day');
                    if (lastcompletedTrainingDueDate.year() < credentialExpDate.year()) {
                        if (process.env.IS_LOCAL)
                            console.log(`!!! SHCA and rehire w/ ${student.credentials[0].status} ${student.credentials[0].name} credential, assign duedate to cred expiration date !!!\t`);
                        dueDate = credentialExpDate.toDate();
                    }
                }
            }
            if ((category === consts_1.Constants.work_category.ADULT_CHILD || student.student_status_set.isGrandFathered)
                && lastCompletedTraining.due_date
                && student.student_status_set.isRehire === true) {
                const tmpLastCompletedTraining = moment(lastCompletedTraining.due_date).utc().startOf('day');
                const terminationDateYear = moment(student.employments[0].terminate_date).utc().startOf('day').year();
                const rehireYear = moment(student.employments[0].rehire_date).utc().startOf('day').year();
                if (tmpLastCompletedTraining.year() >= terminationDateYear && tmpLastCompletedTraining.year() < rehireYear) {
                    dueDate = tmpLastCompletedTraining.year(rehireYear).utc().startOf('day').toDate();
                    if (process.env.IS_LOCAL)
                        console.log('!!! ADCH and Rehire duedate !!!\t', dueDate);
                }
            }
            return dueDate;
        }
    }
    getCredentialExpirationCEDueDate(student, expirationDate) {
        const expirationDay = moment(expirationDate).utc().startOf('day');
        const dob = student.birth_date;
        let expirationDOB = moment(dob).utc().startOf('day').year(expirationDay.year());
        return expirationDOB.toDate();
    }
    getNextBirthDate(student) {
        const today = moment().utc().startOf('day');
        const dob = student.birth_date;
        let nextDOB = moment(dob).utc().startOf('day').year(today.year());
        if (process.env.IS_LOCAL)
            console.log('\n***\ntoday:', today, '>=', 'nextDOB:', nextDOB, ':', today.isSameOrAfter(nextDOB), '\n***');
        if (today.isSameOrAfter(nextDOB))
            nextDOB = nextDOB.year(today.year() + 1);
        return nextDOB.toDate();
    }
    isContinuingEducation(lastCompletedTraining) {
        return helper_1.Helper.isSpecificTraining(lastCompletedTraining, consts_1.Constants.training_code.CE_12.CODE);
    }
    getLastCompletedTraining(student) {
        let training = null;
        if (!(0, util_1.isNullOrUndefined)(student.trainings)) {
            let completedTrainings = _.filter(student.trainings, t => helper_1.Helper.trainingIsClosedByComplete(t) && t.is_required);
            if (!(0, util_1.isNullOrUndefined)(completedTrainings)
                && _.size(completedTrainings) > 0) {
                let sorted = _.sortBy(completedTrainings, 'completed_date').reverse();
                training = _.head(sorted);
                if (this.isContinuingEducation(training)) {
                    const completedCEs = _.filter(completedTrainings, t => _.includes([consts_1.Constants.training_code.CE_12.CODE], t.training_code));
                    training = _.head(_.sortBy(completedCEs, 'due_date').reverse());
                }
            }
        }
        return training;
    }
    checkIsHCAandNAC(student) {
        let isHCA = false;
        let isNAC = false;
        if (!(0, util_1.isNullOrUndefined)(student.credentials)) {
            let credHCA = student.credentials
                .filter(c => c.name == consts_1.Constants
                .credential_type
                .HCA.CODE)[0];
            isHCA = (!(0, util_1.isNullOrUndefined)(credHCA)
                && credHCA.status == consts_1.Constants.credential_status.ACTIVE)
                ? true : false;
            let credNAC = student.credentials
                .filter(c => c.name == consts_1.Constants
                .credential_type
                .NAC.CODE)[0];
            isNAC = (!(0, util_1.isNullOrUndefined)(credNAC)
                && credNAC.status == consts_1.Constants.credential_status.ACTIVE)
                ? true : false;
        }
        return [isHCA, isNAC];
    }
    checkIsOSPI(student) {
        let isOSPI = false;
        if (!(0, util_1.isNullOrUndefined)(student.credentials)) {
            let credOSPI = helper_1.Helper.getCredentialByType(student, consts_1.Constants.credential_type.OSPI.CODE);
            isOSPI = (!(0, util_1.isNullOrUndefined)(credOSPI)
                && credOSPI.status == consts_1.Constants.credential_status.ACTIVE)
                ? true : false;
        }
        return isOSPI;
    }
}
exports.Student_training_due_date_rule = Student_training_due_date_rule;
//# sourceMappingURL=student-training-due-date.rule.js.map