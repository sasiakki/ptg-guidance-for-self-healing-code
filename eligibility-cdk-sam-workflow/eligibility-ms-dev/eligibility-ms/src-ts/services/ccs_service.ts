import {
    Course_completion,
  } from './../models';
  import { isNullOrUndefined } from 'util';
  
  
  export class ccs_service {
  
    public static getCourseCompletions(c: any): Course_completion[] {
        const coursecompletions: Course_completion[] = new Array<Course_completion>();
        for (const s of c){
            if(!isNullOrUndefined(s.name)
            &&!isNullOrUndefined(s.status)
            &&!isNullOrUndefined(s.completed_date)) {
                const coursecompletion: Course_completion = new Course_completion();
                coursecompletion.name = s.name;
                coursecompletion.status = s.status;
                coursecompletion.completed_date = s.completed_date;
                coursecompletions.push(coursecompletion);
            }
        }
        return coursecompletions.length > 0 ? coursecompletions : null;
    }
}