import { ValueObject, model, property } from '@loopback/repository';

@model()
export class Course_completion extends ValueObject {
  @property({
    type: 'string',
    required: true,
  })
  name?: string;

  @property({
    type: 'string',
    required: false,
  })
  status?: string;

  @property({
    type: 'date',
    required: false,
  })
  completed_date?: string;

  //@property({
  //  type: 'string',
  //  required: false,
  //})
  //publisher?: string;

  //@property({
  //  type: 'string',
  //  required: false,
  //})
  //sfId?: string;

  constructor(data?: Partial<Course_completion>) {
    super(data);
  }
}
