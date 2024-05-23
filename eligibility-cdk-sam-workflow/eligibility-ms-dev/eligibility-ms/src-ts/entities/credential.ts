import { BaseEntity, Column, Entity, JoinColumn, ManyToOne, PrimaryGeneratedColumn } from 'typeorm';
import { Studente } from './student';

// prod.credential

@Entity('credential', { schema: 'eligibility'})
export class Credentiale extends BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  cred_id: number

  @Column({
    nullable: true
  })
  name: string;

  @Column({
    nullable: true
  })
  status: string;

  @Column({
    nullable: true
  })
  firstIssuance_date: string;

  @Column({
    nullable: true
  })
  expiration_date: string;

  @Column({
    nullable: false
    })
  credential_number: string;

  @ManyToOne(() => Studente, student => student.credentials)
  @JoinColumn({
    referencedColumnName: 'id'
  })
  student: Studente;

}
