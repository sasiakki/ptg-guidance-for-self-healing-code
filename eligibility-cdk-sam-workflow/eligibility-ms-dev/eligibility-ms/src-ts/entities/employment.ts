import { BaseEntity, Column, Entity, PrimaryGeneratedColumn, ManyToOne, JoinColumn } from "typeorm";
import { Studente } from "./student";
// employmentrelationship

@Entity('employment', {schema:'eligibility'})
export class Employmente extends BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  emp_id: number

  @Column({
    nullable: true
  })
  name?: string;

  @Column({
    nullable: false
  })
  status: string;

  @Column({
    nullable: false
  })
  hire_date: string;

  @Column({
    nullable: true
  })
  terminate_date?: string;

 // @Column({
  //  nullable: true
  //}) 
  //authentication_date?: string;

  @Column({
    nullable: false
  })
  training_category: string;

  //@Column({
   // nullable: true,
   // default: false
  //})
  //ignore_assigned_category?: boolean;

  @ManyToOne(() => Studente, student => student.employments)
  @JoinColumn({
    referencedColumnName: 'id'
  })
  student: Studente;
}
