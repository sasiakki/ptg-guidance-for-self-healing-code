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
exports.Student_training_bt_rule = void 0;
const util_1 = require("util");
const consts_1 = require("./consts");
const _ = __importStar(require("lodash"));
const helper_1 = require("../helpers/helper");
class Student_training_bt_rule {
    constructor() { }
    static isBtEligible(student, trainings, courseCode) {
        let isEligible = false;
        const requiresEmployment = true;
        const isOSCompleted = helper_1.Helper.hasCompletedTraining(consts_1.Constants.training_code.OS.CODE, trainings);
        const isBTCompleted = helper_1.Helper.hasCompletedTraining(courseCode, trainings);
        const isRenewableCredential = helper_1.Helper.expiredCredentialIsRenewable(student);
        console.log(`studentid: ${student.id}; has completed ${consts_1.Constants.training_code.OS.CODE} ${isOSCompleted}`);
        console.log(`studentid: ${student.id}; has completed ${courseCode} ${isBTCompleted}`);
        if (!helper_1.Helper.studentValuesNullOrUndefined([
            student.student_status_set,
            trainings
        ])
            && student.assigned_category !== consts_1.Constants.work_category.ORIENTATION_SAFETY
            && !helper_1.Helper.isExemptFromOSAndBTByCredential(student)
            && (!isRenewableCredential ||
                (isRenewableCredential && !_.includes([consts_1.Constants.work_category.STANDARD_HCA, consts_1.Constants.work_category.ADULT_CHILD], student.assigned_category)))
            && isOSCompleted
            && (!isBTCompleted || (courseCode == consts_1.Constants.training_code.BT_70.CODE
                && (_.includes([consts_1.Constants.work_category.STANDARD_HCA], student.assigned_category))
                && (0, util_1.isNullOrUndefined)(student.credentials)
                && !helper_1.Helper.hasCompletedBT70Training(courseCode, student)))) {
            isEligible = true;
        }
        const ret = helper_1.Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isBTEligible: ${isEligible}; eligibleTrainingStatus: ${ret}; courseCode: ${courseCode}`);
        return ret;
    }
}
exports.Student_training_bt_rule = Student_training_bt_rule;
//# sourceMappingURL=student-training-bt.rule.js.map