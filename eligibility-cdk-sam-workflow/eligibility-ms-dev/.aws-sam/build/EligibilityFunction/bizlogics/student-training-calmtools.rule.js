"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_calmtools_rule = void 0;
const helper_1 = require("../helpers/helper");
const consts_1 = require("./consts");
class Student_training_calmtools_rule {
    constructor() { }
    static isCalmToolsEligible(student, trainings) {
        const validWorkerCategoryWithOSBT = [
            consts_1.Constants.work_category.LIMITED_SERVICE_PROVIDER,
            consts_1.Constants.work_category.PARENT_PROVIDER_DDD,
            consts_1.Constants.work_category.DDD_NDDD,
            consts_1.Constants.work_category.RESPITE
        ];
        const validWorkerCategoryWithOSBTOrCredential = [
            consts_1.Constants.work_category.STANDARD_HCA,
            consts_1.Constants.work_category.ADULT_CHILD
        ];
        console.log('>>>>>>check CalmTools');
        if (helper_1.Helper.isInCompliance(student)) {
            if (validWorkerCategoryWithOSBTOrCredential.includes(student.assigned_category)
                &&
                    (helper_1.Helper.hasTakenOSAndBT(helper_1.Helper.determineBtType(student.assigned_category), trainings)
                        ||
                            helper_1.Helper.isExemptFromOSAndBTByCredential(student))) {
                console.log('student is eligible for Tools for Calm, creating...');
                return true;
            }
            else if (validWorkerCategoryWithOSBT.includes(student.assigned_category)
                &&
                    helper_1.Helper.hasTakenOSAndBT(helper_1.Helper.determineBtType(student.assigned_category), trainings)) {
                console.log('student is eligible for Tools for Calm, creating...');
                return true;
            }
        }
        return false;
    }
}
exports.Student_training_calmtools_rule = Student_training_calmtools_rule;
//# sourceMappingURL=student-training-calmtools.rule.js.map