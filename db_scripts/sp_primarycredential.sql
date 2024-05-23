-- PROCEDURE: staging.sp_primarycredential()

-- DROP PROCEDURE IF EXISTS staging.sp_primarycredential();

CREATE OR REPLACE PROCEDURE staging.sp_primarycredential(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN

Truncate table staging.cred_details_base;

INSERT INTO staging.cred_details_base
(
  credentialnumber,
  credentialtype,
  hiredateeligible,
  eligiblestatus,
  RANK,
  personid,
  credentialstatus,
  lastissuancedate,
  expirationdate,
  firstissuancedate,
  hiredate,
  credcount,
  cred_status_count,
  stat,
  primary_cred,
  credtype,
  dateofhire,
  hireexp
)

SELECT A.credentialnumber,
       A.credentialtype,
       hiredateeligible,
       eligiblestatus,
       RANK,
       A.personid,
       credentialstatus,
       lastissuancedate,
       CAST(TO_TIMESTAMP(expirationdate::TEXT,'mm/dd/yyyy') AS TIMESTAMP) expirationdate,
       firstissuancedate,
       B.hiredate,
       credcount,
       cred_status_count,
       stat,
       '' AS primary_cred,
       credtype,
       dateofhire,
       CASE
         WHEN COALESCE(b.hiredate,'1900-01-01 00:00:00') <= CAST(TO_TIMESTAMP(expirationdate::TEXT,'mm/dd/yyyy') AS TIMESTAMP) THEN 1
         ELSE 0
       END AS hireexp
FROM staging.vw_getcredentialsforgrid A
--left outer join (Select distinct personid ,min(hiredate) hiredate  from staging.personhistory where categorycode is not null group by personid)  B on A.personid=B.personid
  LEFT OUTER JOIN (SELECT DISTINCT personid,
                          COUNT(DISTINCT credentialnumber) credcount,
                          COUNT(DISTINCT credentialstatus) AS cred_status_count,
                          ARRAY_TO_STRING(ARRAY_AGG(DISTINCT credentialstatus),',') stat,
                          ARRAY_TO_STRING(ARRAY_AGG(DISTINCT credentialtype),',') credtype
                   FROM staging.vw_getcredentialsforgrid A
                   WHERE A.credentialtype <> 'NA'
                   GROUP BY personid) C ON A.personid = C.personid
  LEFT OUTER JOIN (SELECT personid,
                          CASE
                            WHEN MAX(dateofhire) IS NULL AND MAX(hiredate) IS NOT NULL THEN MAX(hiredate)
                            WHEN MAX(dateofhire) IS NOT NULL THEN MAX(TO_TIMESTAMP(dateofhire::TEXT,'MM/DD/YYYY'))
                            ELSE '1900-01-01 00:00:00'
                          END AS hiredate
                   FROM staging.vw_getcredentialsforgrid
                   GROUP BY personid) B ON A.personid = B.personid
WHERE A.credentialtype <> 'NA';

 
--commit ; 

-------------Rules for Primary cred 1 ----------

---Rule 1 --If a goldenrecord has 1 active credential then that one should be primary 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base 
where stat='Active' and credcount=1
and primary_cred ='');

--commit ; 

---Rule 2 ---if it has more than 1 active credential then consider ranking and take the lowest rank 

---Update ones which have same rank and one expirationdate  NC HM ones 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(distinct rank) distrank from staging.cred_details_base A where   cred_status_count>1 and stat like '%Active%' group by A.personid ) B on A.personid=B.personid 
left outer join  (Select distinct personid, count( (expirationdate, 'YYYY-MM-DD')) as countexp
from staging.cred_details_base A where   cred_status_count>=1 and stat like '%Active%'  group by a.personid , expirationdate  ) D on A.personid=D.personid
where stat like '%Active%'
and distrank=1
and countexp=1
and credcount>1
and credentialstatus='Active'
and primary_cred ='');

--commit ; 

--set remaining credentials to 0 

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(distinct rank) distrank from staging.cred_details_base A where   cred_status_count>1 and stat like '%Active%' group by A.personid ) B on A.personid=B.personid 
left outer join  (Select distinct personid, count( (expirationdate, 'YYYY-MM-DD')) as countexp
from staging.cred_details_base A where   cred_status_count>=1 and stat like '%Active%'  group by a.personid , expirationdate  ) D on A.personid=D.personid
where stat like '%Active%'
and distrank=1
and countexp=1
and credcount>1
and credentialstatus<>'Active'
and primary_cred ='');

