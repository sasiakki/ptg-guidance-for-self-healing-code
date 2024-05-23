import {
    Student_status_set,
    Student,
    Employment,
  } from './../models';
  import { isNullOrUndefined } from 'util';
  
  
  export class b2b_service {
  
    private static getEmployments(s: any): Employment[] {
        const employments: Employment[] = new Array<Employment>();
        if(!isNullOrUndefined(s.empstatus)
        &&!isNullOrUndefined(s.trackingdate)
        &&!isNullOrUndefined(s.categorycode)) {
          const employment: Employment = new Employment();
          employment.name = '';
          employment.status = s.empstatus;
          //employment.hire_date = s.trackingdate;
          employment.hire_date = s.hiredate; 
          employment.training_category = s.categorycode;
          //employment.tc_tracking_date = s.trackingdate;
          employment.tc_tracking_date = (s.rehiredate && s.last_termination_date) ? s.rehiredate : s.trackingdate;
          employment.rehire_date = s.rehiredate;
          employment.terminate_date = s.last_termination_date;
          employments.push(employment);
        }
        return employments.length > 0 ? employments : null;
      }
    
      private static getStatusSet(s: any): Student_status_set {
        const statusSet: Student_status_set = new Student_status_set();
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
    
      public static async getStudent(s: any): Promise<Student> {
        const student: Student = new Student();
        student.assigned_category = s.categorycode;
        student.id = s.personid.padStart(12, '0'); // match SF learner id with DEX learner id which is dropping leading 0s
        student.birth_date = s.dob;
        student.prefer_language = s.language1;
        student.student_status_set = this.getStatusSet(s);
        student.employments = this.getEmployments(s);
        student.num_active_emp = s.empstatus == 'Active' ? 1 : 0;
        return student;
      }
}