"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
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
exports.Student_credential_expired_rule = void 0;
const models_1 = require("../models");
const util_1 = require("util");
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
const moment = require("moment");
const _ = __importStar(require("lodash"));
class Student_credential_expired_rule {
    constructor() { }
    static processExistingTrainings(student, trainings) {
        let processed = [];
        let ss = new models_1.Student_status_set();
        const credential = student.credentials[0];
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set)) {
            ss = student.student_status_set;
        }
        let rule = new Student_credential_expired_rule();
        ss.isCredentialExpired = (credential.status === consts_1.Constants.credential_status.EXPIRED
            || (credential.status === consts_1.Constants.credential_status.PENDING && credential.expiration_date.length > 1));
        if (rule.isCredentialExpiredOver3Years(student)) {
            processed = rule.archiveCompletedTrainings(trainings, credential.firstIssuance_date);
        }
        processed = processed.length === 0 ? (trainings !== null && trainings !== void 0 ? trainings : []) : processed;
        return [ss, processed];
    }
    isCredentialExpiredOver3Years(student) {
        return (moment(student.credentials[0].expiration_date).add(3, 'year').isBefore(moment().startOf('day'))
            && _.includes([consts_1.Constants.work_category.STANDARD_HCA, consts_1.Constants.work_category.DDD_STANDARD], student.assigned_category));
    }
    archiveCompletedTrainings(trainings, issue_date) {
        let reqTrainings = helper_1.Helper.completedHigherOrEquTrainings(trainings, consts_1.Constants.training_code.BT_70.CODE);
        let archived = [];
        if (!(0, util_1.isNullOrUndefined)(trainings)) {
            _.forEach(trainings, tr => {
                if (tr.training_code === consts_1.Constants.training_code.CE_12.CODE
                    && tr.status === consts_1.Constants.training_status.CLOSED
                    && !(tr.completed_date)) {
                    tr.archived = moment().utc().toISOString();
                }
                else if (_.includes(reqTrainings, tr)
                    && moment(tr.completed_date).isSameOrBefore(moment(issue_date))) {
                    tr.archived = moment().utc().toISOString();
                }
                archived.push(tr);
            });
        }
        return archived;
    }
}
exports.Student_credential_expired_rule = Student_credential_expired_rule;
//# sourceMappingURL=student-credential-expired.rule.js.map