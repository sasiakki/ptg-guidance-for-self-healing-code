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
exports.Student_status_sete = void 0;
const typeorm_1 = require("typeorm");
const student_1 = require("./student");
let Student_status_sete = class Student_status_sete extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryColumn)({
        nullable: false,
        unique: true
    }),
    __metadata("design:type", String)
], Student_status_sete.prototype, "studentId", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
    }),
    __metadata("design:type", Boolean)
], Student_status_sete.prototype, "isCompliant", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
    }),
    __metadata("design:type", Boolean)
], Student_status_sete.prototype, "isGrandFathered", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
    }),
    __metadata("design:type", Boolean)
], Student_status_sete.prototype, "ahcas_eligible", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
    }),
    __metadata("design:type", String)
], Student_status_sete.prototype, "complianceStatus", void 0);
__decorate([
    (0, typeorm_1.OneToOne)(() => student_1.Studente, student => student.student_status_set),
    __metadata("design:type", student_1.Studente)
], Student_status_sete.prototype, "student", void 0);
Student_status_sete = __decorate([
    (0, typeorm_1.Entity)('student_status_set', { schema: "eligibility" })
], Student_status_sete);
exports.Student_status_sete = Student_status_sete;
//# sourceMappingURL=student-status-set.js.map