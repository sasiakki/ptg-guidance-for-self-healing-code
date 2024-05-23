import "reflect-metadata";
import { createConnection, getManager } from "typeorm";
import { Studente } from "./entities/student";
import { Credentiale } from "./entities/credential";
import { Student_status_sete } from "./entities/student-status-set";
import { Student_traininge } from "./entities/student-training";
import { duedateextension } from "./entities/duedateextension";
import { Employmente } from "./entities/employment";
import { Course_completione } from "./entities/course-completion";
import { Check_person } from "./entities/checkperson";
import {
    Student_training,
    Student_status_set,
    Student,
} from './models'; // which models are affected? will changes only be required to properties (based on ERD)? 
import {
    Student_training_logic
} from './bizlogics';
import * as _ from 'lodash';
import { b2b_service } from "./services/b2b_service";
import { ccs_service } from "./services/ccs_service";
import { training_service } from "./services/training_service";
import { isNullOrUndefined } from "./helpers/tools";
import { trainingrequirement } from "./entities/trainreq";
import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";
import { cred_service } from "./services/cred_service";
import { prod_person } from "./entities/production_person";
import { learner } from "./entities/learner";
import { Helper } from "./helpers/helper";

export const processingMain = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
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
        B2B_NAME =  parsedResult.dbname;
    }
    catch (error) {
        console.error(error);
        throw new Error("Unable to get secrets");
    }

    try {
        let conn = await createConnection({
            type: "postgres",
            host: B2B_HOST,
            port: +B2B_PORT,
            username: B2B_USER,
            password: B2B_PASSWORD,
            database: B2B_NAME,
            logging: true,
            synchronize: false,
            schema: "eligibility",
            entities: [Credentiale, Studente, Student_status_sete, Student_traininge, Employmente, Course_completione, Check_person,duedateextension, trainingrequirement, prod_person, learner]
        });
        const em = getManager();
        console.log("connected to database: " + em.connection.driver.database);
    } catch (error) {
        console.error(error);
        throw new Error("Unable to connect to db");
    }
    const entityManager = getManager()
    ///  ATTENTION!!! 'limit' field to be removed in production. currently capable of processing 10,000 persons in 12 mins avg. 
    const inputs = await entityManager.createQueryBuilder().select("check_person").from(Check_person, 'check_person').where("check_person.check_stat = 0").limit(3000).getMany();
    console.log(inputs.length)

    console.log(`Count of student id's processing in current batch: ${inputs.length}`);

    try {
        let ts: Student_training[] = new Array<Student_training>();

        for (const i of inputs) {
            let student: Student = await b2b_service.getStudent(i);
            var parsedstudentid = parseInt(student.id, 10);
            console.log(`Processing for the studentid:${parsedstudentid}`)
            // console.log(`${JSON.stringify(student)}`);

            // disabled; transcripts are currently not being used
            // const ccs = await entityManager.createQueryBuilder()
            //     .select("course_completion")
            //     .from(Course_completione, 'course_completion')
            //     .where("course_completion.studentId = :id", { id: parsedstudentid })
            //     .getMany();

            // student.course_completions = await ccs_service.getCourseCompletions(ccs);
            // console.log(`studentid: ${parsedstudentid}, transcripts count: ${(student.course_completions) ? student.course_completions.length : 0}`);
            // console.log(`studentid: ${parsedstudentid}, transcripts list: ${JSON.stringify(student.course_completions)}`);

            const creds = await entityManager.createQueryBuilder()
                .select("credential")
                .from(Credentiale, 'credential')
                .where("credential.studentId = :id", { id: parsedstudentid })
                .getMany();

            student.credentials = await cred_service.getCredentials(creds);
            // console.log(`studentid: ${parsedstudentid}, credentials count: ${(student.credentials) ? student.credentials.length : 0}`);
            // console.log(`studentid: ${parsedstudentid}, credentials list: ${JSON.stringify(student.credentials)}`);

            const trains = await entityManager.createQueryBuilder()
                .select("student_training")
                .from(Student_traininge, 'student_training')
                .where("student_training.studentId = :id", { id: parsedstudentid })
                .getMany();

            const sortHistory = function(training1: Student_training, training2: Student_training){
                if(training1.status > training2.status){return -1;}
                if(training1.status<training2.status){return 1;}
                    return 0;
            }

            let history: Student_training[] = await training_service.getTrainings(trains)
            student.trainings = (history) ? history.sort(sortHistory):history;
            console.log(`studentid: ${parsedstudentid}, trainings count: ${(student.trainings) ? student.trainings.length : 0}`);
            // console.log(`studentid: ${parsedstudentid}, trainings list: ${JSON.stringify(student.trainings)}`);
            console.log('student:', student);

            
            let recalculateEligibility:boolean;
            let ss: Student_status_set, training: Student_training[];
            [ss, training, recalculateEligibility] = Student_training_logic .evaluateStudentTraining(student, history);

            // status changed from non-compliant => compliant
            if (recalculateEligibility === true){
                console.log(`studentid: ${student.id}; !!! RecalculateElgiibility !!!`);
                const firstRunTrainings = _.cloneDeep(training);
                let secondRunTrainings: Student_training[];
                [ss, secondRunTrainings, recalculateEligibility] = Student_training_logic.evaluateStudentTraining(student, Helper.mergeTrainings(training, history));

                training = Helper.mergeTrainings(firstRunTrainings, secondRunTrainings);
                console.log('studentid:', student.id, ' MERGED assigendTrainings: ', training);
            }

            await entityManager.createQueryBuilder().update(prod_person)
                .set({ trainingstatus: ss.complianceStatus.toLowerCase(),recordmodifieddate: new Date() })
                .where("personid = :id AND trainingstatus <> :complianceStatus", 
                { id: student.id, complianceStatus: ss.complianceStatus.toLowerCase() })
                .execute();

            await entityManager.createQueryBuilder().update(learner)
                .set({ compliant: ss.complianceStatus.toLowerCase(),recordmodifieddate: new Date() })
                .where("personid = :id AND compliant <> :complianceStatus", 
                { id: student.id, complianceStatus: ss.complianceStatus.toLowerCase() })
                .execute();

            console.log(`studentid: ${parsedstudentid}, new or updated trainings: ${JSON.stringify(training)}`);
            console.log(`End of processing for the studentid :${parsedstudentid}`);

            for (const t1 of training) {
                if (!isNullOrUndefined(t1)) {
                    ts.push(t1)
                }
            }
            await entityManager.createQueryBuilder().update(Check_person)
                .set({ check_stat: 1 })
                .where("pgc_id = :id", { id: i.pgc_id })
                .execute();
        }

        console.log(`studentid :${parsedstudentid}; Updating the prod.trainingrequirement table for new or updated trainings`)

        for (const train of ts) {
            if (!isNullOrUndefined(train)) {
                if (train.reason_code) {
                    const newduedates: duedateextension = new duedateextension();
                    newduedates.trainingid = train.id;
                    newduedates.employerrequested = '';
                    newduedates.personid = parseInt(train.studentId);
                    newduedates.bcapproveddate = new Date();
                    if (train.reason_code === "BC") {
                        newduedates.duedateoverridereason = "Benefits Continuation"; 
                    } else if (train.reason_code === "ERH") {
                        newduedates.duedateoverridereason = "Emergency Rule Rehire"; 
                    } else if (train.reason_code === "CV19") {
                        newduedates.duedateoverridereason = "Covid19 Emergency Rule"; 
                    } else if (train.reason_code === "BIS") {
                        newduedates.duedateoverridereason = "Break In Service Rehire";
                    } else if (train.reason_code === "RH") {
                        newduedates.duedateoverridereason = "Rehire";
                    } else {
                        newduedates.duedateoverridereason = train.reason_code; // Adding new column with default value
                    }
                    newduedates.duedateoverride = !isNullOrUndefined(train.benefit_continuation_due_date) ? new Date(train.benefit_continuation_due_date) : null;
                    await entityManager.createQueryBuilder()
                        .insert()
                        .into(duedateextension)
                        .values(newduedates)
                        .execute();
                }

                const newtrainreq: trainingrequirement = new trainingrequirement();
                newtrainreq.trackingdate = !isNullOrUndefined(train.tracking_date) ? new Date(train.tracking_date) : null;
                newtrainreq.requiredhours = train.required_hours;
                newtrainreq.duedate = !isNullOrUndefined(train.due_date) ? new Date(train.due_date) : null;
                newtrainreq.duedateextension = !isNullOrUndefined(train.benefit_continuation_due_date) ? new Date(train.benefit_continuation_due_date) : null;
                newtrainreq.trainingprogram = train.name;
                newtrainreq.trainingprogramcode = train.training_code;
                newtrainreq.status = train.status;
                newtrainreq.trainingid = train.id;
                newtrainreq.isrequired = train.is_required;
                newtrainreq.created = !isNullOrUndefined(train.created) ? new Date(train.created) : new Date();
                newtrainreq.personid = parseInt(train.studentId);
                if (train.reason_code === "BC") {
                    newtrainreq.duedateoverridereason = "Benefits Continuation"; 
                } else if (train.reason_code === "ERH") {
                    newtrainreq.duedateoverridereason = "Emergency Rule Rehire"; 
                } else if (train.reason_code === "CV19") {
                    newtrainreq.duedateoverridereason = "Covid19 Emergency Rule"; 
                } else if (train.reason_code === "BIS") {
                    newtrainreq.duedateoverridereason = "Break In Service Rehire"; 
                } else if (train.reason_code === "RH") {
                    newtrainreq.duedateoverridereason = "Rehire";
                } else {
                    newtrainreq.duedateoverridereason = train.reason_code; 
                }
                newtrainreq.archived = !isNullOrUndefined(train.archived) ? new Date(train.archived) : null;

                var currentTimeInSeconds = new Date();
                await entityManager.createQueryBuilder()
                .insert()
                .into(trainingrequirement)
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
        console.log(`Completed Updating the prod.trainingrequirement table for new or updated trainings`)
        entityManager.connection.close();
        return {
            statusCode: 200,
            body: `Queries after eligibility execution: ${queries}`
        }
    } catch (error) {
        console.log(`Calling Eligibility Thrown ${error}`);
        throw error;
    }
}
