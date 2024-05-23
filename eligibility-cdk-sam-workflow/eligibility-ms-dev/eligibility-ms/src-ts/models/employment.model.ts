import { ValueObject, model, property } from '@loopback/repository';

@model()
export class Employment extends ValueObject {
  @property({
    type: 'string',
    required: false,
  })
  name?: string;

  @property({
    type: 'string',
    required: true,
  })
  status: string;

  @property({
    type: 'date',
    required: true,
  })
  hire_date: string;

  @property({
    type: 'date',
    required: true,
  })
  rehire_date: string;

  @property({
    type: 'date',
    required: false,
  })
  terminate_date?: string;

  //@property({
   // type: 'date',
   // required: false,
  //})
  //authentication_date?: string;

  @property({
    type: 'string',
    required: true,
  })
  training_category: string;

  @property({
    type: 'date',
    required: true,
  })
  tc_tracking_date: string;

  //@property({
   // type: 'boolean',
   // required: false,
  //})
  //ignore_assigned_category?: boolean;

  constructor(data?: Partial<Employment>) {
    super(data);
  }
}
