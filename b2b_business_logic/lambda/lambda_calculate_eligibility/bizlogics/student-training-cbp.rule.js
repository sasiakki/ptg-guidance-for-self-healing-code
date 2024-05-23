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
exports.Student_training_cbp_rule = void 0;
const util_1 = require("util");
const _ = __importStar(require("lodash"));
class Student_training_cbp_rule {
    constructor() {
    }
    static isCBPEligible(student, trainings) {
        var ret = false;
        console.log(`Start isCBPEligible ${ret}`);
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set)) {
            console.log(`student.student_status_set.complianceStatus ${student.student_status_set.complianceStatus}`);
        }
        console.log(`student.active_training ${student.active_training}`);
        if (!(0, util_1.isNullOrUndefined)(student.student_status_set)
            && !(0, util_1.isNullOrUndefined)(student.student_status_set.complianceStatus)) {
            if ((student.student_status_set.complianceStatus === 'Compliant')
                && (!(0, util_1.isNullOrUndefined)(student.active_training)
                    && student.active_training === 'Continuing Education')
                && (!(0, util_1.isNullOrUndefined)(student.prefer_language)
                    && student.prefer_language === 'English')
                && !(0, util_1.isNullOrUndefined)(student.course_completions)) {
                var number = _.filter(_.uniqBy(student.course_completions, 'name'), function (val, key, obj) {
                    return val.name === 'HCA Best Practices in Infection Control and Blood Borne Pathogens SEIU 775 UT';
                });
                if (number.length === 0)
                    ret = true;
            }
        }
        console.log(`End isCBPEligible ${ret}`);
        return ret;
    }
}
exports.Student_training_cbp_rule = Student_training_cbp_rule;
//# sourceMappingURL=student-training-cbp.rule.js.map