--commit ; 
--Update all grid with active 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A where credentialstatus ='Active' group by A.personid ) B on A.personid=B.personid 
where   cred_status_count>=1
and stat like '%Active%'
and rank=minrank
and credentialstatus='Active'
and primary_cred ='');

--commit ; 
--set remaining credentials to 0 

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A where credentialstatus ='Active' group by A.personid ) B on A.personid=B.personid 
where   cred_status_count>=1
and stat like '%Active%'
and rank<>minrank
and primary_cred ='');
--commit ; 

---Rule 3 ---if a goldenrecord has pending credentials and hiredate<=expiration then it should be mark a primary

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, max(rank) minrank , count(distinct rank) distrank from staging.cred_details_base A where   cred_status_count>1 and stat like '%Pending%' and credentialtype in ('HM','NC','OSPI') group by A.personid ) B on A.personid=B.personid 
left outer join  (Select distinct personid, count( (expirationdate, 'YYYY-MM-DD')) as countexp
from staging.cred_details_base A where   cred_status_count>=1 and stat like '%Pending%' and credentialtype in ('HM','NC','OSPI')  group by a.personid , expirationdate  ) D on A.personid=D.personid
where stat like '%Pending%'
and distrank=1
and countexp=1
and credcount>1
and credentialstatus='Pending'
and credentialtype in ('HM','NC','OSPI')
and primary_cred ='');

--commit ; 
--set remaining credentials to 0 

update staging.cred_details_base set primary_cred=0 --herexcxcvcvxvvx
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
where A.personid in (select personid from staging.cred_details_base where primary_cred='1')
 and A.primary_cred='');

--commit ; 

--Update all grid with Pending and credentialtype in ('HM','NC')

update staging.cred_details_base set primary_cred=1 --here
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A where credentialstatus ='Pending' and credentialtype in ('HM','NC','OSPI') group by A.personid ) B on A.personid=B.personid 
where   cred_status_count>=1
and stat like '%Pending%'
and rank=minrank
and credentialstatus='Pending'
and credentialtype in ('HM','NC','OSPI')
and primary_cred ='');

--commit ; 

--set remaining credentials to 0 

update staging.cred_details_base set primary_cred=0 --herexcxcvcvxvvx
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
where A.personid in (select personid from staging.cred_details_base where primary_cred='1')
 and A.primary_cred='');

---commit;

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A where credentialstatus ='Pending' and credentialtype not in ('HM','NC','OSPI') group by A.personid ) B on A.personid=B.personid 
where   cred_status_count>1
and stat like '%Pending%'
and rank=minrank
and credentialstatus='Pending'
and credentialtype not in ('HM','NC','OSPI')
and hireexp=1
and primary_cred ='');
--commit;

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A where credentialstatus ='Pending' and credentialtype not in ('HM','NC','OSPI') group by A.personid ) B on A.personid=B.personid 
where   cred_status_count>1
and stat like '%Pending%'
and rank<>minrank
and credentialstatus='Pending'
and credentialtype not in ('HM','NC','OSPI')
and hireexp=1
and primary_cred ='');
--commit ; 

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
select credentialnumber
 from staging.cred_details_base A
Left Outer Join (Select distinct A.personid, max(rank) minrank , count(distinct rank) distrank from staging.cred_details_base A where credcount=2 and stat='Pending' and cred_status_count=1 group by A.personid ) B on A.personid=B.personid 
join (Select distinct personid from staging.cred_details_base  where credcount=2 and stat='Pending'  and eligiblestatus=1)D on A.personid=D.personid 
join (Select distinct personid,max(dateofhire)mdoh from staging.cred_details_base  where credcount=2 and stat='Pending' group by personid)E on A.personid=E.personid 
where credcount=2 and stat='Pending' and distrank=1  and( eligiblestatus=0 or dateofhire<>mdoh) 
);

--commit ; 

---Rule 5--- if a goldenrecord has a 1 credential and hiredate<=expirationdate it doesn't matter the status it should be marked as primary 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
where credcount=1
and hiredate <= TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')
and primary_cred='');

--commit ;

-- update remaining to 0 

update staging.cred_details_base set primary_cred=0 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
where credcount=1
and hiredate >= TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')
and primary_cred='');

--commit ;

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from staging.cred_details_base where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count(distinct expirationdate) as count_exp from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )D on A.personid=D.personid
where stat ='Expired'
and credcount>1
and cred_status_count=1
and credcount=count_exp
and expirationdate=maxexp
and primary_cred='');

