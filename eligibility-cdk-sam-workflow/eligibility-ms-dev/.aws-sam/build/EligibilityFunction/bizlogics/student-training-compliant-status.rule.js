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
exports.Student_training_compliant_status_rule = void 0;
const util_1 = require("util");
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
const moment = require("moment");
const _ = __importStar(require("lodash"));
class Student_training_compliant_status_rule {
    constructor() { }
    static isCompliant(student, trainings) {
        let ret = false;
        if ((0, util_1.isNullOrUndefined)(student.trainings))
            student.trainings = trainings;
        let rule = new Student_training_compliant_status_rule();
        const isEmployed = helper_1.Helper.hasEmployment(student);
        if (isEmployed || rule.hasTraining(student.trainings)) {
            if (rule.isTrainingNeedCredential(student)) {
                if (((rule.isCredentialActive(student))
                    || helper_1.Helper.isGrandFathered(student))
                    && !rule.isTrainingOverdue(student.trainings)) {
                    ret = true;
                }
                else if (helper_1.Helper.hasCredential(helper_1.Helper.CE_EXEMPT_CREDENTIAL_CODES, student.credentials, helper_1.Helper.NON_ACTIVE_CREDENTIAL_STATUSES)
                    && isEmployed) {
                    ret = true;
                }
                else if ((0, util_1.isNullOrUndefined)(student.credentials)
                    && !helper_1.Helper.isGrandFathered(student)) {
                    if (helper_1.Helper.isPendingDOHExam(student)
                        && isEmployed) {
                        ret = true;
                    }
                    else if (!rule.hasActiveCETraining(student.trainings)
                        && !rule.isTrainingOverdue(student.trainings)) {
                        ret = true;
                    }
                }
            }
            else {
                if (!rule.isTrainingOverdue(student.trainings)) {
                    ret = true;
                }
            }
        }
        console.log(`studentid: ${student.id}; isCompliant ${ret}`);
        return ret;
    }
    hasTraining(trainings) {
        let ret = false;
        if (!(0, util_1.isNullOrUndefined)(trainings)
            && (_.filter(trainings, tr => tr.status === consts_1.Constants.training_status.ACTIVE)
                .length > 0))
            ret = true;
        return ret;
    }
    isTrainingOverdue(trainings) {
        let ret = false;
        if (!(0, util_1.isNullOrUndefined)(trainings)
            && (_.filter(trainings, tr => (tr.status === consts_1.Constants.training_status.ACTIVE
                && tr.training_code !== consts_1.Constants.training_code.OS.CODE
                && (moment(tr.due_date).isBefore(moment().startOf('day'))
                    && ((0, util_1.isNullOrUndefined)(tr.benefit_continuation_due_date)
                        || moment().isAfter(tr.benefit_continuation_due_date)))))
                .length > 0))
            ret = true;
        return ret;
    }
    isTrainingNeedCredential(student) {
        let ret = false;
        if (_.includes([consts_1.Constants.work_category.STANDARD_HCA,
            consts_1.Constants.work_category.DDD_STANDARD], student.assigned_category)) {
            ret = true;
        }
        return ret;
    }
    isCredentialActive(student) {
        let ret = false;
        if (!(0, util_1.isNullOrUndefined)(student.credentials)
            && (_.filter(student.credentials, cred => (cred.status === consts_1.Constants.credential_status.ACTIVE))
                .length > 0))
            ret = true;
        return ret;
    }
    hasActiveCETraining(trainings) {
        let ret = false;
        let activeTrainings = _.filter(trainings, tr => (tr.status === consts_1.Constants.training_status.ACTIVE));
        if (!(0, util_1.isNullOrUndefined)(activeTrainings)) {
            if (_.some(activeTrainings, tr => {
                return tr.training_code === consts_1.Constants.training_code.CE_12.CODE;
            })) {
                ret = true;
            }
        }
        return ret;
    }
}
exports.Student_training_compliant_status_rule = Student_training_compliant_status_rule;
//# sourceMappingURL=student-training-compliant-status.rule.js.map