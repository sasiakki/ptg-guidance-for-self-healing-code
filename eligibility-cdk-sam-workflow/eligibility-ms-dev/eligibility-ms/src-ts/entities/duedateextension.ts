import {BaseEntity, Column, CreateDateColumn, Entity, PrimaryColumn, UpdateDateColumn} from 'typeorm';

@Entity('duedateextension', { schema: "prod" })
export class duedateextension extends BaseEntity {
 
    @PrimaryColumn({
        nullable: false,
        unique: true
    })
    trainingid: string;

    @PrimaryColumn({
        nullable: false,
        unique: true
    })
    personid: number;
    
    @Column({
        nullable: true
    })
    duedateoverridereason: string;

    @Column({
        nullable: true
    })
    employerrequested: string;

    @Column({
        nullable: true
    })
    bcapproveddate: Date;

    @Column({
        nullable: true
    })
    duedateoverride: Date;
    
    @CreateDateColumn()
    recordcreateddate: Date;

    @UpdateDateColumn()
    recordmodifieddate: Date;

}