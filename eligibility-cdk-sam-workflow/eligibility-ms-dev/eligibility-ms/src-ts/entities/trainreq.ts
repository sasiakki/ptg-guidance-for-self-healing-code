import {BaseEntity, Column, CreateDateColumn, Entity, PrimaryGeneratedColumn, UpdateDateColumn} from 'typeorm';

@Entity('trainingrequirement', { schema: "prod" })
export class trainingrequirement extends BaseEntity {
    @PrimaryGeneratedColumn('uuid')
    trainreq_id: number
    
    @Column({
        nullable: true,
        type: 'bigint'
    })
    personid: number;
    
    @Column({
        nullable: true
    })
    trackingdate: Date;

    @Column({
        nullable: true
    })
    requiredhours: number;

    @Column({
        nullable: true,
        type: "float"
    })
    earnedhours: number;

    @Column({
        nullable: true
    })
    transferredhours: number;

    @Column({
        nullable: true
    })
    duedate: Date;

    @Column({
        nullable: true,
        default: false
    })
    isoverride: boolean;

    @Column({
        nullable: true
    })
    duedateextension: Date;

    @Column({
        nullable: true
    })
    trainingprogram: string;

    @Column({
        nullable: true
    })
    duedateoverridereason: string;
    
    @Column({
        nullable: true
    })
    trainingprogramcode: string;

    @Column({
        nullable: true
    })
    completeddate: Date;

    @Column({
        nullable: true
    })
    status: string;

    @Column({
        nullable: true,
        unique: true
    })
    trainingid: string;

    @Column({
        nullable: true
    })
    isrequired: boolean;

    @Column({
        nullable: true
    })
    created: Date;
    
    @Column({
        nullable: true
      })
      archived: Date;
      
      
    @CreateDateColumn()
    recordcreateddate: Date;

    @UpdateDateColumn()
    recordmodifieddate: Date;

}