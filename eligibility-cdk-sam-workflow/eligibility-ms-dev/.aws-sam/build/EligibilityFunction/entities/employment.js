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
exports.Employmente = void 0;
const typeorm_1 = require("typeorm");
const student_1 = require("./student");
let Employmente = class Employmente extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)('uuid'),
    __metadata("design:type", Number)
], Employmente.prototype, "emp_id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Employmente.prototype, "name", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false
    }),
    __metadata("design:type", String)
], Employmente.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false
    }),
    __metadata("design:type", String)
], Employmente.prototype, "hire_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Employmente.prototype, "terminate_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false
    }),
    __metadata("design:type", String)
], Employmente.prototype, "training_category", void 0);
__decorate([
    (0, typeorm_1.ManyToOne)(() => student_1.Studente, student => student.employments),
    (0, typeorm_1.JoinColumn)({
        referencedColumnName: 'id'
    }),
    __metadata("design:type", student_1.Studente)
], Employmente.prototype, "student", void 0);
Employmente = __decorate([
    (0, typeorm_1.Entity)('employment', { schema: 'eligibility' })
], Employmente);
exports.Employmente = Employmente;
//# sourceMappingURL=employment.js.map