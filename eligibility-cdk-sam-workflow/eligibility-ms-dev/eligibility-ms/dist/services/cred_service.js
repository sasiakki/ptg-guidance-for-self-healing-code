"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.cred_service = void 0;
const models_1 = require("./../models");
const util_1 = require("util");
class cred_service {
    static getCredentials(t) {
        const credentials = new Array();
        for (const s of t) {
            if (!(0, util_1.isNullOrUndefined)(s.name) && !(0, util_1.isNullOrUndefined)(s.status) && !(0, util_1.isNullOrUndefined)(s.firstIssuance_date)) {
                const credential = new models_1.Credential();
                credential.credential_number = s.name;
                credential.name = s.name;
                credential.status = s.status;
                credential.firstIssuance_date = !(0, util_1.isNullOrUndefined)(s.firstIssuance_date) ? s.firstIssuance_date : '';
                credential.expiration_date = !(0, util_1.isNullOrUndefined)(s.expiration_date) ? s.expiration_date : '';
                credentials.push(credential);
            }
        }
        return credentials.length > 0 ? credentials : null;
    }
}
exports.cred_service = cred_service;
//# sourceMappingURL=cred_service.js.map