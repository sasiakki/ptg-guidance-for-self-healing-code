import { Student, Student_training } from '../models';
import { Constants } from './consts';
import { Helper } from '../helpers/helper';
import * as _ from 'lodash';

export class Student_training_ebt_rule {
    constructor() { }

    /**
     * 
     * @param student 
     * @param trainings 
     * 
     * Student is eligible for the Exempt BT if they are
     * 1. In Compliance **AND**
     * 2a. Exempt by Employment **OR**
     * 2b. Have proper Work Category
     */
    public static isEbtEligible(
        student: Student,
        trainings: Student_training[]
    ): boolean {
        console.log('>>>>>>check Exempt BT');
        //An array of the work category codes that are valid for this training
        const validWorkCategories = [
            Constants.work_category.ADULT_CHILD,
            Constants.work_category.PARENT_PROVIDER_DDD,
            Constants.work_category.DDD_NDDD,
            Constants.work_category.RESPITE,
            Constants.work_category.LIMITED_SERVICE_PROVIDER
        ];
        if (
            !Helper.isInCompliance(student)
            ||
            Helper.studentValuesNullOrUndefined([
                student.assigned_category,
                trainings
            ])
        ) {
            return false;
        }
        if(
            Helper.isInCompliance(student) 
            &&
            (
                Helper.isGrandFathered(student)
                ||
                validWorkCategories.includes(student.assigned_category)
            )
        ) {
            console.log('student is eligible, creating new Exempt BT training...');
            return true;
        }
        return false;
    }
}