--commit ;

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from staging.cred_details_base where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count(distinct expirationdate) as count_exp from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )D on A.personid=D.personid
where stat ='Expired'
and credcount>1
and cred_status_count=1
and credcount=count_exp
and expirationdate<>maxexp
and primary_cred='');

--commit ;

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from staging.cred_details_base where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count(distinct expirationdate) as count_exp from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid    ) E on A.personid=E.personid
where stat ='Expired'
and credcount>1
and cred_status_count=1
and credcount<>count_exp
and rank=minrank
and primary_cred='');

--commit ;

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from staging.cred_details_base where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count(distinct expirationdate) as count_exp from staging.cred_details_base A where stat='Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat='Expired' and credcount>1 group by A.personid    ) E on A.personid=E.personid
where stat ='Expired'
and credcount>1
and  cred_status_count=1
and credcount<>count_exp
and rank<>minrank
and primary_cred='');

--commit ;

 --- If credential has expired and if hiredate<=expireddate and if both expirationdates are equal take min rank 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from  staging.cred_details_base where stat='Expired' and credcount>=1  and hiredate <= TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') ) B on A.personid=B.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A group by A.personid ) E on A.personid=E.personid 
left outer join  (Select distinct personid, count( (expirationdate, 'YYYY-MM-DD')) as countexp , (expirationdate, 'YYYY-MM-DD') ::text  as expdate
from staging.cred_details_base A where   cred_status_count>=1 and stat ='Expired'  group by a.personid , expirationdate  ) D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A group by A.personid )C on A.personid=C.personid 
where credcount>=1
and stat='Expired'
and countexp >1
and A.expirationdate=maxexp
and rank=minrank
and primary_cred='');

--commit ;

--set remaining credentials to 0 

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
inner join (Select distinct personid from  staging.cred_details_base where stat='Expired' and credcount>=1  and hiredate <= TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') ) B on A.personid=B.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank from staging.cred_details_base A group by A.personid ) E on A.personid=E.personid 
left outer join  (Select distinct personid, count( (expirationdate, 'YYYY-MM-DD')) as countexp , (expirationdate, 'YYYY-MM-DD') ::text  as expdate
from staging.cred_details_base A where   cred_status_count>=1 and stat ='Expired'  group by a.personid , expirationdate  ) D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A group by A.personid )C on A.personid=C.personid 
where credcount>=1
and stat='Expired'
and countexp >1
and A.expirationdate=maxexp
and rank<>minrank
and primary_cred='');

--commit ;

---When credcount >1 and hiredate<=expirationdate and credential is closed / DOH Negative Status- No Work we take the min rank 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from  staging.cred_details_base A 
inner join (Select distinct personid from staging.cred_details_base where stat in ('DOH Negative Status- No Work','Closed') and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat in ('DOH Negative Status- No Work','Closed') and credcount>1 group by A.personid    ) E on A.personid=E.personid
where credcount>1 
and stat in ('DOH Negative Status- No Work','Closed')
and rank=minrank
and primary_cred='');

--commit ;

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber 
from  staging.cred_details_base A 
inner join (Select distinct personid from staging.cred_details_base where stat in ('DOH Negative Status- No Work','Closed') and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat in ('DOH Negative Status- No Work','Closed') and credcount>1 group by A.personid    ) E on A.personid=E.personid
where credcount>1 
and stat in ('DOH Negative Status- No Work','Closed')
and rank<>minrank
and primary_cred='');

--commit ;

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base  A
inner join (Select distinct personid from staging.cred_details_base where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count(distinct expirationdate) as count_exp from staging.cred_details_base A where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid    ) E on A.personid=E.personid
where 
credentialstatus ='DOH Negative Status- No Work'
 and credcount>2
and cred_status_count>1
and credcount<>count_exp
and rank=minrank
and hireexp=1
and primary_cred='');

--commit;

update staging.cred_details_base set primary_cred=0 
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base  A
inner join (Select distinct personid from staging.cred_details_base where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count(distinct expirationdate) as count_exp from staging.cred_details_base A where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat='DOH Negative Status- No Work,Expired' and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid    ) E on A.personid=E.personid
where  
 credcount>2
and cred_status_count>1
and credcount<>count_exp
and rank<>minrank
and hireexp=1
and primary_cred='');
--commit ; 

