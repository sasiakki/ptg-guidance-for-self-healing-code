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
        switch (bcddTR.training_code) {
            case consts_1.Constants.training_code.BT_7.CODE:
            case consts_1.Constants.training_code.BT_9.CODE:
            case consts_1.Constants.training_code.BT_30.CODE:
            case consts_1.Constants.training_code.BT_42.CODE:
            case consts_1.Constants.training_code.BT_70.CODE:
                if (!bcddTR.benefit_continuation_due_date) {
                    const btDate = (isRehire)
                        ? moment(student.employments[0].rehire_date).utc().startOf('day')
                        : moment(bcddTR.tracking_date).utc().startOf('day');
                    bcdd = this.getBTBenefitContinuationDueDate(btDate.toDate());
                }
                break;
            case consts_1.Constants.training_code.CE_12.CODE:
                bcdd = this.getCEBenefitContinuationDueDate(moment(bcddTR.due_date).toDate());
                break;
            default:
                break;
        }
        if (bcdd) {
            bcddTR.benefit_continuation_due_date = moment(bcdd).toISOString();
            bcddTR.reason_code = (isRehire)
                ? consts_1.Constants.bcdd_reason_code.REHIRED
                : consts_1.Constants.bcdd_reason_code.COVID19;
        }
        return bcddTR;
    }
    getBTBenefitContinuationDueDate(trackingDate) {
        const mTrackingDate = moment(trackingDate).utc().startOf('day');
        let bcdd = null;
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
        bcdd = (bcdd) ? bcdd.toDate() : null;
        return bcdd;
    }
    getCEBenefitContinuationDueDate(dueDate) {
        const mDueDate = moment(dueDate).utc().startOf('day');
        let bcdd = null;
        if (mDueDate.isBefore(moment(consts_1.Constants.CE_BCDD).utc().startOf('day'), 'day')) {
            bcdd = moment(moment(consts_1.Constants.CE_BCDD).utc().startOf('day')).toDate();
        }
        return bcdd;
    }
}
exports.Student_training_bcdd_rule = Student_training_bcdd_rule;
//# sourceMappingURL=Student-training-bcdd.rule.js.map