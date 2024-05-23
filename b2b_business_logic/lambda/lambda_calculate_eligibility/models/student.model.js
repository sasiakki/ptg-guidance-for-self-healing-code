"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Student = void 0;
const repository_1 = require("@loopback/repository");
const student_training_model_1 = require("./student-training.model");
const credential_model_1 = require("./credential.model");
const employment_model_1 = require("./employment.model");
const student_status_set_model_1 = require("./student-status-set.model");
const course_completion_model_1 = require("./course-completion.model");
let Student = class Student extends repository_1.Entity {
    constructor(data) {
        super(data);
    }
    name() {
    }
};
__decorate([
    (0, repository_1.property)({
        type: 'string',
        id: true,
        required: true,
    }),
    __metadata("design:type", String)
], Student.prototype, "id", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
    }),
    __metadata("design:type", String)
], Student.prototype, "provider_id", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "first_name", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "last_name", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "training_status", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "status", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "active_training", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "assigned_category", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'number'
    }),
    __metadata("design:type", Number)
], Student.prototype, "num_active_emp", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string'
    }),
    __metadata("design:type", String)
], Student.prototype, "prefer_language", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date'
    }),
    __metadata("design:type", String)
], Student.prototype, "birth_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: student_status_set_model_1.Student_status_set
    }),
    __metadata("design:type", student_status_set_model_1.Student_status_set)
], Student.prototype, "student_status_set", void 0);
__decorate([
    repository_1.property.array(credential_model_1.Credential),
    __metadata("design:type", Array)
], Student.prototype, "credentials", void 0);
__decorate([
    repository_1.property.array(employment_model_1.Employment),
    __metadata("design:type", Array)
], Student.prototype, "employments", void 0);
__decorate([
    repository_1.property.array(course_completion_model_1.Course_completion),
    __metadata("design:type", Array)
], Student.prototype, "course_completions", void 0);
__decorate([
    (0, repository_1.hasMany)(() => student_training_model_1.Student_training),
    __metadata("design:type", Array)
], Student.prototype, "trainings", void 0);
Student = __decorate([
    (0, repository_1.model)(),
    __metadata("design:paramtypes", [Object])
], Student);
exports.Student = Student;
//# sourceMappingURL=student.model.js.map