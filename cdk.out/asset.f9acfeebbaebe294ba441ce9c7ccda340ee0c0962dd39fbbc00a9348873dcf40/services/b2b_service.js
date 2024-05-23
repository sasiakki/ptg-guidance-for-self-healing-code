"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.b2b_service = void 0;
const models_1 = require("./../models");
const util_1 = require("util");
class b2b_service {
    static getEmployments(s) {
        const employments = new Array();
        if (!(0, util_1.isNullOrUndefined)(s.empstatus)
            && !(0, util_1.isNullOrUndefined)(s.trackingdate)
            && !(0, util_1.isNullOrUndefined)(s.categorycode)) {
            const employment = new models_1.Employment();
            employment.name = '';
            employment.status = s.empstatus;
            employment.hire_date = s.hiredate;
            employment.training_category = s.categorycode;
            employment.tc_tracking_date = (s.rehiredate && s.last_termination_date) ? s.rehiredate : s.trackingdate;
            employment.rehire_date = s.rehiredate;
            employment.terminate_date = s.last_termination_date;
            employments.push(employment);
        }
        return employments.length > 0 ? employments : null;
    }
    static getStatusSet(s) {
        const statusSet = new models_1.Student_status_set();
        statusSet.isGrandFathered = (s.exempt == 'true'
            || s.exempt == true)
            ? true : false;
        statusSet.ahcas_eligible = (s.ahcas_eligible == true
            || s.ahcas_eligible == 'true'
            || s.ahcas_eligible == 1
            || s.ahcas_eligible == '1')
            ? true : false;
        statusSet.isRehire = (s.rehiredate && s.last_termination_date) ? true : false;
        return statusSet;
    }
    static async getStudent(s) {
        const student = new models_1.Student();
        student.assigned_category = s.categorycode;
        student.id = s.personid.padStart(12, '0');
        student.birth_date = s.dob;
        student.prefer_language = s.language1;
        student.student_status_set = this.getStatusSet(s);
        student.employments = this.getEmployments(s);
        student.num_active_emp = s.empstatus == 'Active' ? 1 : 0;
        return student;
    }
}
exports.b2b_service = b2b_service;
//# sourceMappingURL=b2b_service.js.map