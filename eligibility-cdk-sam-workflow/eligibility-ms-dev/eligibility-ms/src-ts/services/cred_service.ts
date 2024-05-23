import {
    Credential,
  } from './../models';
  import { isNullOrUndefined } from 'util';
  
  
  export class cred_service {
  
    public static getCredentials(t: any): Credential[] {
        const credentials: Credential[] = new Array<Credential>();
        for (const s of t){
            if (!isNullOrUndefined(s.name) && !isNullOrUndefined(s.status) && !isNullOrUndefined(s.firstIssuance_date))
	    //&& !isNullOrUndefined(s.expiration_date)) //commented as the part of MDL-570 
	    {
                const credential: Credential = new Credential();
                //s.name refers to credential type in eligibility.credential table
                credential.credential_number = s.name;
                credential.name = s.name;
                credential.status = s.status;
                //credential.firstIssuance_date = s.firstIssuance_date;
                //credential.expiration_date = s.expiration_date;
                credential.firstIssuance_date = !isNullOrUndefined(s.firstIssuance_date) ? s.firstIssuance_date : ''; //added NULL/Undefined check for MDL-570 & b2bds936
                credential.expiration_date = !isNullOrUndefined(s.expiration_date) ? s.expiration_date : ''; //added NULL/Undefined check for MDL-570 & b2bds936
                credentials.push(credential);
            }
        }
        return credentials.length > 0 ? credentials : null;
    }
}

