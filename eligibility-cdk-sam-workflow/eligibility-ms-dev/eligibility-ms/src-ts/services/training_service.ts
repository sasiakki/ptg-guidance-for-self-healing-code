import {
    Student_training,
  } from './../models';
  import { isNullOrUndefined } from 'util';
  
  export class training_service {
  
    public static getTrainings(t: any): Student_training[] {
        const trainings: Student_training[] = new Array<Student_training>();
        for (const s of t){
            if (!isNullOrUndefined(s.train_id) && !isNullOrUndefined(s.status) && !isNullOrUndefined(s.training_code)){
                const training: Student_training = new Student_training();
                training.id = s.train_id;
                training.benefit_continuation_due_date = s.benefit_continuation_due_date;
                training.studentId = s.studentId;
                training.status = s.status;
                training.name = s.training_category;
                training.training_code = s.training_code;
                training.is_required = s.is_required;
                training.required_hours = s.required_hours;
                training.tracking_date = s.tracking_date;
                training.due_date = s.due_date;
                training.earned_hours = s.earned_hours;
                training.transfer_hours = s.transfer_hours;
                training.archived = s.archived;
                training.reason_code = s.reasoncode;
                training.total_hours = s.total_hours;
                training.completed_date = s.completed_date;
                training.created = s.created;
                training.training_category = s.training_category;          
                trainings.push(training);
            }
        }
        return trainings.length > 0 ? trainings : null;
    }
}

