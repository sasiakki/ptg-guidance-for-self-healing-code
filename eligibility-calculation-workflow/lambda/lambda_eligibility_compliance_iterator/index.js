"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processingMain = void 0;
require("reflect-metadata");
const typeorm_1 = require("typeorm");
const prodperson_1 = require("./entities/prodperson");

const processingMain = async (event, context, callback) => {

  var B2B_HOST = "";
  var B2B_USER = "";
  var B2B_PASSWORD = "";
  var B2B_PORT = "";
  var B2B_NAME = "";
  var count = 0;

  try {
    const environment = process.env.environment_type
    console.log("Get aws sdk");

    var aws = require("aws-sdk");
    let secretManager = new aws.SecretsManager({ region: "us-west-2" });
    const dbsecrets = await secretManager.getSecretValue({ SecretId: environment + "/b2bds/rds/system-pipelines" }).promise();
    const parsedResult = JSON.parse(dbsecrets.SecretString);
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
      port: B2B_PORT,
      username: B2B_USER,
      password: B2B_PASSWORD,
      database: B2B_NAME,
      logging: true,
      schema: "eligibility",
      entities: [prodperson_1.Check_person]
    });
    const em = (0, typeorm_1.getManager)();
    console.log("connected to database: " + em.connection.driver.database);

    const entityManager = (0, typeorm_1.getManager)();
    const inputs = await entityManager.createQueryBuilder().select("check_person").from(prodperson_1.Check_person, 'check_person').where("check_person.check_stat = 0").limit(3000).getMany();
    console.log(inputs.length);

    count = inputs.length;

    await conn.close();

  }
  catch (error) {
    console.error(error);
    throw new Error("Unable to connect to db");
  }

  callback(null, {
    count,
    continue: count > 0
  })

}
exports.processingMain = processingMain;
