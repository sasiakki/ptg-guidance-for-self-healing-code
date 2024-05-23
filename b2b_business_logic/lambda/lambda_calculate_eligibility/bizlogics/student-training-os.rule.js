"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_os_rule = void 0;
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
class Student_training_os_rule {
    constructor() { }
    static isOsEligible(student, trainings) {
        let isEligible = false;
        const requiresEmployment = true;
        if (!helper_1.Helper.isExemptFromOSAndBTByCredential(student)
            && !helper_1.Helper.hasCompletedTraining(consts_1.Constants.training_code.OS.CODE, student.trainings)
            && !(student.student_status_set.isCredentialExpired && student.assigned_category === consts_1.Constants.work_category.ADULT_CHILD)
            && !helper_1.Helper.expiredCredentialIsRenewable(student)) {
            isEligible = true;
        }
        const ret = helper_1.Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isOSEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
exports.Student_training_os_rule = Student_training_os_rule;
//# sourceMappingURL=student-training-os.rule.js.map