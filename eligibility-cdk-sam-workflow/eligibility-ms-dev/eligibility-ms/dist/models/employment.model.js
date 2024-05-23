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
exports.Employment = void 0;
const repository_1 = require("@loopback/repository");
let Employment = class Employment extends repository_1.ValueObject {
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
], Employment.prototype, "name", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: true,
    }),
    __metadata("design:type", String)
], Employment.prototype, "status", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: true,
    }),
    __metadata("design:type", String)
], Employment.prototype, "hire_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: true,
    }),
    __metadata("design:type", String)
], Employment.prototype, "rehire_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: false,
    }),
    __metadata("design:type", String)
], Employment.prototype, "terminate_date", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: true,
    }),
    __metadata("design:type", String)
], Employment.prototype, "training_category", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: true,
    }),
    __metadata("design:type", String)
], Employment.prototype, "tc_tracking_date", void 0);
Employment = __decorate([
    (0, repository_1.model)(),
    __metadata("design:paramtypes", [Object])
], Employment);
exports.Employment = Employment;
//# sourceMappingURL=employment.model.js.map