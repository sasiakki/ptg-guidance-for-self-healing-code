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
exports.Student_bt_rehire_rule = void 0;
const util_1 = require("util");
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
const moment = require("moment");
const _ = __importStar(require("lodash"));
class Student_bt_rehire_rule {
    constructor() { }
    static processTrainings(student, btTrainings) {
        let rule = new Student_bt_rehire_rule();
        let invalidBtTrainings = [];
        if (student.student_status_set.isRehire
            && student.employments
            && moment(consts_1.Constants.BT_REHIRE_MIN).utc().startOf('day').isSameOrBefore(moment(student.employments[0].rehire_date).utc().startOf('day'))) {
            if (!(0, util_1.isNullOrUndefined)(btTrainings)) {
                _.forEach(btTrainings, tr => {
                    if (_.includes(helper_1.Helper.BT_CODES, tr.training_code)
                        && tr.status === consts_1.Constants.training_status.ACTIVE
                        && (0, util_1.isNullOrUndefined)(tr.benefit_continuation_due_date)
                        && tr.tracking_date
                        && moment(tr.tracking_date).utc().startOf('day').isBefore(moment(consts_1.Constants.BT_REHIRE_MIN).utc().startOf('day'))) {
                        tr.status = consts_1.Constants.training_status.CLOSED;
                        invalidBtTrainings.push(tr);
                    }
                });
            }
        }
        return invalidBtTrainings;
    }
}
exports.Student_bt_rehire_rule = Student_bt_rehire_rule;
//# sourceMappingURL=student-bt-rehire.rule.js.map