import { ValueObject, model, property } from '@loopback/repository';

@model()
export class Credential extends ValueObject {
  @property({
    type: 'string',
    required: true,
  })
  name: string;

  @property({
    type: 'string',
    required: true,
  })
  status: string;

  @property({
    type: 'date',
    required: false,
  })
  firstIssuance_date: string;

  @property({
    type: 'date',
    required: false,
  })
  expiration_date: string;

  @property({
    type: 'string',
    required: true,
  })
  credential_number: string;

  constructor(data?: Partial<Credential>) {
    super(data);
  }
}
