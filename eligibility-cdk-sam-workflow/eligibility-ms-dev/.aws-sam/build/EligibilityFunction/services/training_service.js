"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.training_service = void 0;
const models_1 = require("./../models");
const util_1 = require("util");
class training_service {
    static getTrainings(t) {
        const trainings = new Array();
        for (const s of t) {
            if (!(0, util_1.isNullOrUndefined)(s.train_id) && !(0, util_1.isNullOrUndefined)(s.status) && !(0, util_1.isNullOrUndefined)(s.training_code)) {
                const training = new models_1.Student_training();
                training.id = s.train_id;
                training.benefit_continuation_due_date = s.benefit_continuation_due_date;
                training.studentId = s.studentId;
                training.status = s.status;
                training.name = s.training_category;
                training.training_code = s.training_code;
                training.is_required = s.is_required;
                training.required_hours = s.required_hours;
                training.tracking_date = s.tracking_date;
                training.due_date = s.due_date;
                training.earned_hours = s.earned_hours;
                training.transfer_hours = s.transfer_hours;
                training.archived = s.archived;
                training.reason_code = s.reasoncode;
                training.total_hours = s.total_hours;
                training.completed_date = s.completed_date;
                training.created = s.created;
                training.training_category = s.training_category;
                trainings.push(training);
            }
        }
        return trainings.length > 0 ? trainings : null;
    }
}
exports.training_service = training_service;
//# sourceMappingURL=training_service.js.map