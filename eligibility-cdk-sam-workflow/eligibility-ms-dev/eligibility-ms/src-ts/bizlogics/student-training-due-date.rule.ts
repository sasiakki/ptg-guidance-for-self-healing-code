import {
  Student,
  Credential,
  Student_training
} from '../models'
import { isNullOrUndefined } from 'util';
import { Constants } from './consts';
import moment = require('moment');
import * as _ from 'lodash';
import { Helper } from '../helpers/helper';
import { IoTJobsDataPlane } from 'aws-sdk';

export class Student_training_due_date_rule {

  constructor() { }

  public static createNewTraining(student: Student, training_code: string)
    : Student_training {

    let newTraining = new Student_training();
    const cTrs =  _.filter(
      student.trainings,
      {
        training_code
      }
    );
    let ind: number = cTrs.length > 0 ? _.max(_.map(cTrs, x=> Number(x.id.split('-')[2]))) + 1 : 1;
    newTraining.id = student.id + '-' + training_code + '-' + ind;
    newTraining.training_code = training_code;
    newTraining.status = Constants.training_status.ACTIVE;
    let required_hours = _.find(Constants.training_code,
      ['CODE', training_code]).HOURS;
    if (required_hours !== '') {
      newTraining.required_hours = Number(required_hours);
    }
    newTraining.name = _.find(Constants.training_code,
      ['CODE', training_code]).NAME;

      
    let benefitContinuationDueDate: Date | null | undefined = undefined;
    let dueDate: Date | null | undefined = undefined;
    let trackingDate: Date | null | undefined = undefined;
    let trkDate: Date = (!isNullOrUndefined(student.employments) && 
                        student.employments.length>0)
                      ? moment(student.employments[0].tc_tracking_date).toDate()
                      : moment().toDate();

    [trackingDate, dueDate] = Student_training_due_date_rule
      .getTrackingDateAndDueDate
      (student,
        newTraining,
        student.assigned_category,
        trkDate
      );
    newTraining.tracking_date = trackingDate != undefined
      ? moment(trackingDate).toISOString()
      : undefined;
    newTraining.due_date = dueDate != undefined
      ? moment(dueDate).toISOString()
      : undefined;
    newTraining.benefit_continuation_due_date = null;
    newTraining.created = moment().utc().toISOString();
    newTraining.is_required = _.find(Constants.training_code,
      ['CODE', training_code]).REQUIRED;
    newTraining.studentId = student.id;
    console.log(`studentid: ${student.id}; new training created: ${JSON.stringify(newTraining)}`);
    return newTraining;
  }


  public static getTrackingDateAndDueDate(student: Student,
    training: Student_training, category: String, trkDate?: Date)
    : [Date, Date | null | undefined] {

    let trackingDate: Date = trkDate;
    let dueDate: Date | null | undefined = undefined;

    switch (training.training_code) {
      case Constants.training_code.BT_7.CODE:
      case Constants.training_code.BT_9.CODE:
      case Constants.training_code.BT_30.CODE:
      case Constants.training_code.BT_42.CODE:
      case Constants.training_code.BT_70.CODE:
        dueDate = new Student_training_due_date_rule()
          .getBasicTrainingDueDate(trackingDate);
        break;
      case Constants.training_code.CE_12.CODE:
        dueDate = new Student_training_due_date_rule()
          .getContinuingEducationDueDate(student, category);
        trackingDate = moment(dueDate).add(-1, 'years').toDate();
        
        break;
      default:
        dueDate = undefined;
        trackingDate = undefined;
    }
    return [trackingDate, dueDate];
  }

  private getBasicTrainingDueDate(trackingDate: Date): Date | null {
    return moment(trackingDate).add(119, 'days').toDate();
  }

