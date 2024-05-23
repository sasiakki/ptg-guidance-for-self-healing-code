//import { Student_training } from './student-training';
import { Credentiale } from './credential';
//import { Employment } from './employment';
import { Student_status_sete } from './student-status-set';
//import { Course_completion } from './course-completion'
import { BaseEntity, Column, OneToMany, PrimaryColumn, Entity, OneToOne} from 'typeorm';
import { Employmente } from './employment';
import { Course_completione } from './course-completion';
import { Student_traininge } from './student-training';

// required model. needs to be created with new models. 

@Entity('student', {schema: 'eligibility'})
export class Studente extends BaseEntity {

  @PrimaryColumn({
    unique: true,
    nullable: false,
  })
  id: string;

  @Column({
    nullable: true
  })
  provider_id?: string;

  @Column({
    nullable: true
  })
  first_name?: string;

  @Column({
    nullable: true
  })
  last_name?: string;

  @Column({
    nullable: true 
  })
  training_status?: string;

  @Column({
    nullable: true 
  })
  status?: string;

  //@Column({
  //  nullable: true
  //})
  //publisher?: string;

  @Column({
    nullable: true
  })
  active_training?: string;

  @Column({
    nullable: true
  })
  assigned_category?: string;

  @Column({
    nullable: true
  })
  num_active_emp?: number;

  @Column({
    nullable: true
  })
  prefer_language?: string;
  
  @Column({
    nullable: true
  })
  birth_date?: string;

  @OneToOne(() => Student_status_sete, student_status_set => student_status_set.student)
  student_status_set: Student_status_sete

  @OneToMany(() => Credentiale, credential => credential.student)
  credentials: Credentiale[];

  @OneToMany(() => Employmente, employment => employment.student)
  employments: Employmente[];

  @OneToMany(() => Course_completione, course_completion => course_completion.student)
  course_completions: Course_completione[];

  @OneToMany(() => Student_traininge, student_training => student_training.student)
  trainings: Student_traininge[];
 
}
