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
exports.Student_ce_rehire_rule = void 0;
const util_1 = require("util");
const consts_1 = require("./consts");
const moment = require("moment");
const _ = __importStar(require("lodash"));
class Student_ce_rehire_rule {
    constructor() { }
    static processTrainings(student, ceTrainings) {
        let invalidCETrainings = [];
        if (student.student_status_set.isRehire
            && student.employments
            && ((student.employments[0].training_category === consts_1.Constants.work_category.ADULT_CHILD || student.student_status_set.isGrandFathered)
                || ((student.employments[0].training_category === consts_1.Constants.work_category.STANDARD_HCA && student.credentials && student.credentials[0].status === consts_1.Constants.credential_status.ACTIVE)))) {
            if (!(0, util_1.isNullOrUndefined)(ceTrainings)) {
                _.forEach(ceTrainings, tr => {
                    if (tr.training_code === consts_1.Constants.training_code.CE_12.CODE
                        && tr.status === consts_1.Constants.training_status.ACTIVE) {
                        const dueDate = moment(tr.due_date).utc().startOf('day');
                        const rehireYear = moment(student.employments[0].rehire_date).utc().startOf('day').year();
                        const terminationDateYear = moment(student.employments[0].terminate_date).utc().startOf('day').year();
                        if (dueDate.year() < rehireYear && dueDate.year() > terminationDateYear) {
                            tr.status = consts_1.Constants.training_status.CLOSED;
                            invalidCETrainings.push(tr);
                        }
                    }
                });
            }
        }
        return invalidCETrainings;
    }
}
exports.Student_ce_rehire_rule = Student_ce_rehire_rule;
//# sourceMappingURL=student-ce-rehire.rule.js.map