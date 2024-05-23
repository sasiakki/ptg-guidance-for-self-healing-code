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
exports.Course_completion = void 0;
const repository_1 = require("@loopback/repository");
let Course_completion = class Course_completion extends repository_1.ValueObject {
    constructor(data) {
        super(data);
    }
};
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: true,
    }),
    __metadata("design:type", String)
], Course_completion.prototype, "name", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'string',
        required: false,
    }),
    __metadata("design:type", String)
], Course_completion.prototype, "status", void 0);
__decorate([
    (0, repository_1.property)({
        type: 'date',
        required: false,
    }),
    __metadata("design:type", String)
], Course_completion.prototype, "completed_date", void 0);
Course_completion = __decorate([
    (0, repository_1.model)(),
    __metadata("design:paramtypes", [Object])
], Course_completion);
exports.Course_completion = Course_completion;
//# sourceMappingURL=course-completion.model.js.map