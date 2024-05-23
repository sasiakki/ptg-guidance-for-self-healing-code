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
exports.Credentiale = void 0;
const typeorm_1 = require("typeorm");
const student_1 = require("./student");
let Credentiale = class Credentiale extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)('uuid'),
    __metadata("design:type", Number)
], Credentiale.prototype, "cred_id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Credentiale.prototype, "name", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Credentiale.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Credentiale.prototype, "firstIssuance_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], Credentiale.prototype, "expiration_date", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: false
    }),
    __metadata("design:type", String)
], Credentiale.prototype, "credential_number", void 0);
__decorate([
    (0, typeorm_1.ManyToOne)(() => student_1.Studente, student => student.credentials),
    (0, typeorm_1.JoinColumn)({
        referencedColumnName: 'id'
    }),
    __metadata("design:type", student_1.Studente)
], Credentiale.prototype, "student", void 0);
Credentiale = __decorate([
    (0, typeorm_1.Entity)('credential', { schema: 'eligibility' })
], Credentiale);
exports.Credentiale = Credentiale;
//# sourceMappingURL=credential.js.map