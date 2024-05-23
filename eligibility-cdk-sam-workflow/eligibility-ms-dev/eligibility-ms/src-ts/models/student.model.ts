import { Entity, model, property, hasMany } from '@loopback/repository';
import { Student_training } from './student-training.model';
import { Credential } from './credential.model';
import { Employment } from './employment.model';
import { Student_status_set } from './student-status-set.model';
import { Course_completion } from './course-completion.model'

@model()
export class Student extends Entity {

  @property({
    type: 'string',
    id: true,
    required: true,
  })
  id: string;

  @property({
    type: 'string',
  })
  provider_id?: string;

  @property({
    type: 'string'
  })
  first_name?: string;

  @property({
    type: 'string'
  })
  last_name?: string;

  @property({
    type: 'string'
  })
  training_status?: string;

  @property({
    type: 'string'
  })
  status?: string;

  // @property({
  //   type: 'string'
  // })
  // publisher?: string;

  @property({
    type: 'string'
  })
  active_training?: string;

  @property({
    type: 'string'
  })
  assigned_category?: string;

  @property({
    type: 'number'
  })
  num_active_emp?: number;

  @property({
    type: 'string'
  })
  prefer_language?: string;
  
  @property({
    type:'date'
  })
  birth_date?: string;

  @property({
    type: Student_status_set
  })
  student_status_set?: Student_status_set;

  @property.array(Credential)
  credentials?: Credential[];

  @property.array(Employment)
  employments?: Employment[];

  @property.array(Course_completion)
  course_completions?: Course_completion[];

  @hasMany(() => Student_training)
  trainings?: Student_training[];

  constructor(data?: Partial<Student>) {
    super(data);
  }

  /**
   * calculate student training
   */
  public name() {

  }
}