  private getContinuingEducationDueDate(student: Student,
    category: String)
    : Date | null | undefined {
    let lastCompletedTraining: Student_training = this.getLastCompletedTraining(student);
    let isFirstCE = !(this.isContinuingEducation(lastCompletedTraining));
    let nextDOB = this.getNextBirthDate(student);
    let nextDOBplusOne = moment(nextDOB).add(1, 'years').toDate();
    let lastCompletedDateYrDOBplusOne: Date = (lastCompletedTraining) ? moment(nextDOB).year(moment(lastCompletedTraining.completed_date).add(1, 'years').year()).utc().startOf('day').toDate() : null;

    if (process.env.IS_LOCAL) {
      console.log('\n**************************');
      console.log('lastCompletedTraining: ', lastCompletedTraining);
      console.log('isFirstCE: ', isFirstCE);
      console.log('nextDOB: ', nextDOB);
      console.log('nextDOB + 1 yr: ', nextDOBplusOne);
      console.log('lastCompletedDateYrDOB + 1 yr: ', lastCompletedDateYrDOBplusOne);
      console.log('lastCompletedDateYrDOB + 1 yr difference with lastCompletedDate:', (lastCompletedTraining && lastCompletedDateYrDOBplusOne) ? moment(lastCompletedDateYrDOBplusOne).diff(moment(lastCompletedTraining.completed_date), 'days') : 0 , 'days');
      console.log('**************************\n');
    }

    if (isFirstCE) {
      switch (category) {
        case Constants.work_category.ADULT_CHILD:
          /*
           * nextDOB if lastcompleted is not BT30;
           * due date set to learner’s birthday of completed BT30 year + 1;
           * add another year if completeddate and new duedate are within the grace period (in days)
           */
          if (lastCompletedTraining && Helper.isSpecificTraining(lastCompletedTraining, Constants.training_code.BT_30.CODE)) {
            return lastCompletedDateYrDOBplusOne;
          } else {
            return nextDOB;
          }
        case Constants.work_category.STANDARD_HCA:
          // have credentials or grandfathered
          if (!isNullOrUndefined(student.credentials)) {
            // grab first credential
            const credential = student.credentials[0];
            if (credential){
              const credentialExpirationDate = moment(credential.expiration_date).utc().startOf('day');

              if (process.env.IS_LOCAL) {
                console.log('\n**************************');
                console.log('Credential \t', credential.name);
                console.log('CredentialStatus \t', credential.status);
                console.log('CredentialExpiration \t', credentialExpirationDate.toDate());
                console.log('**************************\n');
              }

              // active credential
              if (credential.status === Constants.credential_status.ACTIVE) {

                // HCA|NAC: 
                if (_.includes([Constants.credential_type.HCA.CODE, Constants.credential_type.NAC.CODE], credential.name)) {
                  /*** due date is set to active credential expiration date ***/
                  if (process.env.IS_LOCAL) console.log('!!! FirstCE, SHCA with HM|NC credential, assign to the expiration date !!!\n');
                  return credentialExpirationDate.toDate();

                // OSPI:
                } else if (credential.name === Constants.credential_type.OSPI.CODE){
                    /*
                    * Added as part of MDL-570: 
                    * For OSPI credential first CE calculation:
                    * For newly OSPI credential CE due date is provider’s next birthday
                    */
                  if (process.env.IS_LOCAL) console.log('!!! OSPI credential, providers next birthday !!!\n');
                  return nextDOB;
                } else {
                  if (process.env.IS_LOCAL) console.log('!!! possible exempt user with invalid credentials, providers next birthday !!!\n');
                  return nextDOB;
                }
              // expired|pending credential
              } else if (_.includes([Constants.credential_status.EXPIRED, Constants.credential_status.PENDING], credential.status)) {
                  if (_.includes([Constants.credential_type.HCA.CODE, Constants.credential_type.NAC.CODE], credential.name)){
                    if (process.env.IS_LOCAL) console.log('!!! expired | pending HM|NC credential, use credential expiration date as due date !!!\n');
                    return credentialExpirationDate.toDate();
                  }
                  else {
                    if (process.env.IS_LOCAL) console.log('!!! expired | pending NON-(HM|NC) credential, use birthday of expiration date year as due date !!!\n');
                    return this.getCredentialExpirationCEDueDate(student, credential.expiration_date);
                  }
              } else { 
                //credential other than expired, pending or active;
                return undefined;
              }
            }

          // exempt user w/ no credentials
          } else if (!isNullOrUndefined(student.student_status_set) && student.student_status_set.isGrandFathered) {
            /*
             * Exempt by employment CE due date:
             * CE is due the first birthday after hire date
             * CE due date should be using next birthday
             */
            if (process.env.IS_LOCAL) console.log('!!! no credentials but exempt by employment, is next birthday !!!\n');
            return nextDOB;
          } else {
            if (process.env.IS_LOCAL) console.log('!!! no credentials and not exempt, set to undefined !!!\n');
            return undefined; //this should error (you don't have credentials or an exempt status)
          }
          break;
        default:
          if (process.env.IS_LOCAL) console.log('!!! only adch and shca are valid working types, set to undefined !!!\n');
          return undefined; // Should not get here; For any learner, only ADCH or SHCA are valid working types to trigger CE;
      }
    } else {
      // * Set DEFAULT dueDate if not firstCE
      // historical data: not all ce trs had due_dates
      let dueDate = (lastCompletedTraining.due_date) 
        ? moment(lastCompletedTraining.due_date).add(1, 'years').toDate()
        : nextDOB;
      
      /* SHCA rehire|non-rehire w/ HM | NC (pending | expired OR active and rehired) credentials use credential expiration date */
      if (category === Constants.work_category.STANDARD_HCA 
        && student.credentials 
        && _.includes([Constants.credential_type.HCA.CODE, Constants.credential_type.NAC.CODE], student.credentials[0].name)) {
        if (student.student_status_set.isCredentialExpired===true //expired or pending with expiration date credential
          || (student.credentials[0].status === Constants.credential_status.ACTIVE 
            && (student.student_status_set.isRehire === true))) {
          const credentialExpDate = moment(student.credentials[0].expiration_date).utc().startOf('day');
          const lastcompletedTrainingDueDate = moment(lastCompletedTraining.due_date).utc().startOf('day');

          // fast forward due date to credential expiration date
          if (lastcompletedTrainingDueDate.year() < credentialExpDate.year()) {
              if (process.env.IS_LOCAL) console.log(`!!! SHCA and rehire w/ ${student.credentials[0].status} ${student.credentials[0].name} credential, assign duedate to cred expiration date !!!\t`);
              dueDate = credentialExpDate.toDate();
          }
        }
      }

      /* Standard HCA who are 1163 exempt OR Adult Child Providers, CE for every year they work */
      if ((category === Constants.work_category.ADULT_CHILD || student.student_status_set.isGrandFathered)
        && lastCompletedTraining.due_date 
        && student.student_status_set.isRehire === true ) {
          // check last completion against termination due date year; 
          // if year is before termination date year take default action of adding 1 year to last completed; 
          // if term year and before hire date;
          const tmpLastCompletedTraining = moment(lastCompletedTraining.due_date).utc().startOf('day');
          const terminationDateYear = moment(student.employments[0].terminate_date).utc().startOf('day').year();
          const rehireYear = moment(student.employments[0].rehire_date).utc().startOf('day').year();
          if (tmpLastCompletedTraining.year() >= terminationDateYear && tmpLastCompletedTraining.year() < rehireYear){
            dueDate = tmpLastCompletedTraining.year(rehireYear).utc().startOf('day').toDate();
            if (process.env.IS_LOCAL) console.log('!!! ADCH and Rehire duedate !!!\t', dueDate);
          }
      }

      return dueDate
    }
  }

