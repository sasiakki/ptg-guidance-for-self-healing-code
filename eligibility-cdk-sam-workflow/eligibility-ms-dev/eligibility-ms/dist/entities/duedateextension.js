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
exports.duedateextension = void 0;
const typeorm_1 = require("typeorm");
let duedateextension = class duedateextension extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryColumn)({
        nullable: false,
        unique: true
    }),
    __metadata("design:type", String)
], duedateextension.prototype, "trainingid", void 0);
__decorate([
    (0, typeorm_1.PrimaryColumn)({
        nullable: false,
        unique: true
    }),
    __metadata("design:type", Number)
], duedateextension.prototype, "personid", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], duedateextension.prototype, "duedateoverridereason", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], duedateextension.prototype, "employerrequested", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], duedateextension.prototype, "bcapproveddate", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], duedateextension.prototype, "duedateoverride", void 0);
__decorate([
    (0, typeorm_1.CreateDateColumn)(),
    __metadata("design:type", Date)
], duedateextension.prototype, "recordcreateddate", void 0);
__decorate([
    (0, typeorm_1.UpdateDateColumn)(),
    __metadata("design:type", Date)
], duedateextension.prototype, "recordmodifieddate", void 0);
duedateextension = __decorate([
    (0, typeorm_1.Entity)('duedateextension', { schema: "prod" })
], duedateextension);
exports.duedateextension = duedateextension;
//# sourceMappingURL=duedateextension.js.map