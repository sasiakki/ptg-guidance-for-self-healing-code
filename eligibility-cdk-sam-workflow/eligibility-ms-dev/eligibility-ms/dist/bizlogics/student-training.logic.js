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
exports.Student_training_logic = void 0;
const bizlogics_1 = require("../bizlogics");
const util_1 = require("util");
const consts_1 = require("./consts");
const helper_1 = require("../helpers/helper");
const _ = __importStar(require("lodash"));
class Student_training_logic {
    constructor() { }
    static evaluateStudentTraining(student, traininghistory) {
        let assignedTrainings = [];
        let createdOrUpdatedTr = null;
        let recalculateEligibility = false;
        let ss = null;
        let trainings = null;
        let permanentTrainingUpdates = null;
        [ss, trainings, permanentTrainingUpdates] = helper_1.Helper.validateStudentObject(student, traininghistory);
        student.student_status_set = ss;
        const initialIsCompliant = ss.isCompliant;
        if (permanentTrainingUpdates && permanentTrainingUpdates.length > 0) {
            assignedTrainings.push(...permanentTrainingUpdates);
            console.log('permanent Trainings Updated: ', permanentTrainingUpdates);
        }
        console.log(`validate student object: ${JSON.stringify(student)}`);
        createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, consts_1.Constants.training_code.CE_12.CODE, bizlogics_1.Student_training_rules.isEligible(student, trainings, consts_1.Constants.training_code.CE_12.CODE));
        if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
            console.log(`studentid: ${student.id}; push CE_12`);
            assignedTrainings.push(...createdOrUpdatedTr);
        }
        createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, consts_1.Constants.training_code.MINDFUL_WC.CODE, consts_1.Constants.eligible_training_status.CLOSE);
        if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
            console.log(`studentid: ${student.id}; push MINDFUL_WC`);
            assignedTrainings.push(...createdOrUpdatedTr);
        }
        createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, consts_1.Constants.training_code.CBP_WINTER2019.CODE, consts_1.Constants.eligible_training_status.CLOSE);
        if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
            console.log(`studentid: ${student.id}; push CBP_WINTER2019`);
            assignedTrainings.push(...createdOrUpdatedTr);
        }
        createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, consts_1.Constants.training_code.OS.CODE, bizlogics_1.Student_training_rules.isEligible(student, trainings, consts_1.Constants.training_code.OS.CODE));
        if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
            console.log(`studentid: ${student.id}; push OS`);
            assignedTrainings.push(...createdOrUpdatedTr);
        }
        const btCode = helper_1.Helper.determineBtType(student.assigned_category);
        if (btCode !== undefined) {
            createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, btCode, bizlogics_1.Student_training_rules.isEligible(student, trainings, btCode));
            if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
                console.log(`studentid: ${student.id}; push BTs`);
                assignedTrainings.push(...createdOrUpdatedTr);
            }
        }
        else {
            const openBtTrainigs = helper_1.Helper.getActiveBTTrainings(student.trainings);
            if (!(0, util_1.isNullOrUndefined)(openBtTrainigs))
                assignedTrainings.push(...helper_1.Helper.closeAllOpenTrainings(openBtTrainigs));
        }
        createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, consts_1.Constants.training_code.REFRESHER.CODE, bizlogics_1.Student_training_rules.isEligible(student, trainings, consts_1.Constants.training_code.REFRESHER.CODE));
        if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
            console.log(`studentid: ${student.id}; push REFRESHER`);
            assignedTrainings.push(...createdOrUpdatedTr);
        }
        createdOrUpdatedTr = helper_1.Helper.createOrUpdateTraining(student, consts_1.Constants.training_code.AHCAS.CODE, bizlogics_1.Student_training_rules.isEligible(student, trainings, consts_1.Constants.training_code.AHCAS.CODE));
        if (!(0, util_1.isNullOrUndefined)(createdOrUpdatedTr)) {
            console.log(`studentid: ${student.id}; push AHCAS`);
            assignedTrainings.push(...createdOrUpdatedTr);
        }
        ss.isCompliant = bizlogics_1.Student_training_compliant_status_rule
            .isCompliant(student, helper_1.Helper.mergeTrainings(assignedTrainings, trainings));
        if (initialIsCompliant === false && ss.isCompliant) {
            const requiredActiveTrainings = _.filter(assignedTrainings, t => t.status === 'active' && t.is_required);
            recalculateEligibility = ((!requiredActiveTrainings || _.size(requiredActiveTrainings) === 0));
        }
        ;
        ss.complianceStatus = ss.isCompliant
            ? consts_1.Constants.compliant_status.COMPLIANT
            : consts_1.Constants.compliant_status.NONCOMPLIANT;
        student.student_status_set = ss;
        console.log('assignedTrainings: ', assignedTrainings);
        return [ss, assignedTrainings, recalculateEligibility];
    }
}
exports.Student_training_logic = Student_training_logic;
//# sourceMappingURL=student-training.logic.js.map