  /*
  Credential expiration dates fall on learner's birthday; updated logic to adjust if it does not, take dob on expiration date year
  */
  private getCredentialExpirationCEDueDate(student: Student, expirationDate: string): Date {
    const expirationDay = moment(expirationDate).utc().startOf('day');
    const dob = student.birth_date;
    let expirationDOB = moment(dob).utc().startOf('day').year(expirationDay.year());

    // if (process.env.IS_LOCAL) console.log('expirationDay.isBefore(expirationDOB)', expirationDay, expirationDOB, expirationDay.isBefore(expirationDOB));
    // if (expirationDay.isBefore(expirationDOB)) expirationDOB = expirationDOB.year(expirationDay.year() - 1);
    return expirationDOB.toDate();
  }

  private getNextBirthDate(student: Student): Date {
    const today = moment().utc().startOf('day');
    const dob = student.birth_date;
    let nextDOB = moment(dob).utc().startOf('day').year(today.year());

    if (process.env.IS_LOCAL) console.log('\n***\ntoday:', today, '>=', 'nextDOB:', nextDOB, ':', today.isSameOrAfter(nextDOB), '\n***');
    if (today.isSameOrAfter(nextDOB)) nextDOB = nextDOB.year(today.year() + 1);
    return nextDOB.toDate();
  }

