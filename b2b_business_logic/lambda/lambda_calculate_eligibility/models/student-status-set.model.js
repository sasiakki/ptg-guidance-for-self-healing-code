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
exports.Student_status_set = void 0;
const repository_1 = require("@loopback/repository");
let Student_status_set = class Student_status_set extends repository_1.ValueObject {
    constructor(data) {
        super(data);
    }
};
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: false,
    }),
    __metadata("design:type", String)
], Student_status_set.prototype, "studentId", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'boolean',
        required: false,
    }),
    __metadata("design:type", Boolean)
], Student_status_set.prototype, "isCompliant", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'boolean',
        required: false,
    }),
    __metadata("design:type", Boolean)
], Student_status_set.prototype, "isGrandFathered", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'boolean',
        required: false,
    }),
    __metadata("design:type", Boolean)
], Student_status_set.prototype, "ahcas_eligible", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: false,
    }),
    __metadata("design:type", String)
], Student_status_set.prototype, "complianceStatus", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'boolean',
        required: false,
    }),
    __metadata("design:type", Boolean)
], Student_status_set.prototype, "isRehire", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'boolean',
        required: false,
    }),
    __metadata("design:type", Boolean)
], Student_status_set.prototype, "isCredentialExpired", void 0);
Student_status_set = __decorate([
    (0, repository_1.model)(),
    __metadata("design:paramtypes", [Object])
], Student_status_set);
exports.Student_status_set = Student_status_set;
//# sourceMappingURL=student-status-set.model.js.map