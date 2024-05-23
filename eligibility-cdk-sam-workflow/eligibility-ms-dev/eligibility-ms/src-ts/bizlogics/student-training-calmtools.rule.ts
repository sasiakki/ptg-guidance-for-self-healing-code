import {
  Student,
  Student_training
} from '../models';
import { Helper } from '../helpers/helper';
import { Constants } from './consts';

export class Student_training_calmtools_rule {

  constructor() {}

  public static isCalmToolsEligible(student: Student,
    trainings: Student_training[])
    : boolean {
      //eligible based on worker category AND completed OS & BT trainings
      const validWorkerCategoryWithOSBT: string[] = [
        Constants.work_category.LIMITED_SERVICE_PROVIDER,
        Constants.work_category.PARENT_PROVIDER_DDD,
        Constants.work_category.DDD_NDDD,
        Constants.work_category.RESPITE
      ];
      //eligible based on worker category and EITHER OS & BT **OR** credential
      const validWorkerCategoryWithOSBTOrCredential: string[] = [
        Constants.work_category.STANDARD_HCA,
        Constants.work_category.ADULT_CHILD
      ];
      console.log('>>>>>>check CalmTools');

      if(Helper.isInCompliance(student)) {
        if(
          validWorkerCategoryWithOSBTOrCredential.includes(student.assigned_category)
          &&
          (
            Helper.hasTakenOSAndBT(Helper.determineBtType(student.assigned_category), trainings)
            ||
            Helper.isExemptFromOSAndBTByCredential(student)
          )
          ) {
          console.log('student is eligible for Tools for Calm, creating...');
          return true;
        } else if(
          validWorkerCategoryWithOSBT.includes(student.assigned_category) 
          &&
          Helper.hasTakenOSAndBT(Helper.determineBtType(student.assigned_category), trainings)
          ) {
          console.log('student is eligible for Tools for Calm, creating...');
          return true;
        }
      }
      return false;
  }
}
