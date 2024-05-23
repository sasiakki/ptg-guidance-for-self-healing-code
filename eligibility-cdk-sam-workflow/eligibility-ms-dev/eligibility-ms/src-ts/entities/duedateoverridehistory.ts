import {BaseEntity, Column, CreateDateColumn, Entity, PrimaryColumn, UpdateDateColumn} from 'typeorm';

@Entity('duedateoverridehistory', { schema: "prod" })
export class duedateoverridehistory extends BaseEntity {
 
    @PrimaryColumn({
        nullable: false,
        unique: true
    })
    trainingid: string;
    
    @Column({
        nullable: true
    })
    reasoncode: string;

    @Column({
        nullable: true
    })
    duedateoverride: Date;
    
    @CreateDateColumn()
    recordcreateddate: Date;

    @UpdateDateColumn()
    recordmodifieddate: Date;

}