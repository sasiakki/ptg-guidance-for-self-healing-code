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
exports.Student_traininge = void 0;
const typeorm_1 = require("typeorm");
const student_1 = require("./student");
let Student_traininge = class Student_traininge extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)('uuid'),
    __metadata("design:type", Number)
], Student_traininge.prototype, "cc_id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false,
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "studentId", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "training_code", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "name", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "due_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "tracking_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "completed_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "training_category", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], Student_traininge.prototype, "required_hours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], Student_traininge.prototype, "earned_hours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], Student_traininge.prototype, "transfer_hours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], Student_traininge.prototype, "total_hours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "sfId", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
        default: null
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "benefit_continuation_due_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "created", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "reasoncode", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "archived", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Boolean)
], Student_traininge.prototype, "is_required", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
    }),
    __metadata("design:type", String)
], Student_traininge.prototype, "train_id", void 0);
__decorate([
    (0, typeorm_1.ManyToOne)(() => student_1.Studente, student => student.trainings),
    (0, typeorm_1.JoinColumn)({
        referencedColumnName: 'id'
    }),
    __metadata("design:type", student_1.Studente)
], Student_traininge.prototype, "student", void 0);
Student_traininge = __decorate([
    (0, typeorm_1.Entity)('student_training', { schema: 'eligibility' })
], Student_traininge);
exports.Student_traininge = Student_traininge;
//# sourceMappingURL=student-training.js.map