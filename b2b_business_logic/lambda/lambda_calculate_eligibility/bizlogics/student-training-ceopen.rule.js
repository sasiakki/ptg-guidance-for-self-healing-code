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
exports.Student_training_ceopen_rule = void 0;
const util_1 = require("util");
const _ = __importStar(require("lodash"));
const consts_1 = require("./consts");
const student_training_due_date_rule_1 = require("./student-training-due-date.rule");
const helper_1 = require("../helpers/helper");
class Student_training_ceopen_rule {
    constructor() { }
    static isOpenCEEligible(student, trainings) {
        console.log(`Start isOpenCEEligible ${ret}`);
        var ret = false;
        if (helper_1.Helper.isInCompliance(student) &&
            helper_1.Helper.hasEmployment(student) &&
            !helper_1.Helper.studentValuesNullOrUndefined([
                student.assigned_category,
                student.student_status_set.complianceStatus,
            ])) {
            if ((student.assigned_category == consts_1.Constants.work_category.STANDARD_HCA ||
                student.assigned_category == consts_1.Constants.work_category.ADULT_CHILD) &&
                !(0, util_1.isNullOrUndefined)(student.credentials) &&
                helper_1.Helper.hasActiveCredential([
                    consts_1.Constants.credential_type.ARNP.CODE,
                    consts_1.Constants.credential_type.RN.CODE,
                    consts_1.Constants.credential_type.LPN.CODE,
                ], student.credentials)) {
                ret = true;
            }
        }
        if (student.assigned_category ==
            consts_1.Constants.work_category.PARENT_PROVIDER_DDD ||
            student.assigned_category == consts_1.Constants.work_category.DDD_NDDD ||
            student.assigned_category == consts_1.Constants.work_category.RESPITE ||
            student.assigned_category ==
                consts_1.Constants.work_category.LIMITED_SERVICE_PROVIDER) {
            if (helper_1.Helper.isExemptFromOSAndBTByCredential(student) === true) {
                ret = true;
            }
            else {
                if (helper_1.Helper.hasTakenOSAndBT(helper_1.Helper.determineBtType(student.assigned_category), trainings) === true) {
                    ret = true;
                }
            }
        }
        console.log(`End isOpenCEEligible ${ret}`);
        return ret;
    }
    static createOrUpdateTraining(student, trainings, status) {
        let training = null;
        let CLLTrains = _.filter(trainings, {
            training_code: consts_1.Constants.training_code.CE_OPEN_LIB.CODE,
        });
        if (CLLTrains.length > 0) {
            CLLTrains[0].status =
                status === true
                    ? consts_1.Constants.training_status.ACTIVE
                    : consts_1.Constants.training_status.CLOSED;
            training = CLLTrains[0];
        }
        else if (CLLTrains.length == 0 && status) {
            training = student_training_due_date_rule_1.Student_training_due_date_rule.createNewTraining(student, consts_1.Constants.training_code.CE_OPEN_LIB.CODE);
        }
        return training;
    }
}
exports.Student_training_ceopen_rule = Student_training_ceopen_rule;
//# sourceMappingURL=student-training-ceopen.rule.js.map