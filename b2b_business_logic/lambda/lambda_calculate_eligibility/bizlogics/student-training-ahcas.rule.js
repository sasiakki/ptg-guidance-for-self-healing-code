"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_ahcas_rule = void 0;
const helper_1 = require("../helpers/helper");
const consts_1 = require("./consts");
class Student_training_ahcas_rule {
    constructor() {
    }
    static isAhcasEligible(student) {
        let isEligible = false;
        const requiresEmployment = false;
        let ret = consts_1.Constants.eligible_training_status.CLOSE;
        if (!helper_1.Helper.studentValuesNullOrUndefined([student.student_status_set])
            && student.student_status_set.ahcas_eligible) {
            isEligible = true;
        }
        ret = helper_1.Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isAhcasEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
exports.Student_training_ahcas_rule = Student_training_ahcas_rule;
//# sourceMappingURL=student-training-ahcas.rule.js.map