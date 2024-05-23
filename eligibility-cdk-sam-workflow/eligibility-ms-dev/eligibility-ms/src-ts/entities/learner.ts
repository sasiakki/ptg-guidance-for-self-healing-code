import {BaseEntity, Column, CreateDateColumn, Entity, PrimaryColumn, PrimaryGeneratedColumn, Timestamp, UpdateDateColumn} from 'typeorm';

@Entity('learner', { schema: "staging" })
export class learner extends BaseEntity {
    @PrimaryColumn({
        type: 'bigint'
    })
    personid: number;
    
    @Column({
        nullable: true
    })
    benefitscontinuation: boolean;

    @Column({
        nullable: true
    })
    orientationandsafetycomplete: Date;

    @Column({
        nullable: true
    })
    compliant: string;

    @Column({
        nullable: true
    })
    requiredtraining: string;

    @CreateDateColumn()
    created: Date;

    @UpdateDateColumn()
    modified: Date;

    @Column({
        nullable: true
    })
    archived: string;

    @CreateDateColumn()
    recordcreateddate: Date;

    @UpdateDateColumn()
    recordmodifieddate: Date;

    @PrimaryGeneratedColumn('uuid')
    learnerid: number;
}