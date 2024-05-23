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
exports.Student_training_os_rule = void 0;
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
const _ = __importStar(require("lodash"));
class Student_training_os_rule {
    constructor() { }
    static isOsEligible(student, trainings) {
        let isEligible = false;
        const requiresEmployment = true;
        const isRenewableCredential = helper_1.Helper.expiredCredentialIsRenewable(student);
        if (!helper_1.Helper.isExemptFromOSAndBTByCredential(student)
            && !helper_1.Helper.hasCompletedTraining(consts_1.Constants.training_code.OS.CODE, student.trainings)
            && !(student.student_status_set.isCredentialExpired && student.assigned_category === consts_1.Constants.work_category.ADULT_CHILD)
            && (!isRenewableCredential
                || (isRenewableCredential && !_.includes([consts_1.Constants.work_category.STANDARD_HCA, consts_1.Constants.work_category.ADULT_CHILD], student.assigned_category)))) {
            isEligible = true;
        }
        const ret = helper_1.Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isOSEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
exports.Student_training_os_rule = Student_training_os_rule;
//# sourceMappingURL=student-training-os.rule.js.map