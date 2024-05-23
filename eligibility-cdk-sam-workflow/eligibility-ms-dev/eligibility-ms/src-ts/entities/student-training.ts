import { BaseEntity, Column, PrimaryGeneratedColumn, Entity, ManyToOne, JoinColumn } from 'typeorm';
import { Studente } from './student';

// training_requirement

@Entity('student_training', {schema: 'eligibility'})
export class Student_traininge extends BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  cc_id: number

  @Column({
    nullable: false,
  })
  studentId?: string;

  @Column({
    nullable: false
  })
  training_code?: string;

  @Column({
    nullable: true 
  })
  name?: string;
  
  @Column({
    nullable: false
  })
  status?: string;

  @Column({
    nullable: true
  })
  due_date?: string;

  @Column({
    nullable: true
  })
  tracking_date?: string;

  // @Column({
  //   nullable: true
  // })
  // eligibility_date?: string;

  // @Column({
  //   nullable: true
  // })
  // start_date?: string;

  @Column({
    nullable: true
  })
  completed_date?: string;

  @Column({
    nullable: true
  })
  training_category?: string;

  @Column({
    nullable: true
  })
  required_hours?: number;

  @Column({
    nullable: true
  })
  earned_hours?: number;

  @Column({
    nullable: true
  })
  transfer_hours?: number;


  @Column({
    nullable: true
  })
  total_hours?: number;

  @Column({
    nullable: true
  })
  sfId?: string;

  //@Column({
  //  nullable: true
  //})
  //publisher?: string;
  
  @Column({
    nullable: true,
    default: null
  })
  benefit_continuation_due_date?: string;
  
  @Column({
    nullable: true
  })
  created?: string;

  @Column({
    nullable: true
  })
  reasoncode?: string;
  
  @Column({
    nullable: true
  })
  archived?: string;
  
  @Column({
    nullable: true
  })
  is_required?: boolean;
  
  @Column({
    nullable: true,
  })
  train_id?: string; 

  @ManyToOne(() => Studente, student => student.trainings)
  @JoinColumn({
    referencedColumnName: 'id'
  })
  student?: Studente;

}
