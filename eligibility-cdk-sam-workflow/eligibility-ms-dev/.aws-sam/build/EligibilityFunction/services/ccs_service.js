"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ccs_service = void 0;
const models_1 = require("./../models");
const util_1 = require("util");
class ccs_service {
    static getCourseCompletions(c) {
        const coursecompletions = new Array();
        for (const s of c) {
            if (!(0, util_1.isNullOrUndefined)(s.name)
                && !(0, util_1.isNullOrUndefined)(s.status)
                && !(0, util_1.isNullOrUndefined)(s.completed_date)) {
                const coursecompletion = new models_1.Course_completion();
                coursecompletion.name = s.name;
                coursecompletion.status = s.status;
                coursecompletion.completed_date = s.completed_date;
                coursecompletions.push(coursecompletion);
            }
        }
        return coursecompletions.length > 0 ? coursecompletions : null;
    }
}
exports.ccs_service = ccs_service;
//# sourceMappingURL=ccs_service.js.map