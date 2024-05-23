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
exports.Course_completione = void 0;
const typeorm_1 = require("typeorm");
const student_1 = require("./student");
let Course_completione = class Course_completione extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)('uuid'),
    __metadata("design:type", Number)
], Course_completione.prototype, "cc_id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        type: 'bigint',
        nullable: false
    }),
    __metadata("design:type", Number)
], Course_completione.prototype, "personid", void 0);
__decorate([
    (0, typeorm_1.Column)(),
    __metadata("design:type", String)
], Course_completione.prototype, "name", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Course_completione.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Course_completione.prototype, "completed_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Course_completione.prototype, "sfId", void 0);
__decorate([
    (0, typeorm_1.ManyToOne)(() => student_1.Studente, student => student.course_completions),
    (0, typeorm_1.JoinColumn)({
        referencedColumnName: 'id'
    }),
    __metadata("design:type", student_1.Studente)
], Course_completione.prototype, "student", void 0);
Course_completione = __decorate([
    (0, typeorm_1.Entity)('course_completion', { schema: 'eligibility' })
], Course_completione);
exports.Course_completione = Course_completione;
//# sourceMappingURL=course-completion.js.map