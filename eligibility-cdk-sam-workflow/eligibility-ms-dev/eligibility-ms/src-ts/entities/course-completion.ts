import {BaseEntity, Column, Entity, PrimaryGeneratedColumn, ManyToOne, JoinColumn} from 'typeorm';
import { Studente } from './student';

// raw.ss_course_completion

@Entity('course_completion', { schema: 'eligibility'})
export class Course_completione extends BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  cc_id: number

  @Column({
    type: 'bigint',
    nullable: false
  }) 
  personid?: number;

  @Column()
  name?: string;

  @Column({
    nullable: true 
  })
  status?: string;

  @Column({
    nullable: true
  })
  completed_date?: string;

  //@Column({
  //  nullable: true
  //})
  //publisher?: string;

  @Column({
    nullable: true
  })
  sfId?: string;

  @ManyToOne(() => Studente, student => student.course_completions)
  @JoinColumn({
    referencedColumnName: 'id'
  })
  student: Studente;
}
