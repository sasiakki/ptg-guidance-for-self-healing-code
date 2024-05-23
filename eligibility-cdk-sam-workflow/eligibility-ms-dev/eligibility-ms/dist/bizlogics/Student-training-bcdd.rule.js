"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_bcdd_rule = void 0;
const consts_1 = require("./consts");
const moment = require("moment");
class Student_training_bcdd_rule {
    constructor() { }
    static processTrainingBcdd(student, training) {
        let rule = new Student_training_bcdd_rule();
        return rule.updateBCDD(training, student);
    }
    updateBCDD(training, student) {
        const isRehire = student.student_status_set.isRehire;
        let bcddTR = training;
        let bcdd = null;
        let bcddReasonCode = null;
        switch (bcddTR.training_code) {
            case consts_1.Constants.training_code.BT_7.CODE:
            case consts_1.Constants.training_code.BT_9.CODE:
            case consts_1.Constants.training_code.BT_30.CODE:
            case consts_1.Constants.training_code.BT_42.CODE:
            case consts_1.Constants.training_code.BT_70.CODE:
                if (!bcddTR.benefit_continuation_due_date || isRehire) {
                    const btDate = (isRehire)
                        ? moment(student.employments[0].rehire_date).utc().startOf('day')
                        : moment(bcddTR.tracking_date).utc().startOf('day');
                    [bcdd, bcddReasonCode] = this.getBTBenefitContinuationDueDate(btDate.toDate(), isRehire);
                }
                break;
            case consts_1.Constants.training_code.CE_12.CODE:
                [bcdd, bcddReasonCode] = this.getCEBenefitContinuationDueDate(moment(bcddTR.due_date).toDate(), isRehire);
                break;
            default:
                break;
        }
        if (bcdd) {
            bcddTR.benefit_continuation_due_date = moment(bcdd).toISOString();
            bcddTR.reason_code = bcddReasonCode;
        }
        return bcddTR;
    }
    getBTBenefitContinuationDueDate(trackingDate, isRehire) {
        const mTrackingDate = moment(trackingDate).utc().startOf('day');
        let bcdd = null;
        let dueDateExtension = null;
        let reasonCode = null;
        if (mTrackingDate.isSameOrAfter(moment('2019-08-17'), 'day') && mTrackingDate.isSameOrBefore(moment('2020-09-30'), 'day')) {
            bcdd = moment('2023-01-31').utc().startOf('day');
        }
        else if (mTrackingDate.isSameOrAfter(moment('2020-10-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2021-04-30'), 'day')) {
            bcdd = moment('2023-04-30').utc().startOf('day');
        }
        else if (mTrackingDate.isSameOrAfter(moment('2021-05-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2022-03-31'), 'day')) {
            bcdd = moment('2023-07-31').utc().startOf('day');
        }
        else if (mTrackingDate.isSameOrAfter(moment('2022-04-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2022-09-30'), 'day')) {
            bcdd = moment('2023-10-31').utc().startOf('day');
        }
        else if (mTrackingDate.isSameOrAfter(moment('2022-10-01'), 'day') && mTrackingDate.isSameOrBefore(moment('2023-06-30'), 'day')) {
            bcdd = moment('2023-11-30').utc().startOf('day');
        }
        else if (mTrackingDate.isSameOrAfter(moment('2023-07-01'), 'day') && isRehire === true) {
            bcdd = mTrackingDate.add(consts_1.Constants.BT_REHIRE_EXTENSION_DAYS, 'day');
            reasonCode = consts_1.Constants.bcdd_reason_code.HB1694_REHIRE;
        }
        if (bcdd) {
            dueDateExtension = bcdd.toDate();
            if (isRehire === false)
                reasonCode = consts_1.Constants.bcdd_reason_code.COVID19;
            else if (!reasonCode)
                reasonCode = consts_1.Constants.bcdd_reason_code.ER_REHIRE;
        }
        return [dueDateExtension, reasonCode];
    }
    getCEBenefitContinuationDueDate(dueDate, isRehire) {
        const mDueDate = moment(dueDate).utc().startOf('day');
        let bcdd = null;
        let reasonCode = null;
        if (mDueDate.isBefore(moment(consts_1.Constants.CE_BCDD).utc().startOf('day'), 'day')) {
            bcdd = moment(moment(consts_1.Constants.CE_BCDD).utc().startOf('day')).toDate();
            reasonCode = (isRehire) ? consts_1.Constants.bcdd_reason_code.ER_REHIRE : consts_1.Constants.bcdd_reason_code.COVID19;
        }
        return [bcdd, reasonCode];
    }
}
exports.Student_training_bcdd_rule = Student_training_bcdd_rule;
//# sourceMappingURL=Student-training-bcdd.rule.js.map