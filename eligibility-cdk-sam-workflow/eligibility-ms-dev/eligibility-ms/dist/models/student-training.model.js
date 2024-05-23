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
exports.Student_training = void 0;
const repository_1 = require("@loopback/repository");
const student_model_1 = require("./student.model");
let Student_training = class Student_training extends repository_1.Entity {
    getId() {
        return this.id;
    }
    constructor(data) {
        super(data);
    }
};
__decorate([
    (0, repository_1.belongsTo)(() => student_model_1.Student),
    __metadata("design:type", String)
], Student_training.prototype, "studentId", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: true,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "training_code", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: false,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "name", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: true,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "status", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
    }),
    __metadata("design:type", String)
], Student_training.prototype, "due_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
    }),
    __metadata("design:type", String)
], Student_training.prototype, "tracking_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: false,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "completed_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
    }),
    __metadata("design:type", String)
], Student_training.prototype, "training_category", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'number',
        required: false,
    }),
    __metadata("design:type", Number)
], Student_training.prototype, "required_hours", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'number',
        required: false,
    }),
    __metadata("design:type", Number)
], Student_training.prototype, "earned_hours", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'number',
        required: false,
    }),
    __metadata("design:type", Number)
], Student_training.prototype, "transfer_hours", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'number',
        required: false,
    }),
    __metadata("design:type", Number)
], Student_training.prototype, "total_hours", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: false,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "benefit_continuation_due_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: false,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "created", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: false,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "archived", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'boolean',
        required: false,
    }),
    __metadata("design:type", Boolean)
], Student_training.prototype, "is_required", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: true,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "reason_code", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        id: true,
    }),
    __metadata("design:type", String)
], Student_training.prototype, "id", void 0);
Student_training = __decorate([
    (0, repository_1.model)(),
    __metadata("design:paramtypes", [Object])
], Student_training);
exports.Student_training = Student_training;
//# sourceMappingURL=student-training.model.js.map