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
exports.trainingrequirement = void 0;
const typeorm_1 = require("typeorm");
let trainingrequirement = class trainingrequirement extends typeorm_1.BaseEntity {
};
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)('uuid'),
    __metadata("design:type", Number)
], trainingrequirement.prototype, "trainreq_id", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
        type: 'bigint'
    }),
    __metadata("design:type", Number)
], trainingrequirement.prototype, "personid", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "trackingdate", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], trainingrequirement.prototype, "requiredhours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
        type: "float"
    }),
    __metadata("design:type", Number)
], trainingrequirement.prototype, "earnedhours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Number)
], trainingrequirement.prototype, "transferredhours", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "duedate", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
        default: false
    }),
    __metadata("design:type", Boolean)
], trainingrequirement.prototype, "isoverride", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "duedateextension", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], trainingrequirement.prototype, "trainingprogram", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], trainingrequirement.prototype, "duedateoverridereason", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], trainingrequirement.prototype, "trainingprogramcode", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "completeddate", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", String)
], trainingrequirement.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true,
        unique: true
    }),
    __metadata("design:type", String)
], trainingrequirement.prototype, "trainingid", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Boolean)
], trainingrequirement.prototype, "isrequired", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "created", void 0);
__decorate([
    (0, typeorm_1.Column)({
        nullable: true
    }),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "archived", void 0);
__decorate([
    (0, typeorm_1.CreateDateColumn)(),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "recordcreateddate", void 0);
__decorate([
    (0, typeorm_1.UpdateDateColumn)(),
    __metadata("design:type", Date)
], trainingrequirement.prototype, "recordmodifieddate", void 0);
trainingrequirement = __decorate([
    (0, typeorm_1.Entity)('trainingrequirement', { schema: "prod" })
], trainingrequirement);
exports.trainingrequirement = trainingrequirement;
//# sourceMappingURL=trainreq.js.map