import { Entity, model, property, belongsTo } from '@loopback/repository';
import { Student } from './student.model';

@model()
export class Student_training extends Entity {

  @belongsTo(() => Student)
  studentId: string;

  @property({
    type: 'string',
    required: true,
  })
  training_code: string;

  @property({
    type: 'string',
    required: false,
  })
  name?: string;
  
  @property({
    type: 'string',
    required: true,
  })
  status?: string;

  @property({
    type: 'date',
  })
  due_date?: string;

  @property({
    type: 'date',
  })
  tracking_date?: string;

 // @property({
  //  type: 'date',
  //  required: false,
  //})
  //eligibility_date?: string;

  //@property({
   // type: 'date',
   // required: false,
  //})
  //start_date?: string;

  @property({
    type: 'date',
    required: false,
  })
  completed_date?: string;

  @property({
    type: 'string',
  })
  training_category?: string;

  @property({
    type: 'number',
    required: false,
  })
  required_hours?: number;

  @property({
    type: 'number',
    required: false,
  })
  earned_hours?: number;

  @property({
    type: 'number',
    required: false,
  })
  transfer_hours?: number;

  @property({
    type: 'number',
    required: false,
  })
  total_hours?: number;

  //@property({
   // type: 'string',
    //required: false,
  //})
  //sfId?: string;

  //@property({
   // type: 'string',
   // required: false,
  //})
  //publisher: string;
  
  @property({
    type: 'date',
    required: false,
  })
  benefit_continuation_due_date?: string;
  
  @property({
    type: 'date',
    required: false,
  })
  created?: string;
  
  @property({
    type: 'date',
    required: false,
  })
  archived?: string;
  
  @property({
    type: 'boolean',
    required: false,
  })
  is_required?: boolean;

  @property({
    type: 'string',
    required: true,
  })
  reason_code: string;
  
  @property({
    type: 'string',
    id: true,
  })
  id: string;

  getId() {
    return this.id;
  }

  constructor(data?: Partial<Student_training>) {
    super(data);
  }
}
