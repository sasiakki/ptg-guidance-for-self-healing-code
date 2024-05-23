import { ValueObject, model, property } from '@loopback/repository';

@model()
export class Student_status_set extends ValueObject {

  @property({
    type: 'string',
    required: false,
  })
  studentId?: string;

  @property({
    type: 'boolean',
    required: false,
  })
  isCompliant?: boolean;

  @property({
    type: 'boolean',
    required: false,
  })
  isGrandFathered?: boolean;

  @property({
    type: 'boolean',
    required: false,
  })
  ahcas_eligible?: boolean;

  @property({
    type: 'string',
    required: false,
  })
  complianceStatus?: string;

  @property({
    type: 'boolean',
    required: false,
  })
  isRehire?: boolean;

  @property({
    type: 'boolean',
    required: false,
  })
  isCredentialExpired?: boolean;

  constructor(data?: Partial<Student_status_set>) {
    super(data);
  }
}
