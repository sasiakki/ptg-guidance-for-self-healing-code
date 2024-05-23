-- FUNCTION: staging.fn_checkquarantineperson(character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, bigint)

-- DROP FUNCTION IF EXISTS staging.fn_checkquarantineperson(character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, bigint);

CREATE OR REPLACE FUNCTION staging.fn_checkquarantineperson(
	var_firstname character varying DEFAULT NULL::character varying,
	var_lastname character varying DEFAULT NULL::character varying,
	var_ssn character varying DEFAULT NULL::character varying,
	var_dob character varying DEFAULT NULL::character varying,
	var_homephone character varying DEFAULT NULL::character varying,
	var_mobilephone character varying DEFAULT NULL::character varying,
	var_email1 character varying DEFAULT NULL::character varying,
	var_email2 character varying DEFAULT NULL::character varying,
	var_mailingaddress character varying DEFAULT NULL::character varying,
	var_mailingzip character varying DEFAULT NULL::character varying,
	var_dshsid bigint DEFAULT NULL::bigint)
    RETURNS numeric
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$



DECLARE	
	
	c_puid numeric := NULL::numeric;
	c_zip character varying := NULL::character varying;
	
BEGIN

	var_firstname := lower(trim(var_firstname));
	var_firstname := regexp_replace(var_firstname,'[^\w]+|_','','g')::character varying;
	var_lastname := lower(trim(var_lastname));
	var_lastname := regexp_replace(var_lastname,'[^\w]+|_','','g')::character varying;
	var_ssn := trim(var_ssn);
	var_dob := trim(var_dob);
	var_homephone := lower(trim(var_homephone));
	var_mobilephone := lower(trim(var_mobilephone));
	var_email1 := lower(trim(var_email1));
	var_email2 := lower(trim(var_email2));
	var_mailingzip := lower(trim(var_mailingzip));
	
	c_zip := var_mailingzip;
	
	-- criteria 1: dshsid
	IF (var_dshsid is not null) and
		 Exists (select * from staging.personquarantine p where p.dshsid = var_dshsid) Then
				 
			select p.person_unique_id into c_puid from staging.personquarantine p where p.dshsid = var_dshsid;
			
	-- criteria 2: f,l,ssn
	ELSIF (var_lastname is not null and var_ssn is not null and var_firstname is not null) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.ssn) = var_ssn and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname) Then
		
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.ssn) = var_ssn and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname;
		
	-- criteria 3: f,l,dob
	ELSIF (var_lastname is not null and var_firstname is not null and var_dob is not null) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and trim(p.dob) = var_dob) Then
				 
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and trim(p.dob) = var_dob;

	-- criteria 4: f,l,ssn,dob
	ELSIF (var_lastname is not null and var_firstname is not null and var_ssn is not null and var_dob is not null) and
		 Exists (select * from staging.personquarantine p where lower(trim(Left(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying,4))) = left(var_lastname,4) and
				  lower(trim(Left(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying,4))) = left(var_firstname,4) and trim(p.ssn) = var_ssn and trim(p.dob) = var_dob) Then
				 
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(Left(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying,4))) = left(var_lastname,4) and
				  lower(trim(Left(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying,4))) = left(var_firstname,4) and trim(p.ssn) = var_ssn and trim(p.dob) = var_dob;
	
	-- criteria 5: f,l,ssn,phone
	ELSIF (var_lastname is not null and var_firstname is not null and var_ssn is not null and (var_homephone is not null or var_mobilephone is not null) ) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname
				  and trim(p.ssn) = var_ssn and (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone)) Then
				 
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname
				  and trim(p.ssn) = var_ssn and (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone);

	-- criteria 6: f,l,ssn,email
	ELSIF (var_firstname is not null and var_lastname is not null and (var_email1 is not null or var_email2 is not null) and var_ssn is not null) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.ssn) = var_ssn and (lower(trim(p.email1)) = var_email1 or lower(trim(p.email2)) = var_email2 or lower(trim(p.email1)) = var_email2 or lower(trim(p.email2)) = var_email1)) Then
				 
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.ssn) = var_ssn and (lower(trim(p.email1)) = var_email1 or lower(trim(p.email2)) = var_email2 or lower(trim(p.email1)) = var_email2 or lower(trim(p.email2)) = var_email1);

	-- criteria 7: f,l,dob,phone
	ELSIF (var_firstname is not null and var_lastname is not null and var_dob is not null and (var_homephone is not null or var_mobilephone is not null) ) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.dob) = var_dob and
				  (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone)) Then
				 
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.dob) = var_dob and
				  (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone);
				 
	-- criteria 8: f4,l4,dob,phone
	ELSIF (var_lastname is not null and var_firstname is not null and var_dob is not null and (var_homephone is not null or var_mobilephone is not null) ) and
		 Exists (select * from staging.personquarantine p where lower(trim(Left(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying,4))) = left(var_lastname,4) and lower(trim(Left(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying,4))) = left(var_firstname,4) and
				  trim(p.dob) = var_dob and (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone)) Then
		
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(Left(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying,4))) = left(var_lastname,4) and lower(trim(Left(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying,4))) = left(var_firstname,4) and
				  trim(p.dob) = var_dob and (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone);
				 
	-- criteria 9: f,l,ssn,addr
	ELSIF (var_firstname is not null and var_lastname is not null and var_ssn is not null and var_mailingzip is not null ) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and
				  trim(p.ssn) = var_ssn and lower(trim(p.mailingzip)) = c_zip) Then
		
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and
				  trim(p.ssn) = var_ssn and lower(trim(p.mailingzip)) = c_zip;
				 
	-- criteria 10: f,l,dob,addr
	ELSIF (var_firstname is not null and var_lastname is not null and var_dob is not null and var_mailingzip is not null ) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.dob) = var_dob and lower(trim(p.mailingzip)) = c_zip) Then
		
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.dob) = var_dob and lower(trim(p.mailingzip)) = c_zip;

	-- criteria 11: f,l,addr,phone
	ELSIF (var_firstname is not null and var_lastname is not null and var_mailingzip is not null and (var_mobilephone is not null or var_homephone is not null) ) and
		 Exists (select * from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(p.mailingzip)) = c_zip and
				  (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone)) Then
		
			select p.person_unique_id into c_puid from staging.personquarantine p where lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(p.mailingzip)) = c_zip and
				  (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone);

	ELSE
	
		c_puid := NULL::numeric;
		
	END IF;
	
	return c_puid::numeric;
	
END;
$BODY$;

