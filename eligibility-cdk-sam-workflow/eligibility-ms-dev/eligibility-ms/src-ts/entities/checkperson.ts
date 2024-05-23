import {BaseEntity, Column, Entity, PrimaryGeneratedColumn} from 'typeorm';

@Entity('check_person', { schema: 'eligibility'})
export class Check_person extends BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  pgc_id: number

  @Column({
      type: 'bigint',
      nullable: false
  })
  personid?: number;

  @Column({
    nullable: true 
  })
  type?: string;

  @Column({
    nullable: true
  })
  credentialstatus?: string;

  @Column({
    nullable: true
  })
  firstissuance?: string;

  @Column({
    nullable: true
  })
  expiration?: string;

  @Column({
    nullable: true
  })
  workercategory?: string;

  @Column({
    nullable: true
  })
  categorycode?: string;

  @Column({
    nullable: true
  })
  hiredate?: Date;

  @Column({
    nullable: true
  })
  exempt?: string;

  @Column({
    nullable: true
  })
  ahcas_eligible?: boolean;

  @Column({
    nullable: true
  })
  trackingdate?: Date;
  
  @Column({
    nullable: true
  })
  empstatus?: string;

  @Column({
    nullable: true
  })
  dob?: string;

  @Column({
    nullable: true
  })
  language1?: string;

  @Column({
    default: 0
  })
  check_stat?: number;

  @Column({
    default: 0
  })
  rehiredate?: Date;


  @Column({
    default: 0
  })
  last_termination_date?: Date;
}