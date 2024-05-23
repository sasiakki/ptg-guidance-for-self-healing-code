"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_rules = void 0;
const student_training_ahcas_rule_1 = require("./student-training-ahcas.rule");
const student_training_12hrce_rule_1 = require("./student-training-12hrce.rule");
const student_training_os_rule_1 = require("./student-training-os.rule");
const student_training_bt_rule_1 = require("./student-training-bt.rule");
const student_training_refresher_rule_1 = require("./student-training-refresher.rule");
const consts_1 = require("./consts");
class Student_training_rules {
    constructor() { }
    static isEligible(student, trainings, course_code) {
        switch (course_code) {
            case consts_1.Constants.training_code.CE_12.CODE:
                return student_training_12hrce_rule_1.Student_training_12hrce_rule.is12hrCEEligible(student, trainings);
            case consts_1.Constants.training_code.OS.CODE:
                return student_training_os_rule_1.Student_training_os_rule.isOsEligible(student, trainings);
            case consts_1.Constants.training_code.BT_7.CODE:
            case consts_1.Constants.training_code.BT_9.CODE:
            case consts_1.Constants.training_code.BT_30.CODE:
            case consts_1.Constants.training_code.BT_70.CODE:
                return student_training_bt_rule_1.Student_training_bt_rule.isBtEligible(student, trainings, course_code);
            case consts_1.Constants.training_code.REFRESHER.CODE:
                return student_training_refresher_rule_1.Student_training_refresher_rule.isRefresherEligible(student, trainings);
            case consts_1.Constants.training_code.AHCAS.CODE:
                return student_training_ahcas_rule_1.Student_training_ahcas_rule.isAhcasEligible(student);
            default:
                return consts_1.Constants.eligible_training_status.CLOSE;
        }
    }
}
exports.Student_training_rules = Student_training_rules;
//# sourceMappingURL=student-training.rules.js.map