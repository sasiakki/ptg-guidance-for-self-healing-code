"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_refresher_rule = void 0;
const helper_1 = require("../helpers/helper");
const consts_1 = require("./consts");
const student_training_bt_rule_1 = require("./student-training-bt.rule");
class Student_training_refresher_rule {
    constructor() { }
    static isRefresherEligible(student, trainings) {
        let isEligible = false;
        const requiresEmployment = false;
        const validWorkerCategories = [consts_1.Constants.work_category.STANDARD_HCA];
        if (validWorkerCategories.includes(student.assigned_category)
            && helper_1.Helper.isPendingDOHExam(student)
            && helper_1.Helper.hasCompletedTraining(consts_1.Constants.training_code.BT_70.CODE, trainings)
            && !helper_1.Helper.isGrandFathered(student)
            && (student_training_bt_rule_1.Student_training_bt_rule.isBtEligible(student, trainings, consts_1.Constants.training_code.BT_70.CODE) === consts_1.Constants.eligible_training_status.CLOSE)) {
            isEligible = true;
        }
        const ret = helper_1.Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; isRefresherEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
exports.Student_training_refresher_rule = Student_training_refresher_rule;
//# sourceMappingURL=student-training-refresher.rule.js.map