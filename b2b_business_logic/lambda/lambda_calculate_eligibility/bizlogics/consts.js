"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Constants = void 0;
exports.Constants = {
    work_category: {
        TERMINATED: 'TERM',
        ORIENTATION_SAFETY: 'OSAF',
        ADULT_CHILD: 'ADCH',
        DDD_ADULT: 'DDAC',
        DDD_NDDD: 'PPPP',
        DDD_RESPITE: 'PPRE',
        DDD_STANDARD: 'DDST',
        PARENT_PROVIDER_DDD: 'DDPP',
        PARENT_NON_DDD: 'PPND',
        LIMITED_SERVICE_PROVIDER: 'LSPR',
        STANDARD_HCA: 'SHCA',
        RESPITE: 'RESP'
    },
    training_code: {
        OS: { CODE: '100', NAME: 'Orientation and Safety', HOURS: '5', REQUIRED: true },
        BT_7: { CODE: '204', NAME: 'Basic Training 7', HOURS: '7', REQUIRED: true },
        BT_9: { CODE: '203', NAME: 'Basic Training 9', HOURS: '9', REQUIRED: true },
        BT_30: { CODE: '202', NAME: 'Basic Training 30', HOURS: '30', REQUIRED: true },
        BT_70: { CODE: '201', NAME: 'Basic Training 70', HOURS: '70', REQUIRED: true },
        SAFETY: { CODE: '901', NAME: 'Safety', HOURS: '', REQUIRED: true },
        ORIENTATION: { CODE: '902', NAME: 'Orientation', HOURS: '', REQUIRED: true },
        REFRESHER: { CODE: '200', NAME: 'Refresher', HOURS: '', REQUIRED: false },
        BT_42: { CODE: '913', NAME: 'Basic Training 42', HOURS: '42', REQUIRED: true },
        MFOC: { CODE: '912', NAME: 'Modified Fundamentals of Care', HOURS: '', REQUIRED: false },
        RFOC: { CODE: '911', NAME: 'Revised Fundamentals of Care', HOURS: '', REQUIRED: false },
        CE_12: { CODE: '300', NAME: 'Continuing Education', HOURS: '12', REQUIRED: true },
        CBP_WINTER2019: { CODE: '301', NAME: 'Caregiver Best Practices Winter 2019', HOURS: '', REQUIRED: false },
        NDC_9: { CODE: '400', NAME: 'Nurse Delegation Core', HOURS: '', REQUIRED: false },
        NDD_3: { CODE: '401', NAME: 'Nurse Delegation Diabetes', HOURS: '', REQUIRED: false },
        EXEMPT_BT70: { CODE: '602', NAME: 'Exempt Certification Benefit 70', HOURS: '', REQUIRED: false },
        AHCAS: { CODE: '500', NAME: 'Advanced Training', HOURS: '70', REQUIRED: false },
        CE_OPEN_LIB: { CODE: '601', NAME: 'CE Open Library', HOURS: '', REQUIRED: false },
        MINDFUL_WC: { CODE: '603', NAME: 'Mindfulness at Work for Caregivers', HOURS: '', REQUIRED: false },
    },
    higher_equ_training_map: [
        { CODE: '204', HIGHER_EQU_TRAINING: ['204', '203', '202', '205', '201', '913', '912', '911', '602'] },
        { CODE: '203', HIGHER_EQU_TRAINING: ['203', '202', '205', '201', '913', '912', '911', '602'] },
        { CODE: '202', HIGHER_EQU_TRAINING: ['202', '205', '201', '913', '912', '911', '602'] },
        { CODE: '205', HIGHER_EQU_TRAINING: ['205', '202', '201', '913', '912', '911', '602'] },
        { CODE: '201', HIGHER_EQU_TRAINING: ['201', '913', '912', '911', '602'] },
        { CODE: '913', HIGHER_EQU_TRAINING: ['201', '913', '912', '911', '602'] },
        { CODE: '912', HIGHER_EQU_TRAINING: ['201', '913', '912', '911', '602'] },
        { CODE: '911', HIGHER_EQU_TRAINING: ['201', '913', '912', '911', '602'] }
    ],
    training_status: {
        ACTIVE: 'active',
        CLOSED: 'closed'
    },
    compliant_status: {
        COMPLIANT: 'Compliant',
        NONCOMPLIANT: 'Non-Compliant'
    },
    credential_status: {
        EXPIRED: 'Expired',
        ACTIVE: 'Active',
        NEGATIVE: 'DOH Negative Status- No Work',
        PENDING: 'Pending',
        CLOSED: 'Closed'
    },
    employment_status: {
        ACTIVE: 'Active',
        INACTIVE: 'Inactive'
    },
    credential_type: {
        ARNP: { CODE: 'AP', NAME: 'Advance Registration Nurse Practitioner' },
        HCA: { CODE: 'HM', NAME: 'HCA HomeCare Aide' },
        RN: { CODE: 'RN', NAME: 'Registered Nurse' },
        LPN: { CODE: 'LP', NAME: 'Licensed practitioner Nurse' },
        NAC: { CODE: 'NC', NAME: 'Nursing assistant certified' },
        NAR: { CODE: 'NA', NAME: 'Nurse Assistant Registered' },
        OSPI: { CODE: 'OSPI', NAME: 'OSPI' }
    },
    eligible_training_status: {
        CLOSE: 'close',
        ACTIVATE: 'activate',
        REMAIN_OPEN: 'remain_open'
    },
    CE_BCDD: '2023-08-31',
    REHIRE_MIN: '2019-08-17',
    REHIRE_MAX: '2022-12-31',
    EXPIRED_CREDENTIAL_ISRENEABLE_TIMELIMIT: '3',
    bcdd_reason_code: {
        REHIRED: 'ERH',
        COVID19: 'CV19',
        BENEFITS_CONTINUATION: 'BC',
        BREAK_IN_SERVICE_REHIRE: 'BIS'
    }
};
//# sourceMappingURL=consts.js.map