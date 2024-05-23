"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_ebt_rule = void 0;
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
class Student_training_ebt_rule {
    constructor() { }
    static isEbtEligible(student, trainings) {
        console.log('>>>>>>check Exempt BT');
        const validWorkCategories = [
            consts_1.Constants.work_category.ADULT_CHILD,
            consts_1.Constants.work_category.PARENT_PROVIDER_DDD,
            consts_1.Constants.work_category.DDD_NDDD,
            consts_1.Constants.work_category.RESPITE,
            consts_1.Constants.work_category.LIMITED_SERVICE_PROVIDER
        ];
        if (!helper_1.Helper.isInCompliance(student)
            ||
                helper_1.Helper.studentValuesNullOrUndefined([
                    student.assigned_category,
                    trainings
                ])) {
            return false;
        }
        if (helper_1.Helper.isInCompliance(student)
            &&
                (helper_1.Helper.isGrandFathered(student)
                    ||
                        validWorkCategories.includes(student.assigned_category))) {
            console.log('student is eligible, creating new Exempt BT training...');
            return true;
        }
        return false;
    }
}
exports.Student_training_ebt_rule = Student_training_ebt_rule;
//# sourceMappingURL=student-training-ebt.rule.js.map