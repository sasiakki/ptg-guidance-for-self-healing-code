"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student_training_12hrce_rule = void 0;
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
class Student_training_12hrce_rule {
    constructor() { }
    static is12hrCEEligible(student, trainings) {
        let isEligible = false;
        let isGrandFathered = false;
        const requiresEmployment = true;
        const previousTrainingNotReqCredentials = [
            consts_1.Constants.credential_type.NAC.CODE,
            consts_1.Constants.credential_type.HCA.CODE,
            consts_1.Constants.credential_type.OSPI.CODE
        ];
        const validCredentialStatuses = [
            consts_1.Constants.credential_status.ACTIVE,
            consts_1.Constants.credential_status.EXPIRED,
            consts_1.Constants.credential_status.PENDING
        ];
        if (helper_1.Helper.hasCategory([consts_1.Constants.work_category.STANDARD_HCA, consts_1.Constants.work_category.ADULT_CHILD], student.assigned_category)
            && !helper_1.Helper.hasActiveCredential(helper_1.Helper.CE_EXEMPT_CREDENTIAL_CODES, student.credentials)) {
            if (helper_1.Helper.isGrandFathered(student)) {
                isEligible = true;
                isGrandFathered = true;
            }
            else if (student.assigned_category === consts_1.Constants.work_category.ADULT_CHILD) {
                if (helper_1.Helper.hasCredential(previousTrainingNotReqCredentials, student.credentials, validCredentialStatuses)
                    || helper_1.Helper.hasTakenOSAndBT(consts_1.Constants.training_code.BT_30.CODE, trainings)) {
                    isEligible = true;
                }
            }
            else if (student.assigned_category === consts_1.Constants.work_category.STANDARD_HCA
                && helper_1.Helper.hasCredential(previousTrainingNotReqCredentials, student.credentials, validCredentialStatuses)) {
                if (student.credentials[0].status === consts_1.Constants.credential_status.ACTIVE) {
                    isEligible = true;
                }
                else if (helper_1.Helper.expiredCredentialIsRenewable(student)) {
                    isEligible = true;
                }
            }
        }
        const ret = (isGrandFathered)
            ? consts_1.Constants.eligible_training_status.ACTIVATE
            : helper_1.Helper.setEligibleTrainingStatus(student, isEligible, requiresEmployment);
        console.log(`studentid: ${student.id}; is12hrCEEligible: ${isEligible}; eligibleTrainingStatus: ${ret}`);
        return ret;
    }
}
exports.Student_training_12hrce_rule = Student_training_12hrce_rule;
//# sourceMappingURL=student-training-12hrce.rule.js.map