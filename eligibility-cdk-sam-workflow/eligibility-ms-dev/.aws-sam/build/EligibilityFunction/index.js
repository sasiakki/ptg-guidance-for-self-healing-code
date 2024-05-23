"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.processingMain = void 0;
require("reflect-metadata");
const typeorm_1 = require("typeorm");
const student_1 = require("./entities/student");
const credential_1 = require("./entities/credential");
const student_status_set_1 = require("./entities/student-status-set");
const student_training_1 = require("./entities/student-training");
const duedateextension_1 = require("./entities/duedateextension");
const employment_1 = require("./entities/employment");
const course_completion_1 = require("./entities/course-completion");
const checkperson_1 = require("./entities/checkperson");
const bizlogics_1 = require("./bizlogics");
const _ = __importStar(require("lodash"));
const b2b_service_1 = require("./services/b2b_service");
const training_service_1 = require("./services/training_service");
const tools_1 = require("./helpers/tools");
const trainreq_1 = require("./entities/trainreq");
const cred_service_1 = require("./services/cred_service");
const production_person_1 = require("./entities/production_person");
const learner_1 = require("./entities/learner");
const helper_1 = require("./helpers/helper");
const processingMain = async (event) => {
    const queries = JSON.stringify(event.queryStringParameters);
    var env = process.env.environment_type;
    var B2B_HOST = "";
    var B2B_USER = "";
    var B2B_PASSWORD = "";
    var B2B_PORT = "";
    var B2B_NAME = "";
    try {
        var aws = require("aws-sdk");
        let secretManager = new aws.SecretsManager({ region: "us-west-2" });
        const secrets = await secretManager.getSecretValue({ SecretId: env + "/b2bds/rds/system-pipelines" }).promise();
        const parsedResult = JSON.parse(secrets.SecretString);
        B2B_HOST = parsedResult.host;
        B2B_USER = parsedResult.username;
        B2B_PASSWORD = parsedResult.password;
        B2B_PORT = parsedResult.port;
        B2B_NAME = parsedResult.dbname;
    }
    catch (error) {
        console.error(error);
        throw new Error("Unable to get secrets");
    }
    try {
        let conn = await (0, typeorm_1.createConnection)({
            type: "postgres",
            host: B2B_HOST,
            port: +B2B_PORT,
            username: B2B_USER,
            password: B2B_PASSWORD,
            database: B2B_NAME,
            logging: true,
            synchronize: false,
            schema: "eligibility",
            entities: [credential_1.Credentiale, student_1.Studente, student_status_set_1.Student_status_sete, student_training_1.Student_traininge, employment_1.Employmente, course_completion_1.Course_completione, checkperson_1.Check_person, duedateextension_1.duedateextension, trainreq_1.trainingrequirement, production_person_1.prod_person, learner_1.learner]
        });
        const em = (0, typeorm_1.getManager)();
        console.log("connected to database: " + em.connection.driver.database);
    }
    catch (error) {
        console.error(error);
        throw new Error("Unable to connect to db");
    }
    const entityManager = (0, typeorm_1.getManager)();
    const inputs = await entityManager.createQueryBuilder().select("check_person").from(checkperson_1.Check_person, 'check_person').where("check_person.check_stat = 0").limit(3000).getMany();
    console.log(inputs.length);
    console.log(`Count of student id's processing in current batch: ${inputs.length}`);
    try {
        let ts = new Array();
        for (const i of inputs) {
            let student = await b2b_service_1.b2b_service.getStudent(i);
            var parsedstudentid = parseInt(student.id, 10);
            console.log(`Processing for the studentid:${parsedstudentid}`);
            const creds = await entityManager.createQueryBuilder()
                .select("credential")
                .from(credential_1.Credentiale, 'credential')
                .where("credential.studentId = :id", { id: parsedstudentid })
                .getMany();
            student.credentials = await cred_service_1.cred_service.getCredentials(creds);
            const trains = await entityManager.createQueryBuilder()
                .select("student_training")
                .from(student_training_1.Student_traininge, 'student_training')
                .where("student_training.studentId = :id", { id: parsedstudentid })
                .getMany();
            const sortHistory = function (training1, training2) {
                if (training1.status > training2.status) {
                    return -1;
                }
                if (training1.status < training2.status) {
                    return 1;
                }
                return 0;
            };
            let history = await training_service_1.training_service.getTrainings(trains);
            student.trainings = (history) ? history.sort(sortHistory) : history;
            console.log(`studentid: ${parsedstudentid}, trainings count: ${(student.trainings) ? student.trainings.length : 0}`);
            console.log('student:', student);
            let recalculateEligibility;
            let ss, training;
            [ss, training, recalculateEligibility] = bizlogics_1.Student_training_logic.evaluateStudentTraining(student, history);
            if (recalculateEligibility === true) {
                console.log(`studentid: ${student.id}; !!! RecalculateElgiibility !!!`);
                const firstRunTrainings = _.cloneDeep(training);
                let secondRunTrainings;
                [ss, secondRunTrainings, recalculateEligibility] = bizlogics_1.Student_training_logic.evaluateStudentTraining(student, helper_1.Helper.mergeTrainings(training, history));
                training = helper_1.Helper.mergeTrainings(firstRunTrainings, secondRunTrainings);
                console.log('studentid:', student.id, ' MERGED assigendTrainings: ', training);
            }
            await entityManager.createQueryBuilder().update(production_person_1.prod_person)
                .set({ trainingstatus: ss.complianceStatus.toLowerCase(), recordmodifieddate: new Date() })
                .where("personid = :id AND trainingstatus <> :complianceStatus", { id: student.id, complianceStatus: ss.complianceStatus.toLowerCase() })
                .execute();
            await entityManager.createQueryBuilder().update(learner_1.learner)
                .set({ compliant: ss.complianceStatus.toLowerCase(), recordmodifieddate: new Date() })
                .where("personid = :id AND compliant <> :complianceStatus", { id: student.id, complianceStatus: ss.complianceStatus.toLowerCase() })
                .execute();
            console.log(`studentid: ${parsedstudentid}, new or updated trainings: ${JSON.stringify(training)}`);
            console.log(`End of processing for the studentid :${parsedstudentid}`);
            for (const t1 of training) {
                if (!(0, tools_1.isNullOrUndefined)(t1)) {
                    ts.push(t1);
                }
            }
            await entityManager.createQueryBuilder().update(checkperson_1.Check_person)
                .set({ check_stat: 1 })
                .where("pgc_id = :id", { id: i.pgc_id })
                .execute();
        }
        console.log(`studentid :${parsedstudentid}; Updating the prod.trainingrequirement table for new or updated trainings`);
        for (const train of ts) {
            if (!(0, tools_1.isNullOrUndefined)(train)) {
                if (train.reason_code) {
                    const newduedates = new duedateextension_1.duedateextension();
                    newduedates.trainingid = train.id;
                    newduedates.employerrequested = '';
                    newduedates.personid = parseInt(train.studentId);
                    newduedates.bcapproveddate = new Date();
                    if (train.reason_code === "BC") {
                        newduedates.duedateoverridereason = "Benefits Continuation";
                    }
                    else if (train.reason_code === "ERH") {
                        newduedates.duedateoverridereason = "Emergency Rule Rehire";
                    }
                    else if (train.reason_code === "CV19") {
                        newduedates.duedateoverridereason = "Covid19 Emergency Rule";
                    }
                    else if (train.reason_code === "BIS") {
                        newduedates.duedateoverridereason = "Break In Service Rehire";
                    }
                    else if (train.reason_code === "RH") {
                        newduedates.duedateoverridereason = "Rehire";
                    }
                    else {
                        newduedates.duedateoverridereason = train.reason_code;
                    }
                    newduedates.duedateoverride = !(0, tools_1.isNullOrUndefined)(train.benefit_continuation_due_date) ? new Date(train.benefit_continuation_due_date) : null;
                    await entityManager.createQueryBuilder()
                        .insert()
                        .into(duedateextension_1.duedateextension)
                        .values(newduedates)
                        .execute();
                }
                const newtrainreq = new trainreq_1.trainingrequirement();
                newtrainreq.trackingdate = !(0, tools_1.isNullOrUndefined)(train.tracking_date) ? new Date(train.tracking_date) : null;
                newtrainreq.requiredhours = train.required_hours;
                newtrainreq.duedate = !(0, tools_1.isNullOrUndefined)(train.due_date) ? new Date(train.due_date) : null;
                newtrainreq.duedateextension = !(0, tools_1.isNullOrUndefined)(train.benefit_continuation_due_date) ? new Date(train.benefit_continuation_due_date) : null;
                newtrainreq.trainingprogram = train.name;
                newtrainreq.trainingprogramcode = train.training_code;
                newtrainreq.status = train.status;
                newtrainreq.trainingid = train.id;
                newtrainreq.isrequired = train.is_required;
                newtrainreq.created = !(0, tools_1.isNullOrUndefined)(train.created) ? new Date(train.created) : new Date();
                newtrainreq.personid = parseInt(train.studentId);
                if (train.reason_code === "BC") {
                    newtrainreq.duedateoverridereason = "Benefits Continuation";
                }
                else if (train.reason_code === "ERH") {
                    newtrainreq.duedateoverridereason = "Emergency Rule Rehire";
                }
                else if (train.reason_code === "CV19") {
                    newtrainreq.duedateoverridereason = "Covid19 Emergency Rule";
                }
                else if (train.reason_code === "BIS") {
                    newtrainreq.duedateoverridereason = "Break In Service Rehire";
                }
                else if (train.reason_code === "RH") {
                    newtrainreq.duedateoverridereason = "Rehire";
                }
                else {
                    newtrainreq.duedateoverridereason = train.reason_code;
                }
                newtrainreq.archived = !(0, tools_1.isNullOrUndefined)(train.archived) ? new Date(train.archived) : null;
                var currentTimeInSeconds = new Date();
                await entityManager.createQueryBuilder()
                    .insert()
                    .into(trainreq_1.trainingrequirement)
                    .values(newtrainreq)
                    .onConflict(`("trainingid") DO UPDATE SET "trackingdate" = :trackingdate, 
                        "requiredhours" = :requiredhours, "duedate" = :duedate, "duedateextension" = :duedateextension, 
                        "trainingprogram" = :trainingprogram, "trainingprogramcode" = :trainingprogramcode, 
                        "status" = :status, "isrequired" = :isrequired,"duedateoverridereason"=:duedateoverridereason,
                        "recordmodifieddate" = :recordmdate,"archived" = :archived
                        WHERE "prod"."trainingrequirement"."trainingid" = :ppid`)
                    .setParameter("trackingdate", newtrainreq.trackingdate)
                    .setParameter("requiredhours", newtrainreq.requiredhours)
                    .setParameter("duedate", newtrainreq.duedate)
                    .setParameter("duedateextension", newtrainreq.duedateextension)
                    .setParameter("trainingprogram", newtrainreq.trainingprogram)
                    .setParameter("trainingprogramcode", newtrainreq.trainingprogramcode)
                    .setParameter("status", newtrainreq.status)
                    .setParameter("duedateoverridereason", newtrainreq.duedateoverridereason)
                    .setParameter("isrequired", newtrainreq.isrequired)
                    .setParameter("ppid", newtrainreq.trainingid)
                    .setParameter("archived", newtrainreq.archived)
                    .setParameter("recordmdate", currentTimeInSeconds)
                    .execute();
            }
        }
        console.log(`Count of trainingrequirement's Updated in the prod.trainingrequirement table for current batch: ${ts.length}`);
        console.log(`Completed Updating the prod.trainingrequirement table for new or updated trainings`);
        entityManager.connection.close();
        return {
            statusCode: 200,
            body: `Queries after eligibility execution: ${queries}`
        };
    }
    catch (error) {
        console.log(`Calling Eligibility Thrown ${error}`);
        throw error;
    }
};
exports.processingMain = processingMain;
//# sourceMappingURL=index.js.map