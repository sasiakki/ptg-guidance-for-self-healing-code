import {
  Student,
  Student_training,
  Student_status_set
} from '../models';
import { 
  Student_training_compliant_status_rule,
  Student_training_due_date_rule,
  Student_training_rules
} from '../bizlogics';
import { isNullOrUndefined } from 'util';
import { Constants } from './consts';
import { Helper } from '../helpers/helper';
import * as _ from 'lodash';

export class Student_training_logic {
  constructor() { }

  /**
   * ONLY one training from O/S, BT and CE should ever be Active
   */
  public static evaluateStudentTraining(
    student: Student,
    traininghistory: Student_training[]
  ): [Student_status_set, Student_training[], boolean] {

    let assignedTrainings: Student_training[] = [];
    let createdOrUpdatedTr: Student_training[] = null;
    let recalculateEligibility = false;

    // Dylan Glenn 14 May 2020
    //Update status field on any open trainings before beginning    
    //Helper.closeAllOpenTrainings(trainings);  // ? close all, comment out by Liza.Wu 07/15/2020
    let ss: Student_status_set = null;
    let trainings: Student_training[] = null;
    let permanentTrainingUpdates: Student_training[] = null;
    
    [ss, trainings, permanentTrainingUpdates] = Helper.validateStudentObject(student, traininghistory);
    student.student_status_set = ss;
    const initialIsCompliant = ss.isCompliant;

    // add permanentTrainingUpdates to assigned trainings for updating
    if (permanentTrainingUpdates && permanentTrainingUpdates.length > 0) {
      assignedTrainings.push(...permanentTrainingUpdates);
      console.log('permanent Trainings Updated: ', permanentTrainingUpdates);
    }

    console.log(`validate student object: ${JSON.stringify(student)}`);

    // Juhye.An, 04/17/2020:
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.CE_12.CODE,
                        Student_training_rules.isEligible(student, trainings, Constants.training_code.CE_12.CODE));
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`studentid: ${student.id}; push CE_12`);
      assignedTrainings.push(...createdOrUpdatedTr);
    }

    // Liza.Wu, 08/06/2019:
    /* Liza.Wu, 10/05/2020: Per CLC-689 to comment out Caregiver Learning Library
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.CE_OPEN_LIB.CODE,
                        Student_training_rules.isEligible(student, trainings, Constants.training_code.CE_OPEN_LIB.CODE));
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`push CE_OPEN_LIB`);
      assignedTrainings.push(createdOrUpdatedTr);
    } */

    // Tools for Calm
    // Dylan Glenn 13 May 2020
    // TerryP, 11/25/2020 (EQS-1298): close open training for Dec launch, will be revisited in the spring '21
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.MINDFUL_WC.CODE,
                        // Student_training_rules.isEligible(student, trainings, Constants.training_code.MINDFUL_WC.CODE)
                        Constants.eligible_training_status.CLOSE);
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`studentid: ${student.id}; push MINDFUL_WC`);
      assignedTrainings.push(...createdOrUpdatedTr);
    }

    // Liza.Wu, 09/27/2019: Add CBP
    // TerryP, 11/25/2020 (EQS-1298): close open training for Dec launch, will be revisited in the spring '21
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.CBP_WINTER2019.CODE,
                        // Student_training_rules.isEligible(student, trainings, Constants.training_code.CBP_WINTER2019.CODE)
                        Constants.eligible_training_status.CLOSE);
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`studentid: ${student.id}; push CBP_WINTER2019`);
      assignedTrainings.push(...createdOrUpdatedTr);
    }

    // Dylan Glenn 13 May 2020
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.OS.CODE,
                        Student_training_rules.isEligible(student, trainings, Constants.training_code.OS.CODE));
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`studentid: ${student.id}; push OS`);
      assignedTrainings.push(...createdOrUpdatedTr);
    }

    // Dylan Glenn 14 May 2020
    //Check EXEMPT BT FIRST and only process BT if not exempt
    /* Liza.Wu, 10/05/2020: Per CLC-689 to comment out EXEMPT_BT70 
    if (Student_training_rules.isEligible(student, trainings, Constants.training_code.EXEMPT_BT70.CODE)) {
      training.push(Student_training_due_date_rule.createNewTraining(student, Constants.training_code.EXEMPT_BT70.CODE));
    } else { */
    const btCode = Helper.determineBtType(student.assigned_category);
    if (btCode !== undefined) {
      //valid btCode
      createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                            btCode,
                            Student_training_rules.isEligible(student, trainings, btCode));
      if (!isNullOrUndefined(createdOrUpdatedTr)) {
        console.log(`studentid: ${student.id}; push BTs`);
        assignedTrainings.push(...createdOrUpdatedTr);
      }
    } else {
      //undefined btcode, close all open bt trainings
      const openBtTrainigs = Helper.getActiveBTTrainings(student.trainings);
      if (!isNullOrUndefined(openBtTrainigs))
        assignedTrainings.push(...Helper.closeAllOpenTrainings(openBtTrainigs));
    }

    // Dylan Glenn 13 May 2020
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.REFRESHER.CODE,
                        Student_training_rules.isEligible(student, trainings, Constants.training_code.REFRESHER.CODE));
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`studentid: ${student.id}; push REFRESHER`);
      assignedTrainings.push(...createdOrUpdatedTr);
    }

    //Dylan Glenn 15 June 2020
    createdOrUpdatedTr = Helper.createOrUpdateTraining(student,
                        Constants.training_code.AHCAS.CODE,
                        Student_training_rules.isEligible(student, trainings, Constants.training_code.AHCAS.CODE));
    if(!isNullOrUndefined(createdOrUpdatedTr)) {
      console.log(`studentid: ${student.id}; push AHCAS`);
      assignedTrainings.push(...createdOrUpdatedTr);
    }

    ss.isCompliant = Student_training_compliant_status_rule
                    .isCompliant(student, Helper.mergeTrainings(assignedTrainings, trainings));

    //send user through one more time if they went from non-compliant to compliant and no required active training;
    if (initialIsCompliant === false && ss.isCompliant){
      const requiredActiveTrainings = _.filter(assignedTrainings, t => t.status==='active' && t.is_required);
      recalculateEligibility = ((!requiredActiveTrainings || _.size(requiredActiveTrainings) === 0));
    };

    ss.complianceStatus = ss.isCompliant 
        ? Constants.compliant_status.COMPLIANT
        : Constants.compliant_status.NONCOMPLIANT;
    student.student_status_set = ss;

    console.log('assignedTrainings: ', assignedTrainings);

    return [ss, assignedTrainings, recalculateEligibility];
  }
}
