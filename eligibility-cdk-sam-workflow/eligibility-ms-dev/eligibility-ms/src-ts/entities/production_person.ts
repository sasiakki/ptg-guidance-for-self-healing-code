import {BaseEntity, Column, CreateDateColumn, Entity, PrimaryColumn, Timestamp, UpdateDateColumn} from 'typeorm';

@Entity('person', { schema: "prod" })
export class prod_person extends BaseEntity {
    @PrimaryColumn({
        type: 'bigint'
    })
    personid: number;
    
    @Column({
        nullable: true
    })
    first_name: string;

    @Column({
        nullable: true
    })
    last_name: string;

    @Column({
        nullable: true
    })
    email1: string;

    @Column({
        nullable: true
    })
    email2: string;

    @Column({
        nullable: true
    })
    homephone: string;

    @Column({
        nullable: true
    })
    mobilephone: string;

    @Column({
        nullable: true
    })
    language: string;

    @Column({
        nullable: true
    })
    physicaladdress: string;

    @Column({
        nullable: true
    })
    mailingaddress: string;

    @Column({
        nullable: true
    })
    status: string;

    @Column({
        nullable: true
    })
    exempt: string;

    @Column({
        nullable: true
    })
    type: string;

    @Column({
        nullable: true
    })
    workercategory: string;
    
    @Column({
        nullable: true
    })
    categorycode: string;
    
    @Column({
        nullable: true
    })
    iscarinaeligible: boolean;
    
    @Column({
        nullable: true
    })
    dob: string;
    
    @Column('timestamp', {
        nullable: true
    })
    hiredate: Date;
    
    @Column({
        nullable: true
    })
    trackingdate: Date;
    
    @Column({
        nullable: true
    })
    ahcas_eligible: boolean;
    
    @Column({
        nullable: true
    })
    trainingstatus: string;
    
    @Column({
        nullable: true
    })
    middlename: string;
    
    @Column({
        nullable: true
    })
    mailingstreet1: string;
    
    @Column({
        nullable: true
    })
    mailingstreet2: string;
    
    @Column({
        nullable: true
    })
    mailingcity: string;
    
    @Column({
        nullable: true
    })
    mailingstate: string;
    
    @Column({
        nullable: true
    })
    mailingzip: string;
    
    @Column({
        nullable: true
    })
    mailingcountry: string;
    
    @Column({
        type: 'bigint',
        nullable: true
    })
    dshsid: number;
    
    @Column({
        nullable: true
    })
    credentialnumber: string;
        
    @Column({
        type: 'bigint'
    })
    cdwaid: string;

    @Column({
        nullable: true
    })
    sfcontactid: string;

    @CreateDateColumn()
    recordcreateddate: Date;

    @UpdateDateColumn()
    recordmodifieddate: Date;
}