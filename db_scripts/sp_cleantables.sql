CREATE OR REPLACE PROCEDURE raw.sp_cleantables()
    LANGUAGE plpgsql
AS
$procedure$

DECLARE
    r RECORD;
BEGIN
    ALTER SEQUENCE staging.employmentrelationshiphistory_relationshipid_seq RESTART WITH 1;

    FOR r IN SELECT tablename, schemaname
             FROM pg_tables
             WHERE schemaname in ('prod', 'staging', 'raw', 'logs')
               AND tablename not in
                   ('branch', 'employer', 'instructor', 'coursecatalog', 'employertrust', 'workercategory', 'gender',
                    'ethnicity', 'race', 'languages', 'maritalstatus', 'transfers_trainingprogram', 'courseequivalency',
                    'sftpfilelog', 'lastprocessed')
        LOOP
            EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename) || ' ; ';
            IF EXISTS (SELECT column_name
                       FROM information_schema.columns
                       WHERE table_name = quote_ident(r.tablename)
                         and column_name = 'id') THEN
                EXECUTE 'ALTER SEQUENCE IF EXISTS ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename) ||
                        '_id_seq RESTART WITH 1';
                EXECUTE 'ALTER SEQUENCE IF EXISTS ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename) ||
                        'id_seq RESTART WITH 1';
                EXECUTE 'ALTER SEQUENCE IF EXISTS ' || quote_ident(r.schemaname) || '.' ||
                        'quarantineperson_relationshipid_seq ' || 'RESTART WITH 1';
            END IF;
        END LOOP;

    ALTER TABLE IF EXISTS prod.transcript ALTER COLUMN transcriptid DROP DEFAULT;
    ALTER SEQUENCE prod.employmentrelationship_relationshipid_seq RESTART WITH 1;

    -- This below script to keep the latest processed files for both inbound and outbound 
    -- of sftp to handle the delta detection
    delete
    from logs.sftpfilelog
    where filename not in (select filename
                        from (select *,
                                        RANK() OVER (
                                            PARTITION BY filecategory
                                            ORDER BY processeddate desc
                                            ) as filerank
                                from logs.sftpfilelog
                                order by processeddate desc, filecategory) as p
                        where filerank = 1);


    
    -- This Block for preserving the last processed date for each process defined in delta detection
        
    -- to create temp table
    create temp table lastprocessed_temp as 
    select * from  
    (select *, Rank() over (partition by processname order by lastprocesseddate desc) as rnk
    from logs.lastprocessed where success = '1') r where rnk =1
    order by lastprocesseddate;

    truncate table logs.lastprocessed;

    -- get the sequence_variable for table
    -- SELECT column_default
    -- FROM information_schema.columns
    -- WHERE table_name = 'lastprocessed'
    -- and table_schema = 'logs'
    -- AND column_name = 'id'; --nextval('logs.lastprocessed_seq'::regclass)

    -- reset sequence to 1.
    ALTER SEQUENCE logs.lastprocessed_seq RESTART WITH 1;

    --Insert preserved data
    insert into logs.lastprocessed(id, processname, lastprocesseddate, success,
                                recordcreateddate, recordmodifieddate)
    select nextval('logs.lastprocessed_seq'::regclass), processname, lastprocesseddate, success, recordcreateddate, recordmodifieddate
    from lastprocessed_temp order by lastprocesseddate;

END
$procedure$
;