  // same for all learners: Grandfathered||isHCA||isNAC||no creds... lookup CE code; 
  private isContinuingEducation(lastCompletedTraining: Student_training): boolean {
    return Helper.isSpecificTraining(lastCompletedTraining, Constants.training_code.CE_12.CODE);
  }

  private getLastCompletedTraining(student: Student): Student_training | null {
    let training: Student_training = null;
    if (!isNullOrUndefined(student.trainings)) {
      let completedTrainings = _.filter(
        student.trainings,
        t => Helper.trainingIsClosedByComplete(t) && t.is_required);

      if (!isNullOrUndefined(completedTrainings)
        && _.size(completedTrainings) > 0) {
        let sorted = _.sortBy(completedTrainings, 'completed_date').reverse();
        training = _.head(sorted);

        /*
        OJT awards the training credits with completion date = due date for the year in which the credits are granted.
        When this happens - and the earlier CEs are being completed more contemporarily because of the due date extensions
        the earlier CEs will show as completed AFTER later CEs, causing a CE with a redundant due_date

        lastCompleted CE shifts to latest due_date of the completed CEs
        */
        if (this.isContinuingEducation(training)){
          const completedCEs = _.filter(completedTrainings, t=> _.includes( [Constants.training_code.CE_12.CODE],t.training_code));
          // completed CE with the latest due_date
          training = _.head(_.sortBy(completedCEs, 'due_date').reverse()); 
        }
      }
    }
    return training;
  }

  private checkIsHCAandNAC(student: Student): [boolean, boolean] {
    let isHCA: boolean = false;
    let isNAC: boolean = false;
    if (!isNullOrUndefined(student.credentials)) {
      let credHCA: Credential = student.credentials
        .filter
        (
          c => c.name == Constants
            .credential_type
            .HCA.CODE
        )[0];
      isHCA = (!isNullOrUndefined(credHCA)
        && credHCA.status == Constants.credential_status.ACTIVE)
        ? true : false;
      let credNAC: Credential = student.credentials
        .filter
        (
          c => c.name == Constants
            .credential_type
            .NAC.CODE
        )[0];
      isNAC = (!isNullOrUndefined(credNAC)
        && credNAC.status == Constants.credential_status.ACTIVE)
        ? true : false;
    }
    return [isHCA, isNAC];
  }

  /*
    function to check if the incoming credential is of OSPI type
  */
  private checkIsOSPI(student: Student): boolean {
    let isOSPI: boolean = false;
    if (!isNullOrUndefined(student.credentials)) {
      let credOSPI: Credential = Helper.getCredentialByType (student, Constants.credential_type.OSPI.CODE);
      isOSPI = (!isNullOrUndefined(credOSPI)
        && credOSPI.status == Constants.credential_status.ACTIVE)
        ? true : false;
    }
    return isOSPI;
  }
}