------for credentials with multiple statuses having hiredate<=expirationdate 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from staging.cred_details_base where cred_status_count<>1 and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
--left join (Select distinct goldenrecordid from staging.cred_details_base where credtype LIKE '%HM%'   and stat LIKE '%Pending%' )F on A.goldenrecordid=F.goldenrecordid 
--left join (Select distinct goldenrecordid from staging.cred_details_base where credtype LIKE '%NC%'   and stat LIKE '%Pending%' )R on A.goldenrecordid=R.goldenrecordid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where  cred_status_count<>1 and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count( distinct expirationdate) as count_exp from staging.cred_details_base A where cred_status_count<>1 and credcount>1  group by A.personid )D on A.personid=D.personid
where credcount>1
and cred_status_count<>1
--and F.goldenrecordid is null
--and R.goldenrecordid is null
and expirationdate=maxexp 
and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')
and primary_cred='');
--commit ; 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner join (Select distinct personid from staging.cred_details_base where cred_status_count<>1 and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')) B on A.personid=B.personid 
inner Join (Select distinct A.personid, max(expirationdate) maxexp  from staging.cred_details_base A where  cred_status_count<>1 and credcount>1 and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00') group by A.personid )C on A.personid=C.personid
left outer join (Select personid, count( distinct expirationdate) as count_exp from staging.cred_details_base A where cred_status_count<>1 and credcount>1  group by A.personid )D on A.personid=D.personid
Left Outer Join (Select distinct A.personid, min(rank) minrank , count(*) rankcount from staging.cred_details_base A where stat='Expired' and credcount>1 group by A.personid    ) E on A.personid=E.personid
where credcount>1
and cred_status_count<>1
--and credcount<>count_exp
and expirationdate=maxexp 
and hiredate<=TO_TIMESTAMP(expirationdate::text,'YYYY-MM-DD 00:00:00')
and rank=minrank
and hireexp=1
and primary_cred='');

--commit ;

---Rule 8 -- Set any status with hiredate<exp date primary cred to 1 

update staging.cred_details_base set primary_cred=1 
where credentialnumber in (
Select credentialnumber 
from staging.cred_details_base A
inner  join (Select personid , sum(hireexp) from staging.cred_details_base   where credcount>1 group by personid having sum(hireexp) =1) B on A.personid=B.personid
--left join (Select distinct goldenrecordid from staging.cred_details_base where credtype LIKE '%HM%'   and stat LIKE '%Pending%' )F on A.goldenrecordid=F.goldenrecordid 
--left join (Select distinct goldenrecordid from staging.cred_details_base where credtype LIKE '%NC%'   and stat LIKE '%Pending%' )R on A.goldenrecordid=R.goldenrecordid 
where 
credcount>1
--and F.goldenrecordid is null
--and R.goldenrecordid is null
and hireexp=1
and  primary_cred=''
);

--commit ;

---set remaining to 0 

update staging.cred_details_base set primary_cred=0
where credentialnumber in (
Select credentialnumber
from staging.cred_details_base A
inner  join (Select personid , sum(hireexp) from staging.cred_details_base   where  credcount>1 group by personid having sum(hireexp) =1) B on A.personid=B.personid
--left join (Select distinct goldenrecordid from staging.cred_details_base where credtype LIKE '%HM%'   and stat LIKE '%Pending%' )F on A.goldenrecordid=F.goldenrecordid 
--left join (Select distinct goldenrecordid from staging.cred_details_base where credtype LIKE '%NC%'   and stat LIKE '%Pending%' )R on A.goldenrecordid=R.goldenrecordid  
where 
credcount>1
--and F.goldenrecordid is null
--and R.goldenrecordid is null
and hireexp<>1
and  primary_cred=''
);
--commit ;

update  staging.cred_details_base
set primary_cred='0'
where primary_cred='' ;
--commit ;

update raw.credential_delta
set primarycredential=cast(primary_cred as int),modified = current_timestamp,recordmodifieddate = current_timestamp
from staging.cred_details_base
where staging.cred_details_base.credentialnumber=raw.credential_delta.credentialnumber and primarycredential<>cast(primary_cred as int);
--commit ;

with cte as ( select p.personid ,per.credentialnumber from staging.personhistory per  
join prod.person p on per.personid=p.personid where per. credentialnumber is not null and per.personid is not null)
update raw.credential_delta d
set personid=c.personid ,recordmodifieddate = current_timestamp
from cte c 
where c.credentialnumber=d.credentialnumber and d.personid is null;

--Insert an entry into the logs table
INSERT INTO logs.lastprocessed
(
  processname,
  lastprocesseddate,
  success
)
VALUES
(
  'glue-primarycredential-process',
  CURRENT_TIMESTAMP,
  '1'
);

END;
$BODY$;
