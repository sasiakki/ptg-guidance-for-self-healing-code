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
exports.Studente = void 0;
const credential_1 = require("./credential");
const student_status_set_1 = require("./student-status-set");
const typeorm_1 = require("typeorm");
const employment_1 = require("./employment");
const course_completion_1 = require("./course-completion");
const student_training_1 = require("./student-training");
let Studente = class Studente extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryColumn)({
        unique: true,
        nullable: false,
    }),
    __metadata("design:type", String)
], Studente.prototype, "id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "provider_id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "first_name", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "last_name", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "training_status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "active_training", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "assigned_category", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], Studente.prototype, "num_active_emp", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "prefer_language", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Studente.prototype, "birth_date", void 0);
__decorate([
    (0, typeorm_1.OneToOne)(() => student_status_set_1.Student_status_sete, student_status_set => student_status_set.student),
    __metadata("design:type", student_status_set_1.Student_status_sete)
], Studente.prototype, "student_status_set", void 0);
__decorate([
    (0, typeorm_1.OneToMany)(() => credential_1.Credentiale, credential => credential.student),
    __metadata("design:type", Array)
], Studente.prototype, "credentials", void 0);
__decorate([
    (0, typeorm_1.OneToMany)(() => employment_1.Employmente, employment => employment.student),
    __metadata("design:type", Array)
], Studente.prototype, "employments", void 0);
__decorate([
    (0, typeorm_1.OneToMany)(() => course_completion_1.Course_completione, course_completion => course_completion.student),
    __metadata("design:type", Array)
], Studente.prototype, "course_completions", void 0);
__decorate([
    (0, typeorm_1.OneToMany)(() => student_training_1.Student_traininge, student_training => student_training.student),
    __metadata("design:type", Array)
], Studente.prototype, "trainings", void 0);
Studente = __decorate([
    (0, typeorm_1.Entity)('student', { schema: 'eligibility' })
], Studente);
exports.Studente = Studente;
//# sourceMappingURL=student.js.map