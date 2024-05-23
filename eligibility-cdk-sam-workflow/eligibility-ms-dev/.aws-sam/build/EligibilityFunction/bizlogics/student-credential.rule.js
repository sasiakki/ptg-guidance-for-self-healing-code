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
exports.Student_credential_rule = void 0;
const models_1 = require("../models");
const util_1 = require("util");
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
const moment = require("moment");
const _ = __importStar(require("lodash"));
class Student_credential_rule {
    constructor() { }
    static processExistingTrainings(student, trainings) {
        const rule = new Student_credential_rule();
        let processed = [];
        let permanentTrainingUpdates = [];
        let ss = new models_1.Student_status_set();
        const credential = student.credentials[0];
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set)) {
            ss = student.student_status_set;
        }
        ss.isCredentialExpired = helper_1.Helper.isCredentialExpired(credential);
        [processed, permanentTrainingUpdates] = rule.checkTrainings(student, trainings);
        processed = processed.length === 0 ? (trainings !== null && trainings !== void 0 ? trainings : []) : processed;
        return [ss, processed, permanentTrainingUpdates];
    }
    isCredentialExpiredRestart(student) {
        return (!helper_1.Helper.expiredCredentialIsRenewable(student)
            && _.includes([consts_1.Constants.work_category.STANDARD_HCA, consts_1.Constants.work_category.DDD_STANDARD], student.assigned_category));
    }
    archiveCompletedTraining(training, isCredentialExpiredRestart, btTrainings, credentialIssueDate) {
        let archiveTraining = false;
        if (isCredentialExpiredRestart) {
            if (training.training_code === consts_1.Constants.training_code.CE_12.CODE
                && training.status === consts_1.Constants.training_status.CLOSED
                && !(training.completed_date)) {
                archiveTraining = true;
            }
            else if (_.includes(btTrainings, training)
                && moment(training.completed_date).isSameOrBefore(moment(credentialIssueDate))) {
                archiveTraining = true;
            }
        }
        return archiveTraining;
    }
    closeTraining(training, student) {
        let closeTraining = false;
        if (helper_1.Helper.hasCategory([consts_1.Constants.work_category.STANDARD_HCA], student.assigned_category)
            && training.training_code === consts_1.Constants.training_code.CE_12.CODE
            && training.status === consts_1.Constants.training_status.ACTIVE
            && ((student.student_status_set.isCredentialExpired
                && helper_1.Helper.hasCredential([consts_1.Constants.credential_type.HCA.CODE, consts_1.Constants.credential_type.NAC.CODE], student.credentials, [consts_1.Constants.credential_status.EXPIRED, consts_1.Constants.credential_status.PENDING]))
                ||
                    (helper_1.Helper.hasCredential([consts_1.Constants.credential_type.HCA.CODE, consts_1.Constants.credential_type.NAC.CODE], student.credentials, [consts_1.Constants.credential_status.ACTIVE])
                        && student.student_status_set.isRehire))
            && moment(training.due_date).utc().startOf('day').isBefore(moment(student.credentials[0].expiration_date).utc().startOf('day'))) {
            closeTraining = true;
        }
        return closeTraining;
    }
    checkTrainings(student, trainings) {
        let processedTrainings = [];
        let permanentTrainingUpdates = [];
        const isCredentialExpiredRestart = this.isCredentialExpiredRestart(student);
        const btTrainings = helper_1.Helper.completedHigherOrEquTrainings(trainings, consts_1.Constants.training_code.BT_70.CODE);
        if (!(0, util_1.isNullOrUndefined)(trainings)) {
            _.forEach(trainings, tr => {
                if (this.archiveCompletedTraining(tr, isCredentialExpiredRestart, btTrainings, student.credentials[0].firstIssuance_date)) {
                    tr.archived = moment().utc().toISOString();
                }
                else if (this.closeTraining(tr, student)) {
                    tr.status = consts_1.Constants.training_status.CLOSED;
                    permanentTrainingUpdates.push(tr);
                }
                processedTrainings.push(tr);
            });
        }
        return [processedTrainings, permanentTrainingUpdates];
    }
}
exports.Student_credential_rule = Student_credential_rule;
//# sourceMappingURL=student-credential.rule.js.map