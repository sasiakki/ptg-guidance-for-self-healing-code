import {BaseEntity, Column, Entity, OneToOne, PrimaryColumn} from 'typeorm';
import { Studente } from './student';

@Entity('student_status_set', { schema: "eligibility" })
export class Student_status_sete extends BaseEntity {

    @PrimaryColumn({
        nullable: false,
        unique: true
    })
    studentId: string;
  
    @Column({
        nullable: true,
    })
    isCompliant: boolean; 
  
    @Column({
        nullable: true,
    })
    isGrandFathered: boolean;
  
    @Column({
        nullable: true,
    })
    ahcas_eligible: boolean;
  
    @Column({
        nullable: true,
    })
    complianceStatus: string;  

    @OneToOne(() => Studente, student => student.student_status_set)
    student: Studente
}
  