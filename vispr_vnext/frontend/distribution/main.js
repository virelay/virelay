(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["main"],{

/***/ "./$$_lazy_route_resource lazy recursive":
/*!******************************************************!*\
  !*** ./$$_lazy_route_resource lazy namespace object ***!
  \******************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function webpackEmptyAsyncContext(req) {
	// Here Promise.resolve().then() is used instead of new Promise() to prevent
	// uncaught exception popping up in devtools
	return Promise.resolve().then(function() {
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	});
}
webpackEmptyAsyncContext.keys = function() { return []; };
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
module.exports = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = "./$$_lazy_route_resource lazy recursive";

/***/ }),

/***/ "./node_modules/raw-loader/dist/cjs.js!./src/app/app.component.html":
/*!**************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/app.component.html ***!
  \**************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("\n<div class=\"main-container\">\n    <header class=\"header header-3\">\n        <div class=\"branding\">\n            <a href=\"/\" class=\"nav-link\">\n                <span class=\"vispr-logo\"></span>\n                <span class=\"title\">VISPR</span>\n            </a>\n        </div>\n\n        <div *ngIf=\"projects\" class=\"header-nav\">\n            <a *ngFor=\"let project of projects\" routerLink=\"/projects/{{ project.id }}\" routerLinkActive=\"active\" class=\"nav-link nav-text\">{{ project.name }}</a>\n        </div>\n    </header>\n\n    <div class=\"content-container\">\n        <div class=\"content-area\">\n            <router-outlet>\n                <span *ngIf=\"isLoadingProjects\" class=\"spinner spinner-centered\"></span>\n            </router-outlet>\n        </div>\n    </div>\n</div>\n");

/***/ }),

/***/ "./node_modules/raw-loader/dist/cjs.js!./src/app/components/before-and-after-slider/before-and-after-slider.component.html":
/*!*********************************************************************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/components/before-and-after-slider/before-and-after-slider.component.html ***!
  \*********************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("\n<div class=\"before-and-after-slider-container\">\n    <div #sliderHandle class=\"slider-handle\"></div>\n    <img #beforeImage class=\"before-image\" [src]=\"beforeImageSource\" [alt]=\"alt\" />\n    <img #afterImage class=\"after-image\" [src]=\"afterImageSource\" [alt]=\"alt\" />\n</div>\n");

/***/ }),

/***/ "./node_modules/raw-loader/dist/cjs.js!./src/app/components/embedding-visualizer/embedding-visualizer.component.html":
/*!***************************************************************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/components/embedding-visualizer/embedding-visualizer.component.html ***!
  \***************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("\n<div class=\"container\" [style.pointer-events]=\"disabled ? 'none' : 'auto'\">\n    <div #selectionBox class=\"selection-box\"></div>\n    <canvas #renderTarget [style.opacity]=\"disabled ? 0.2 : 1.0\"></canvas>\n</div>\n");

/***/ }),

/***/ "./node_modules/raw-loader/dist/cjs.js!./src/app/modules/projects/pages/index/index.page.html":
/*!****************************************************************************************************!*\
  !*** ./node_modules/raw-loader/dist/cjs.js!./src/app/modules/projects/pages/index/index.page.html ***!
  \****************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("\n<span *ngIf=\"isLoading\" class=\"spinner spinner-centered\"></span>\n\n<div *ngIf=\"project\" id=\"panels-container\">\n\n    <aside id=\"options-pane\">\n        <clr-select-container>\n            <label>Analysis method</label>\n            <select clrSelect name=\"analysis-method\" [(ngModel)]=\"selectedAnalysisMethod\">\n                <option *ngIf=\"!selectedAnalysisMethod\" [ngValue]=\"null\">Select an analysis method...</option>\n                <option *ngFor=\"let analysisMethod of project.analysisMethods\" [ngValue]=\"analysisMethod\">{{ analysisMethod.name }}</option>\n            </select>\n        </clr-select-container>\n        <clr-select-container *ngIf=\"selectedAnalysisMethod\">\n            <label>Category</label>\n            <select clrSelect name=\"category\" [(ngModel)]=\"selectedCategory\">\n                <option *ngIf=\"!selectedCategory\" [ngValue]=\"null\">Select a category...</option>\n                <option *ngFor=\"let category of selectedAnalysisMethod.categories\" [ngValue]=\"category\">{{ category.humanReadableName }} ({{ category.name }})</option>\n            </select>\n        </clr-select-container>\n        <clr-select-container *ngIf=\"selectedAnalysisMethod\">\n            <label>Clustering</label>\n            <select clrSelect class=\"full-width\" name=\"clustering\" [(ngModel)]=\"selectedClustering\">\n                <option *ngIf=\"!selectedClustering\" [ngValue]=\"null\">Select a clustering...</option>\n                <option *ngFor=\"let clustering of selectedAnalysisMethod.clusterings\" [value]=\"clustering\">{{ clustering }}</option>\n            </select>\n        </clr-select-container>\n        <clr-select-container *ngIf=\"selectedAnalysisMethod\">\n            <label>Embedding</label>\n            <select clrSelect name=\"embedding\" [(ngModel)]=\"selectedEmbedding\">\n                <option *ngIf=\"!selectedEmbedding\" [ngValue]=\"null\">Select a embedding...</option>\n                <option *ngFor=\"let embedding of selectedAnalysisMethod.embeddings\" [value]=\"embedding\">{{ embedding }}</option>\n            </select>\n        </clr-select-container>\n        <clr-select-container *ngIf=\"embeddingDimensions && embeddingDimensions.length > 2\">\n            <label>X-Axis</label>\n            <select clrSelect name=\"horizontal-axis-dimension-index\" [(ngModel)]=\"firstDimension\">\n                <option *ngFor=\"let index of embeddingDimensions\" [value]=\"index\">{{ index }}</option>\n            </select>\n        </clr-select-container>\n        <clr-select-container *ngIf=\"embeddingDimensions && embeddingDimensions.length > 2\">\n            <label>Y-Axis</label>\n            <select clrSelect name=\"vertical-axis-dimension-index\" [(ngModel)]=\"secondDimension\">\n                <option *ngFor=\"let index of embeddingDimensions\" [value]=\"index\">{{ index }}</option>\n            </select>\n        </clr-select-container>\n        <clr-select-container *ngIf=\"colorMaps\">\n            <label>Color map</label>\n            <select clrSelect name=\"color-map\" [(ngModel)]=\"selectedColorMap\">\n                <option *ngIf=\"!selectedColorMap\" [ngValue]=\"null\">Select a color map...</option>\n                <option *ngFor=\"let colorMap of colorMaps\" [ngValue]=\"colorMap\">{{ colorMap.humanReadableName }}</option>\n            </select>\n        </clr-select-container>\n        <img *ngIf=\"selectedColorMap\" [src]=\"selectedColorMap.url\" [alt]=\"selectedColorMap.humanReadableName\" />\n    </aside>\n\n    <section id=\"embedding-plot\">\n        <app-embedding-visualizer\n            *ngIf=\"analysis\"\n            [(ngModel)]=\"selectedDataPoints\"\n            backgroundColor=\"#EFEFEF\"\n            [embedding]=\"analysis.embedding\"\n            [firstDimension]=\"firstDimension\"\n            [secondDimension]=\"secondDimension\"\n            (onHover)=\"onHoverAsync($event)\"\n            (onUnhover)=\"onUnhover($event)\">\n        </app-embedding-visualizer>\n\n        <img\n            id=\"attribution-hover-preview\"\n            *ngIf=\"datasetSampleHoverPreview && isHovering\"\n            [src]=\"datasetSampleHoverPreview.url\"\n        />\n    </section>\n\n    <aside id=\"selected-attributions\">\n        <span *ngIf=\"isLoadingAttributions\" class=\"spinner spinner-locally-centered\"></span>\n\n        <div *ngIf=\"!isLoadingAttributions && (!selectedDataPoints || selectedDataPoints.length === 0)\" id=\"selection-hint\">\n            <p>Select data points to display attributions...</p>\n        </div>\n\n        <div *ngIf=\"!isLoadingAttributions && selectedAttributions && selectedAttributions.length > 0\" id=\"selected-attribution-list\">\n            <div *ngFor=\"let selectedAttribution of selectedAttributions\" class=\"selected-attribution\" [title]=\"selectedAttribution.attribution.labelDisplay\">\n                <app-before-and-after-slider\n                    [beforeImageSource]=\"selectedAttribution.attribution.urls[selectedColorMap.name]\"\n                    [afterImageSource]=\"selectedAttribution.sample.url\"\n                    [alt]=\"selectedAttribution.attribution.labelDisplay\">\n                </app-before-and-after-slider>\n                <p><span [style.color]=\"selectedAttribution.color\">&#11044;</span> Cluster {{ selectedAttribution.clusterIndex + 1 }}</p>\n            </div>\n        </div>\n    </aside>\n\n    <aside id=\"cluster-pane\">\n        <plotly-plot\n            *ngIf=\"eigenValuesGraphData\"\n            [data]=\"eigenValuesGraphData\"\n            [layout]=\"eigenValuesGraphLayout\"\n            [config]=\"{ displayModeBar: false }\"\n            [style]=\"{ width: '226px', height: '400px', 'marginLeft': '12px' }\">\n        </plotly-plot>\n\n        <div class=\"cluster-selection-buttons-container\">\n            <button *ngFor=\"let cluster of availableClusters\" class=\"btn btn-outline\" (click)=\"selectCluster(cluster.index)\">\n                <span [style.color]=\"cluster.color\">&#11044;</span> Select cluster {{ cluster.index + 1 }}\n            </button>\n        </div>\n    </aside>\n\n    <footer id=\"status-bar\">\n        <clr-icon shape=\"library\"></clr-icon> <strong>Project:</strong> {{ project.name }}\n        <clr-icon shape=\"storage\"></clr-icon> <strong>Dataset:</strong> {{ project.dataset }}\n        <clr-icon shape=\"organization\"></clr-icon> <strong>Model:</strong> {{ project.model }}\n    </footer>\n</div>\n");

/***/ }),

/***/ "./node_modules/tslib/tslib.es6.js":
/*!*****************************************!*\
  !*** ./node_modules/tslib/tslib.es6.js ***!
  \*****************************************/
/*! exports provided: __extends, __assign, __rest, __decorate, __param, __metadata, __awaiter, __generator, __exportStar, __values, __read, __spread, __spreadArrays, __await, __asyncGenerator, __asyncDelegator, __asyncValues, __makeTemplateObject, __importStar, __importDefault */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__extends", function() { return __extends; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__assign", function() { return __assign; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__rest", function() { return __rest; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__decorate", function() { return __decorate; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__param", function() { return __param; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__metadata", function() { return __metadata; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__awaiter", function() { return __awaiter; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__generator", function() { return __generator; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__exportStar", function() { return __exportStar; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__values", function() { return __values; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__read", function() { return __read; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__spread", function() { return __spread; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__spreadArrays", function() { return __spreadArrays; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__await", function() { return __await; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__asyncGenerator", function() { return __asyncGenerator; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__asyncDelegator", function() { return __asyncDelegator; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__asyncValues", function() { return __asyncValues; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__makeTemplateObject", function() { return __makeTemplateObject; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__importStar", function() { return __importStar; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "__importDefault", function() { return __importDefault; });
/*! *****************************************************************************
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
MERCHANTABLITY OR NON-INFRINGEMENT.

See the Apache Version 2.0 License for specific language governing permissions
and limitations under the License.
***************************************************************************** */
/* global Reflect, Promise */

var extendStatics = function(d, b) {
    extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return extendStatics(d, b);
};

function __extends(d, b) {
    extendStatics(d, b);
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
}

var __assign = function() {
    __assign = Object.assign || function __assign(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
        }
        return t;
    }
    return __assign.apply(this, arguments);
}

function __rest(s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
}

function __decorate(decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
}

function __param(paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
}

function __metadata(metadataKey, metadataValue) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(metadataKey, metadataValue);
}

function __awaiter(thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
}

function __generator(thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
}

function __exportStar(m, exports) {
    for (var p in m) if (!exports.hasOwnProperty(p)) exports[p] = m[p];
}

function __values(o) {
    var m = typeof Symbol === "function" && o[Symbol.iterator], i = 0;
    if (m) return m.call(o);
    return {
        next: function () {
            if (o && i >= o.length) o = void 0;
            return { value: o && o[i++], done: !o };
        }
    };
}

function __read(o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
}

function __spread() {
    for (var ar = [], i = 0; i < arguments.length; i++)
        ar = ar.concat(__read(arguments[i]));
    return ar;
}

function __spreadArrays() {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};

function __await(v) {
    return this instanceof __await ? (this.v = v, this) : new __await(v);
}

function __asyncGenerator(thisArg, _arguments, generator) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var g = generator.apply(thisArg, _arguments || []), i, q = [];
    return i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i;
    function verb(n) { if (g[n]) i[n] = function (v) { return new Promise(function (a, b) { q.push([n, v, a, b]) > 1 || resume(n, v); }); }; }
    function resume(n, v) { try { step(g[n](v)); } catch (e) { settle(q[0][3], e); } }
    function step(r) { r.value instanceof __await ? Promise.resolve(r.value.v).then(fulfill, reject) : settle(q[0][2], r); }
    function fulfill(value) { resume("next", value); }
    function reject(value) { resume("throw", value); }
    function settle(f, v) { if (f(v), q.shift(), q.length) resume(q[0][0], q[0][1]); }
}

function __asyncDelegator(o) {
    var i, p;
    return i = {}, verb("next"), verb("throw", function (e) { throw e; }), verb("return"), i[Symbol.iterator] = function () { return this; }, i;
    function verb(n, f) { i[n] = o[n] ? function (v) { return (p = !p) ? { value: __await(o[n](v)), done: n === "return" } : f ? f(v) : v; } : f; }
}

function __asyncValues(o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
}

function __makeTemplateObject(cooked, raw) {
    if (Object.defineProperty) { Object.defineProperty(cooked, "raw", { value: raw }); } else { cooked.raw = raw; }
    return cooked;
};

function __importStar(mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (Object.hasOwnProperty.call(mod, k)) result[k] = mod[k];
    result.default = mod;
    return result;
}

function __importDefault(mod) {
    return (mod && mod.__esModule) ? mod : { default: mod };
}


/***/ }),

/***/ "./src/app/app.component.scss":
/*!************************************!*\
  !*** ./src/app/app.component.scss ***!
  \************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = (".vispr-logo {\n  background-image: url(/assets/images/vispr-logo.png);\n  background-size: 36px 36px;\n  margin-right: 11px;\n  height: 36px;\n  width: 36px;\n}\n\n.content-area {\n  padding: 0 !important;\n}\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2RuZXVtYW5uL1JlcG9zaXRvcmllcy9zcHJpbmNsL3Zpc3ByX3ZuZXh0L2Zyb250ZW5kL3NyYy9hcHAvYXBwLmNvbXBvbmVudC5zY3NzIiwic3JjL2FwcC9hcHAuY29tcG9uZW50LnNjc3MiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQ0E7RUFDSSxvREFBQTtFQUNBLDBCQUFBO0VBQ0gsa0JBQUE7RUFDQSxZQUFBO0VBQ0EsV0FBQTtBQ0FEOztBREdBO0VBQ0MscUJBQUE7QUNBRCIsImZpbGUiOiJzcmMvYXBwL2FwcC5jb21wb25lbnQuc2NzcyIsInNvdXJjZXNDb250ZW50IjpbIlxuLnZpc3ByLWxvZ28ge1xuICAgIGJhY2tncm91bmQtaW1hZ2U6IHVybCgvYXNzZXRzL2ltYWdlcy92aXNwci1sb2dvLnBuZyk7XG4gICAgYmFja2dyb3VuZC1zaXplOiAzNnB4IDM2cHg7XG5cdG1hcmdpbi1yaWdodDogMTFweDtcblx0aGVpZ2h0OiAzNnB4O1xuXHR3aWR0aDogMzZweDtcbn1cblxuLmNvbnRlbnQtYXJlYSB7XG5cdHBhZGRpbmc6IDAgIWltcG9ydGFudDtcbn1cbiIsIi52aXNwci1sb2dvIHtcbiAgYmFja2dyb3VuZC1pbWFnZTogdXJsKC9hc3NldHMvaW1hZ2VzL3Zpc3ByLWxvZ28ucG5nKTtcbiAgYmFja2dyb3VuZC1zaXplOiAzNnB4IDM2cHg7XG4gIG1hcmdpbi1yaWdodDogMTFweDtcbiAgaGVpZ2h0OiAzNnB4O1xuICB3aWR0aDogMzZweDtcbn1cblxuLmNvbnRlbnQtYXJlYSB7XG4gIHBhZGRpbmc6IDAgIWltcG9ydGFudDtcbn0iXX0= */");

/***/ }),

/***/ "./src/app/app.component.ts":
/*!**********************************!*\
  !*** ./src/app/app.component.ts ***!
  \**********************************/
/*! exports provided: AppComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppComponent", function() { return AppComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/router */ "./node_modules/@angular/router/fesm5/router.js");
/* harmony import */ var src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! src/services/projects/projects.service */ "./src/services/projects/projects.service.ts");




/**
 * Represents the app component, which is the entry-point to the VISPR application.
 */
var AppComponent = /** @class */ (function () {
    /**
     * Initializes a new AppComponent instance.
     * @param projectsService The projects service, which is used to load the projects of the current workspace.
     * @param router The router, which is used to navigate to the projects.
     */
    function AppComponent(projectsService, router) {
        this.projectsService = projectsService;
        this.router = router;
    }
    /**
     * Is invoked when the app component is being initialized. Loads the projects from the server.
     */
    AppComponent.prototype.ngOnInit = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            var _a;
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_b) {
                switch (_b.label) {
                    case 0:
                        // Loads the projects from the RESTful API
                        this.isLoadingProjects = true;
                        _a = this;
                        return [4 /*yield*/, this.projectsService.getAsync()];
                    case 1:
                        _a.projects = _b.sent();
                        this.isLoadingProjects = false;
                        // Navigates the user to the first project
                        this.router.navigate(['projects', this.projects[0].id]);
                        return [2 /*return*/];
                }
            });
        });
    };
    AppComponent.ctorParameters = function () { return [
        { type: src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_3__["ProjectsService"] },
        { type: _angular_router__WEBPACK_IMPORTED_MODULE_2__["Router"] }
    ]; };
    AppComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
            selector: 'app-root',
            template: tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! raw-loader!./app.component.html */ "./node_modules/raw-loader/dist/cjs.js!./src/app/app.component.html")).default,
            styles: [tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! ./app.component.scss */ "./src/app/app.component.scss")).default]
        })
    ], AppComponent);
    return AppComponent;
}());



/***/ }),

/***/ "./src/app/app.module.ts":
/*!*******************************!*\
  !*** ./src/app/app.module.ts ***!
  \*******************************/
/*! exports provided: AppModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppModule", function() { return AppModule; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/platform-browser */ "./node_modules/@angular/platform-browser/fesm5/platform-browser.js");
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./app.component */ "./src/app/app.component.ts");
/* harmony import */ var _clr_angular__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @clr/angular */ "./node_modules/@clr/angular/fesm5/clr-angular.js");
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/router */ "./node_modules/@angular/router/fesm5/router.js");
/* harmony import */ var _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/platform-browser/animations */ "./node_modules/@angular/platform-browser/fesm5/animations.js");
/* harmony import */ var src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! src/services/projects/projects.service */ "./src/services/projects/projects.service.ts");
/* harmony import */ var _modules_projects_projects_module__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./modules/projects/projects.module */ "./src/app/modules/projects/projects.module.ts");
/* harmony import */ var src_services_analyses_analyses_service__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! src/services/analyses/analyses.service */ "./src/services/analyses/analyses.service.ts");
/* harmony import */ var src_services_attributions_attributions_service__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! src/services/attributions/attributions.service */ "./src/services/attributions/attributions.service.ts");
/* harmony import */ var src_services_dataset_dataset_service__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! src/services/dataset/dataset.service */ "./src/services/dataset/dataset.service.ts");
/* harmony import */ var src_services_colorMaps_color_maps_service__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! src/services/colorMaps/color-maps.service */ "./src/services/colorMaps/color-maps.service.ts");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm5/forms.js");















var AppModule = /** @class */ (function () {
    function AppModule() {
    }
    AppModule = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["NgModule"])({
            declarations: [
                _app_component__WEBPACK_IMPORTED_MODULE_4__["AppComponent"]
            ],
            imports: [
                _angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__["BrowserModule"],
                _angular_forms__WEBPACK_IMPORTED_MODULE_14__["FormsModule"],
                _angular_common_http__WEBPACK_IMPORTED_MODULE_2__["HttpClientModule"],
                _clr_angular__WEBPACK_IMPORTED_MODULE_5__["ClarityModule"],
                _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_7__["BrowserAnimationsModule"],
                _modules_projects_projects_module__WEBPACK_IMPORTED_MODULE_9__["ProjectsModule"],
                _angular_router__WEBPACK_IMPORTED_MODULE_6__["RouterModule"].forRoot([])
            ],
            providers: [
                src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_8__["ProjectsService"],
                src_services_analyses_analyses_service__WEBPACK_IMPORTED_MODULE_10__["AnalysesService"],
                src_services_attributions_attributions_service__WEBPACK_IMPORTED_MODULE_11__["AttributionsService"],
                src_services_dataset_dataset_service__WEBPACK_IMPORTED_MODULE_12__["DatasetService"],
                src_services_colorMaps_color_maps_service__WEBPACK_IMPORTED_MODULE_13__["ColorMapsService"]
            ],
            bootstrap: [_app_component__WEBPACK_IMPORTED_MODULE_4__["AppComponent"]]
        })
    ], AppModule);
    return AppModule;
}());



/***/ }),

/***/ "./src/app/components/before-and-after-slider/before-and-after-slider.component.scss":
/*!*******************************************************************************************!*\
  !*** ./src/app/components/before-and-after-slider/before-and-after-slider.component.scss ***!
  \*******************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("img {\n  width: 100%;\n  vertical-align: middle;\n}\n\n.before-and-after-slider-container, img, .slider-handle {\n  overflow: hidden;\n  -webkit-user-select: none;\n     -moz-user-select: none;\n      -ms-user-select: none;\n          user-select: none;\n}\n\n.before-and-after-slider-container {\n  position: relative;\n}\n\n.before-image {\n  position: absolute;\n  top: 0;\n  left: 0;\n}\n\n.before-image, .after-image {\n  -ms-interpolation-mode: nearest-neighbor;\n      image-rendering: -moz-crisp-edges;\n      image-rendering: pixelated;\n}\n\n.slider-handle {\n  position: absolute;\n  width: 200px;\n  height: 100%;\n  top: 0;\n  left: 0;\n  z-index: 10;\n}\n\n.slider-handle:before, .slider-handle:after {\n  position: absolute;\n  left: 50%;\n  content: \"\";\n  background: white;\n  cursor: -webkit-grab;\n  cursor: grab;\n}\n\n.slider-handle:before {\n  top: 0;\n  transform: translateX(-50%);\n  width: 1px;\n  height: 100%;\n}\n\n.slider-handle:after {\n  top: 50%;\n  transform: translate(-50%, -50%);\n  width: 5px;\n  height: 33%;\n  border-radius: 5px;\n}\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2RuZXVtYW5uL1JlcG9zaXRvcmllcy9zcHJpbmNsL3Zpc3ByX3ZuZXh0L2Zyb250ZW5kL3NyYy9hcHAvY29tcG9uZW50cy9iZWZvcmUtYW5kLWFmdGVyLXNsaWRlci9iZWZvcmUtYW5kLWFmdGVyLXNsaWRlci5jb21wb25lbnQuc2NzcyIsInNyYy9hcHAvY29tcG9uZW50cy9iZWZvcmUtYW5kLWFmdGVyLXNsaWRlci9iZWZvcmUtYW5kLWFmdGVyLXNsaWRlci5jb21wb25lbnQuc2NzcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFDQTtFQUNJLFdBQUE7RUFDQSxzQkFBQTtBQ0FKOztBREdBO0VBQ0ksZ0JBQUE7RUFDQSx5QkFBQTtLQUFBLHNCQUFBO01BQUEscUJBQUE7VUFBQSxpQkFBQTtBQ0FKOztBREdBO0VBQ0ksa0JBQUE7QUNBSjs7QURHQTtFQUNJLGtCQUFBO0VBQ0EsTUFBQTtFQUNBLE9BQUE7QUNBSjs7QURHQTtFQUNJLHdDQUFBO01BQUEsaUNBQUE7TUFBQSwwQkFBQTtBQ0FKOztBREdBO0VBQ0ksa0JBQUE7RUFDQSxZQUFBO0VBQ0EsWUFBQTtFQUNBLE1BQUE7RUFDQSxPQUFBO0VBQ0EsV0FBQTtBQ0FKOztBREVJO0VBQ0ksa0JBQUE7RUFDQSxTQUFBO0VBQ0EsV0FBQTtFQUNBLGlCQUFBO0VBQ0Esb0JBQUE7RUFBQSxZQUFBO0FDQVI7O0FER0k7RUFDSSxNQUFBO0VBQ0EsMkJBQUE7RUFDQSxVQUFBO0VBQ0EsWUFBQTtBQ0RSOztBRElJO0VBQ0ksUUFBQTtFQUNBLGdDQUFBO0VBQ0EsVUFBQTtFQUNBLFdBQUE7RUFDQSxrQkFBQTtBQ0ZSIiwiZmlsZSI6InNyYy9hcHAvY29tcG9uZW50cy9iZWZvcmUtYW5kLWFmdGVyLXNsaWRlci9iZWZvcmUtYW5kLWFmdGVyLXNsaWRlci5jb21wb25lbnQuc2NzcyIsInNvdXJjZXNDb250ZW50IjpbIlxuaW1nIHtcbiAgICB3aWR0aDogMTAwJTtcbiAgICB2ZXJ0aWNhbC1hbGlnbjogbWlkZGxlO1xufVxuXG4uYmVmb3JlLWFuZC1hZnRlci1zbGlkZXItY29udGFpbmVyLCBpbWcsIC5zbGlkZXItaGFuZGxlIHtcbiAgICBvdmVyZmxvdzogaGlkZGVuO1xuICAgIHVzZXItc2VsZWN0OiBub25lO1xufVxuXG4uYmVmb3JlLWFuZC1hZnRlci1zbGlkZXItY29udGFpbmVyIHtcbiAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG59XG5cbi5iZWZvcmUtaW1hZ2Uge1xuICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICB0b3A6IDA7XG4gICAgbGVmdDogMDtcbn1cblxuLmJlZm9yZS1pbWFnZSwgLmFmdGVyLWltYWdlIHtcbiAgICBpbWFnZS1yZW5kZXJpbmc6IHBpeGVsYXRlZDtcbn1cblxuLnNsaWRlci1oYW5kbGUge1xuICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICB3aWR0aDogMjAwcHg7XG4gICAgaGVpZ2h0OiAxMDAlO1xuICAgIHRvcDogMDtcbiAgICBsZWZ0OiAwO1xuICAgIHotaW5kZXg6IDEwO1xuXG4gICAgJjpiZWZvcmUsICY6YWZ0ZXIge1xuICAgICAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gICAgICAgIGxlZnQ6IDUwJTtcbiAgICAgICAgY29udGVudDogXCJcIjtcbiAgICAgICAgYmFja2dyb3VuZDogd2hpdGU7XG4gICAgICAgIGN1cnNvcjogZ3JhYjtcbiAgICB9XG5cbiAgICAmOmJlZm9yZSB7XG4gICAgICAgIHRvcDogMDtcbiAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVYKC01MCUpO1xuICAgICAgICB3aWR0aDogMXB4O1xuICAgICAgICBoZWlnaHQ6IDEwMCU7XG4gICAgfVxuXG4gICAgJjphZnRlciB7XG4gICAgICAgIHRvcDogNTAlO1xuICAgICAgICB0cmFuc2Zvcm06IHRyYW5zbGF0ZSgtNTAlLCAtNTAlKTtcbiAgICAgICAgd2lkdGg6IDVweDtcbiAgICAgICAgaGVpZ2h0OiAzMyU7XG4gICAgICAgIGJvcmRlci1yYWRpdXM6IDVweDtcbiAgICB9XG59XG4iLCJpbWcge1xuICB3aWR0aDogMTAwJTtcbiAgdmVydGljYWwtYWxpZ246IG1pZGRsZTtcbn1cblxuLmJlZm9yZS1hbmQtYWZ0ZXItc2xpZGVyLWNvbnRhaW5lciwgaW1nLCAuc2xpZGVyLWhhbmRsZSB7XG4gIG92ZXJmbG93OiBoaWRkZW47XG4gIHVzZXItc2VsZWN0OiBub25lO1xufVxuXG4uYmVmb3JlLWFuZC1hZnRlci1zbGlkZXItY29udGFpbmVyIHtcbiAgcG9zaXRpb246IHJlbGF0aXZlO1xufVxuXG4uYmVmb3JlLWltYWdlIHtcbiAgcG9zaXRpb246IGFic29sdXRlO1xuICB0b3A6IDA7XG4gIGxlZnQ6IDA7XG59XG5cbi5iZWZvcmUtaW1hZ2UsIC5hZnRlci1pbWFnZSB7XG4gIGltYWdlLXJlbmRlcmluZzogcGl4ZWxhdGVkO1xufVxuXG4uc2xpZGVyLWhhbmRsZSB7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgd2lkdGg6IDIwMHB4O1xuICBoZWlnaHQ6IDEwMCU7XG4gIHRvcDogMDtcbiAgbGVmdDogMDtcbiAgei1pbmRleDogMTA7XG59XG4uc2xpZGVyLWhhbmRsZTpiZWZvcmUsIC5zbGlkZXItaGFuZGxlOmFmdGVyIHtcbiAgcG9zaXRpb246IGFic29sdXRlO1xuICBsZWZ0OiA1MCU7XG4gIGNvbnRlbnQ6IFwiXCI7XG4gIGJhY2tncm91bmQ6IHdoaXRlO1xuICBjdXJzb3I6IGdyYWI7XG59XG4uc2xpZGVyLWhhbmRsZTpiZWZvcmUge1xuICB0b3A6IDA7XG4gIHRyYW5zZm9ybTogdHJhbnNsYXRlWCgtNTAlKTtcbiAgd2lkdGg6IDFweDtcbiAgaGVpZ2h0OiAxMDAlO1xufVxuLnNsaWRlci1oYW5kbGU6YWZ0ZXIge1xuICB0b3A6IDUwJTtcbiAgdHJhbnNmb3JtOiB0cmFuc2xhdGUoLTUwJSwgLTUwJSk7XG4gIHdpZHRoOiA1cHg7XG4gIGhlaWdodDogMzMlO1xuICBib3JkZXItcmFkaXVzOiA1cHg7XG59Il19 */");

/***/ }),

/***/ "./src/app/components/before-and-after-slider/before-and-after-slider.component.ts":
/*!*****************************************************************************************!*\
  !*** ./src/app/components/before-and-after-slider/before-and-after-slider.component.ts ***!
  \*****************************************************************************************/
/*! exports provided: BeforeAndAfterSliderComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "BeforeAndAfterSliderComponent", function() { return BeforeAndAfterSliderComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");


/**
 * Represents a slider, which shows a before and after image.
 */
var BeforeAndAfterSliderComponent = /** @class */ (function () {
    function BeforeAndAfterSliderComponent() {
    }
    /**
     * Is invoked when the view of component was properly initialized.
     */
    BeforeAndAfterSliderComponent.prototype.ngAfterViewInit = function () {
        var sliderHandle = this.sliderHandle.nativeElement;
        var beforeImage = this.beforeImage.nativeElement;
        var sliderHandleWidth = sliderHandle.getBoundingClientRect().width;
        var imageWidth = beforeImage.getBoundingClientRect().width;
        sliderHandle.style.left = imageWidth / 2 - sliderHandleWidth / 2 + "px";
        beforeImage.style.clip = "rect(0px, " + imageWidth / 2 + "px, 999px, 0px)";
        var isMouseDown = false;
        var sliderHandlePosition;
        sliderHandle.addEventListener('mousedown', function (event) {
            sliderHandlePosition = event.clientX;
            isMouseDown = true;
        });
        document.addEventListener('mouseup', function (_) { return isMouseDown = false; });
        document.addEventListener('mouseleave', function (_) { return isMouseDown = false; });
        sliderHandle.addEventListener('mousemove', function (event) {
            if (isMouseDown) {
                sliderHandle.style.left = parseInt(sliderHandle.style.left, 10) + (event.clientX - sliderHandlePosition) + "px";
                sliderHandlePosition = event.clientX;
                beforeImage.style.clip = "rect(0px, " + (sliderHandle.getBoundingClientRect().width / 2 + parseInt(sliderHandle.style.left, 10)) + "px, " + sliderHandle.getBoundingClientRect().height + "px, 0px)";
            }
        });
    };
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ViewChild"])('sliderHandle', { static: false })
    ], BeforeAndAfterSliderComponent.prototype, "sliderHandle", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ViewChild"])('beforeImage', { static: false })
    ], BeforeAndAfterSliderComponent.prototype, "beforeImage", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ViewChild"])('afterImage', { static: false })
    ], BeforeAndAfterSliderComponent.prototype, "afterImage", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], BeforeAndAfterSliderComponent.prototype, "beforeImageSource", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], BeforeAndAfterSliderComponent.prototype, "afterImageSource", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], BeforeAndAfterSliderComponent.prototype, "alt", void 0);
    BeforeAndAfterSliderComponent = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
            selector: 'app-before-and-after-slider',
            template: tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! raw-loader!./before-and-after-slider.component.html */ "./node_modules/raw-loader/dist/cjs.js!./src/app/components/before-and-after-slider/before-and-after-slider.component.html")).default,
            styles: [tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! ./before-and-after-slider.component.scss */ "./src/app/components/before-and-after-slider/before-and-after-slider.component.scss")).default]
        })
    ], BeforeAndAfterSliderComponent);
    return BeforeAndAfterSliderComponent;
}());



/***/ }),

/***/ "./src/app/components/components.module.ts":
/*!*************************************************!*\
  !*** ./src/app/components/components.module.ts ***!
  \*************************************************/
/*! exports provided: ComponentsModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ComponentsModule", function() { return ComponentsModule; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm5/forms.js");
/* harmony import */ var _before_and_after_slider_before_and_after_slider_component__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./before-and-after-slider/before-and-after-slider.component */ "./src/app/components/before-and-after-slider/before-and-after-slider.component.ts");
/* harmony import */ var _embedding_visualizer_embedding_visualizer_component__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./embedding-visualizer/embedding-visualizer.component */ "./src/app/components/embedding-visualizer/embedding-visualizer.component.ts");





/**
 * Represents the module for application-wide components.
 */
var ComponentsModule = /** @class */ (function () {
    function ComponentsModule() {
    }
    ComponentsModule = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["NgModule"])({
            declarations: [
                _before_and_after_slider_before_and_after_slider_component__WEBPACK_IMPORTED_MODULE_3__["BeforeAndAfterSliderComponent"],
                _embedding_visualizer_embedding_visualizer_component__WEBPACK_IMPORTED_MODULE_4__["EmbeddingVisualizerComponent"]
            ],
            imports: [
                _angular_forms__WEBPACK_IMPORTED_MODULE_2__["FormsModule"]
            ],
            exports: [
                _before_and_after_slider_before_and_after_slider_component__WEBPACK_IMPORTED_MODULE_3__["BeforeAndAfterSliderComponent"],
                _embedding_visualizer_embedding_visualizer_component__WEBPACK_IMPORTED_MODULE_4__["EmbeddingVisualizerComponent"]
            ]
        })
    ], ComponentsModule);
    return ComponentsModule;
}());



/***/ }),

/***/ "./src/app/components/embedding-visualizer/embedding-visualizer.component.scss":
/*!*************************************************************************************!*\
  !*** ./src/app/components/embedding-visualizer/embedding-visualizer.component.scss ***!
  \*************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = (":host {\n  display: block !important;\n  position: relative;\n  width: 100%;\n  height: 100%;\n}\n\ncanvas {\n  width: 100%;\n  height: 100%;\n}\n\n.container {\n  display: block;\n  position: relative;\n  overflow: hidden;\n  width: 100%;\n  height: 100%;\n}\n\n.selection-box {\n  display: none;\n  position: absolute;\n  pointer-events: none;\n  border: 1px solid #55aaff;\n  background-color: rgba(75, 160, 255, 0.3);\n}\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2RuZXVtYW5uL1JlcG9zaXRvcmllcy9zcHJpbmNsL3Zpc3ByX3ZuZXh0L2Zyb250ZW5kL3NyYy9hcHAvY29tcG9uZW50cy9lbWJlZGRpbmctdmlzdWFsaXplci9lbWJlZGRpbmctdmlzdWFsaXplci5jb21wb25lbnQuc2NzcyIsInNyYy9hcHAvY29tcG9uZW50cy9lbWJlZGRpbmctdmlzdWFsaXplci9lbWJlZGRpbmctdmlzdWFsaXplci5jb21wb25lbnQuc2NzcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFDQTtFQUNJLHlCQUFBO0VBQ0Esa0JBQUE7RUFDQSxXQUFBO0VBQ0EsWUFBQTtBQ0FKOztBREdBO0VBQ0ksV0FBQTtFQUNBLFlBQUE7QUNBSjs7QURHQTtFQUNJLGNBQUE7RUFDQSxrQkFBQTtFQUNBLGdCQUFBO0VBQ0EsV0FBQTtFQUNBLFlBQUE7QUNBSjs7QURHQTtFQUNJLGFBQUE7RUFDQSxrQkFBQTtFQUNBLG9CQUFBO0VBQ0EseUJBQUE7RUFDQSx5Q0FBQTtBQ0FKIiwiZmlsZSI6InNyYy9hcHAvY29tcG9uZW50cy9lbWJlZGRpbmctdmlzdWFsaXplci9lbWJlZGRpbmctdmlzdWFsaXplci5jb21wb25lbnQuc2NzcyIsInNvdXJjZXNDb250ZW50IjpbIlxuOmhvc3Qge1xuICAgIGRpc3BsYXk6IGJsb2NrICFpbXBvcnRhbnQ7XG4gICAgcG9zaXRpb246IHJlbGF0aXZlO1xuICAgIHdpZHRoOiAxMDAlO1xuICAgIGhlaWdodDogMTAwJTtcbn1cblxuY2FudmFzIHtcbiAgICB3aWR0aDogMTAwJTtcbiAgICBoZWlnaHQ6IDEwMCU7XG59XG5cbi5jb250YWluZXIge1xuICAgIGRpc3BsYXk6IGJsb2NrO1xuICAgIHBvc2l0aW9uOiByZWxhdGl2ZTtcbiAgICBvdmVyZmxvdzogaGlkZGVuO1xuICAgIHdpZHRoOiAxMDAlO1xuICAgIGhlaWdodDogMTAwJTtcbn1cblxuLnNlbGVjdGlvbi1ib3ggIHtcbiAgICBkaXNwbGF5OiBub25lO1xuICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICBwb2ludGVyLWV2ZW50czogbm9uZTtcbiAgICBib3JkZXI6IDFweCBzb2xpZCAjNTVhYWZmO1xuICAgIGJhY2tncm91bmQtY29sb3I6IHJnYmEoNzUsIDE2MCwgMjU1LCAwLjMpO1xufVxuIiwiOmhvc3Qge1xuICBkaXNwbGF5OiBibG9jayAhaW1wb3J0YW50O1xuICBwb3NpdGlvbjogcmVsYXRpdmU7XG4gIHdpZHRoOiAxMDAlO1xuICBoZWlnaHQ6IDEwMCU7XG59XG5cbmNhbnZhcyB7XG4gIHdpZHRoOiAxMDAlO1xuICBoZWlnaHQ6IDEwMCU7XG59XG5cbi5jb250YWluZXIge1xuICBkaXNwbGF5OiBibG9jaztcbiAgcG9zaXRpb246IHJlbGF0aXZlO1xuICBvdmVyZmxvdzogaGlkZGVuO1xuICB3aWR0aDogMTAwJTtcbiAgaGVpZ2h0OiAxMDAlO1xufVxuXG4uc2VsZWN0aW9uLWJveCB7XG4gIGRpc3BsYXk6IG5vbmU7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgcG9pbnRlci1ldmVudHM6IG5vbmU7XG4gIGJvcmRlcjogMXB4IHNvbGlkICM1NWFhZmY7XG4gIGJhY2tncm91bmQtY29sb3I6IHJnYmEoNzUsIDE2MCwgMjU1LCAwLjMpO1xufSJdfQ== */");

/***/ }),

/***/ "./src/app/components/embedding-visualizer/embedding-visualizer.component.ts":
/*!***********************************************************************************!*\
  !*** ./src/app/components/embedding-visualizer/embedding-visualizer.component.ts ***!
  \***********************************************************************************/
/*! exports provided: HoverEvent, EmbeddingVisualizerComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "HoverEvent", function() { return HoverEvent; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "EmbeddingVisualizerComponent", function() { return EmbeddingVisualizerComponent; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm5/forms.js");
/* harmony import */ var three__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! three */ "./node_modules/three/build/three.module.js");
/* harmony import */ var three_orbitcontrols__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! three-orbitcontrols */ "./node_modules/three-orbitcontrols/OrbitControls.js");
/* harmony import */ var three_orbitcontrols__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(three_orbitcontrols__WEBPACK_IMPORTED_MODULE_4__);





/**
 * Represents a hover event.
 */
var HoverEvent = /** @class */ (function () {
    /**
     * Initializes a new HoverEvent instance.
     * @param dataPoint The data point that the user is hovering.
     * @param clusterColor The color that was assigned to the cluster of the data point.
     */
    function HoverEvent(dataPoint, clusterColor) {
        this.dataPoint = dataPoint;
        this.clusterColor = clusterColor.getStyle();
    }
    return HoverEvent;
}());

/**
 * Represents a visualizer, which can render an embedding.
 */
var EmbeddingVisualizerComponent = /** @class */ (function () {
    /**
     * Initializes a new EmbeddingVisualizerComponent instance.
     * @param ngZone The Angular zone, which is needed to execute some code outside of Angular.
     */
    function EmbeddingVisualizerComponent(ngZone) {
        var _this = this;
        this.ngZone = ngZone;
        /**
         * Contains the index of the data point that is currently being hovered by the user.
         */
        this.indexOfDataPointCurrentBeingHovered = null;
        /**
         * Contains the first dimension of the embedding that is being visualized. Only two dimensions can be displayed at a
         * time, if the embedding is multi-dimensional, then this is the dimension that is displayed on the x-axis.
         */
        this._firstDimension = 0;
        /**
         * Contains the second dimension of the embedding that is being visualized. Only two dimensions can be displayed at
         * a time, if the embedding is multi-dimensional, then this is the dimension that is displayed on the y-axis.
         */
        this._secondDimension = 1;
        /**
         * The event that is invoked when the user hovers a data point.
         */
        this.onHover = new _angular_core__WEBPACK_IMPORTED_MODULE_1__["EventEmitter"]();
        /**
         * The event that is invoked, when the user moves the mouse away from a data point.
         */
        this.onUnhover = new _angular_core__WEBPACK_IMPORTED_MODULE_1__["EventEmitter"]();
        /**
         * Is invoked when the selected data points change.
         */
        this.onSelectedDataPointsChange = function (_) { };
        /**
         * Is invoked when the selected data points were "touched" (which in this case is nothing more then changed).
         */
        this.onSelectedDataPointsTouched = function () { };
        /**
         * Is invoked, when the user clicks a mouse button. When the left mouse button is clicked, then selection process is
         * started.
         * @param event The event arguments that contain information about the event such as the button that was clicked.
         */
        this.onMouseDown = function (event) {
            // Only when the left mouse button was clicked, the selection is started, otherwise nothing needs to be done
            if (event.buttons !== 1) {
                return;
            }
            // Starts the selection
            _this.isSelecting = true;
            // Since the selection box is positioned absolutely, the left and top of the render target need to be subtracted
            // from the mouse position
            var renderTargetNativeElement = _this.renderTarget.nativeElement;
            var boundingRectangle = renderTargetNativeElement.getBoundingClientRect();
            // Shows the selection box
            _this.selectionBoxRectangle = {
                x: event.clientX - boundingRectangle.left,
                y: event.clientY - boundingRectangle.top,
                startX: event.clientX - boundingRectangle.left,
                startY: event.clientY - boundingRectangle.top
            };
            _this.updateSelectionBox();
        };
        /**
         * Is invoked, when the user moves the mouse over the window. This is used for making selections.
         */
        this.onMouseMoveWindow = function (event) {
            // When the user is performing a selection, then the selection box must be updated
            if (_this.isSelecting) {
                // Since the selection box is positioned absolutely, the left and top of the render target need to be subtracted
                // from the mouse position
                var renderTargetNativeElement = _this.renderTarget.nativeElement;
                var boundingRectangle = renderTargetNativeElement.getBoundingClientRect();
                // Updates the selection box
                _this.selectionBoxRectangle.x = event.clientX - boundingRectangle.left;
                _this.selectionBoxRectangle.y = event.clientY - boundingRectangle.top;
                _this.updateSelectionBox();
            }
        };
        /**
         * Is invoked, when the user releases a mouse button. Stops the selection process.
         */
        this.onMouseUp = function () {
            // If the user wasn't selecting, then nothing needs to be done
            if (!_this.isSelecting) {
                return;
            }
            // Stops the selection
            _this.isSelecting = false;
            _this.selectionBoxRectangle = null;
            _this.updateSelectionBox();
            // Gets the data points that have been selected and writes them
            var selectedDataPoints = _this.embedding.filter(function (_, index) { return _this.selectedDataPointIndices.indexOf(index) !== -1; });
            _this.writeValue(selectedDataPoints);
        };
        /**
         * Is invoked, when the user moves the mouse over the render target. This is used to detect the data point the user
         * is hovering over.
         * @param event The event arguments that contain information about the event such as mouse position.
         */
        this.onMouseMoveRenderTarget = function (event) {
            // If the component has not been initialized or no embedding has been specified, there is nothing that the user
            // can hover over
            if (!_this.isInitialized || !_this.embedding) {
                return;
            }
            // When the user is simultaneously using any mouse buttons, then the hover events are not emitted
            if (event.buttons !== 0) {
                if (_this.indexOfDataPointCurrentBeingHovered != null) {
                    _this.onUnhover.emit();
                }
                _this.indexOfDataPointCurrentBeingHovered = null;
                return;
            }
            // Gets a reference to the render target
            var renderTargetNativeElement = _this.renderTarget.nativeElement;
            // Determines the size of the render target
            var width = renderTargetNativeElement.clientWidth;
            var height = renderTargetNativeElement.clientHeight;
            // Determines the position of the mouse in camera space
            var boundingRectangle = event.target.getBoundingClientRect();
            var mouseX = ((event.clientX - boundingRectangle.left) / width) * 2 - 1;
            var mouseY = -((event.clientY - boundingRectangle.top) / height) * 2 + 1;
            var mouseVector = new three__WEBPACK_IMPORTED_MODULE_3__["Vector3"](mouseX, mouseY, 0);
            // Casts a ray from the camera through the mouse and checks if any of the data points intersect with the ray
            var rayCaster = new three__WEBPACK_IMPORTED_MODULE_3__["Raycaster"]();
            rayCaster.params.Points.threshold = 5 / _this.camera.zoom;
            rayCaster.setFromCamera(mouseVector, _this.camera);
            var intersections = rayCaster.intersectObject(_this.embeddingObject);
            if (intersections.length > 0) {
                if (_this.indexOfDataPointCurrentBeingHovered !== intersections[0].index) {
                    var dataPoint = _this.embedding[intersections[0].index];
                    var clusterColor = _this.embeddingObject.geometry.colors[intersections[0].index];
                    _this.indexOfDataPointCurrentBeingHovered = intersections[0].index;
                    _this.onHover.emit(new HoverEvent(dataPoint, clusterColor));
                }
            }
            else {
                if (_this.indexOfDataPointCurrentBeingHovered != null) {
                    _this.onUnhover.emit();
                }
                _this.indexOfDataPointCurrentBeingHovered = null;
            }
        };
        /**
         * Renders the scene.
         */
        this.render = function () {
            requestAnimationFrame(_this.render);
            _this.renderer.render(_this.scene, _this.camera);
        };
    }
    EmbeddingVisualizerComponent_1 = EmbeddingVisualizerComponent;
    Object.defineProperty(EmbeddingVisualizerComponent.prototype, "embedding", {
        /**
         * Gets the embedding that is displayed in the visualizer.
         */
        get: function () {
            return this._embedding;
        },
        /**
         * Sets the embedding that is displayed in the visualizer.
         */
        set: function (value) {
            var e_1, _a;
            // Stores the new value
            this._embedding = value;
            // Determines the total number of clusters, which is needed to determine the number of colors that are needed
            // for the visualization
            if (this.embedding) {
                var clusters = new Array();
                try {
                    for (var _b = tslib__WEBPACK_IMPORTED_MODULE_0__["__values"](this.embedding.map(function (dataPoint) { return dataPoint.cluster; })), _c = _b.next(); !_c.done; _c = _b.next()) {
                        var cluster = _c.value;
                        if (clusters.indexOf(cluster) === -1) {
                            clusters.push(cluster);
                        }
                    }
                }
                catch (e_1_1) { e_1 = { error: e_1_1 }; }
                finally {
                    try {
                        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
                    }
                    finally { if (e_1) throw e_1.error; }
                }
                this.numberOfClusters = clusters.length;
            }
            // Updates the visualizer with the new data points
            this.updateVisualizer();
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(EmbeddingVisualizerComponent.prototype, "firstDimension", {
        /**
         * Gets the first dimension of the embedding that is being visualized.
         */
        get: function () {
            return this._firstDimension;
        },
        /**
         * Sets the first dimension of the embedding that is being visualized.
         */
        set: function (value) {
            this._firstDimension = value;
            this.updateVisualizer();
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(EmbeddingVisualizerComponent.prototype, "secondDimension", {
        /**
         * Gets the second dimension of the embedding that is being visualized.
         */
        get: function () {
            return this._secondDimension;
        },
        /**
         * Sets the second dimension of the embedding that is being visualized.
         */
        set: function (value) {
            this._secondDimension = value;
            this.updateVisualizer();
        },
        enumerable: true,
        configurable: true
    });
    /**
     * Is invoked when the window was resized. Updates the camera and the renderer to the new canvas size.
     */
    EmbeddingVisualizerComponent.prototype.onWindowResize = function () {
        // Gets a reference to the canvas that has probably also been resized due to the window resize
        var renderTargetNativeElement = this.renderTarget.nativeElement;
        // Determines the size of the render target (in this case the parent element is used, because the canvas itself
        // gets a fixed size from the renderer and therefore never resizes unless the renderer is updated)
        var width = renderTargetNativeElement.parentElement.clientWidth;
        var height = renderTargetNativeElement.parentElement.clientHeight;
        // Updates the camera and the renderer to the size
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        // Updates the renderer
        this.renderer.setSize(width, height);
    };
    /**
     * Updates the position of the selection box.
     */
    EmbeddingVisualizerComponent.prototype.updateSelectionBox = function () {
        // If nothing is currently selected, then the selection box is hidden, otherwise it is shown
        var selectionBoxNativeElement = this.selectionBox.nativeElement;
        if (!this.isSelecting) {
            selectionBoxNativeElement.style.display = 'none';
            return;
        }
        selectionBoxNativeElement.style.display = 'block';
        // Updates the selection box
        var left = Math.min(this.selectionBoxRectangle.x, this.selectionBoxRectangle.startX);
        var top = Math.min(this.selectionBoxRectangle.y, this.selectionBoxRectangle.startY);
        var width = Math.abs(this.selectionBoxRectangle.x - this.selectionBoxRectangle.startX);
        var height = Math.abs(this.selectionBoxRectangle.y - this.selectionBoxRectangle.startY);
        selectionBoxNativeElement.style.left = left + "px";
        selectionBoxNativeElement.style.top = top + "px";
        selectionBoxNativeElement.style.width = width + "px";
        selectionBoxNativeElement.style.height = height + "px";
        // Determines the size of the render target
        var renderTargetNativeElement = this.renderTarget.nativeElement;
        var renderTargetWidth = renderTargetNativeElement.clientWidth;
        var renderTargetHeight = renderTargetNativeElement.clientHeight;
        // Determines the positions of the corners of the selection box in camera space
        var right = (Math.max(this.selectionBoxRectangle.x, this.selectionBoxRectangle.startX) / renderTargetWidth) * 2 - 1;
        var bottom = -(Math.max(this.selectionBoxRectangle.y, this.selectionBoxRectangle.startY) / renderTargetHeight) * 2 + 1;
        var topLeftVector = new three__WEBPACK_IMPORTED_MODULE_3__["Vector3"]((left / renderTargetWidth) * 2 - 1, -(top / renderTargetHeight) * 2 + 1, 0);
        var bottomRightVector = new three__WEBPACK_IMPORTED_MODULE_3__["Vector3"](right, bottom, 0);
        // Brings the vertices of the corners of the selection box into the world space
        topLeftVector.unproject(this.camera);
        bottomRightVector.unproject(this.camera);
        // Determines which embedding objects are inside the selection box
        this.selectedDataPointIndices = new Array();
        for (var index = 0; index < this.embedding.length; index++) {
            var vector = this.embeddingObject.geometry.vertices[index];
            if (vector.x > topLeftVector.x && vector.x < bottomRightVector.x && vector.y < topLeftVector.y && vector.y > bottomRightVector.y) {
                this.selectedDataPointIndices.push(index);
            }
        }
        // Increases the saturation of the data points that are selected and decreases the saturation of the rest
        for (var index = 0; index < this.embedding.length; index++) {
            var dataPoint = this.embedding[index];
            if (this.selectedDataPointIndices.indexOf(index) === -1) {
                this.embeddingObject.geometry.colors[index] = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.25, 0.5);
            }
            else {
                this.embeddingObject.geometry.colors[index] = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 1, 0.5);
            }
        }
        this.embeddingObject.geometry.colorsNeedUpdate = true;
    };
    /**
     * Updates the visualization of the embedding.
     */
    EmbeddingVisualizerComponent.prototype.updateVisualizer = function () {
        var e_2, _a;
        // If the component has not been initialized or no embedding has been specified, then the visualizer cannot be
        // updated
        if (!this.isInitialized || !this.embedding) {
            return;
        }
        // If there is an embedding that is currently being visualized, then the object is remove from the scene
        if (this.embeddingObject) {
            this.scene.remove(this.embeddingObject);
        }
        // Gets a reference to the render target
        var renderTargetNativeElement = this.renderTarget.nativeElement;
        // Determines the size of the render target
        var width = renderTargetNativeElement.clientWidth * 0.95 / 2;
        var height = renderTargetNativeElement.clientHeight * 0.95 / 2;
        // Creates the scene object for the data points
        var maximumX = 0;
        var maximumY = 0;
        var pointsGeometry = new three__WEBPACK_IMPORTED_MODULE_3__["Geometry"]();
        try {
            for (var _b = tslib__WEBPACK_IMPORTED_MODULE_0__["__values"](this.embedding), _c = _b.next(); !_c.done; _c = _b.next()) {
                var dataPoint = _c.value;
                // Determines X and Y positions of the points that are the farthest away from the origin, this information
                // is used to scale the data points so that they fill out the whole viewport
                if (Math.abs(dataPoint.value[this.firstDimension]) > maximumX) {
                    maximumX = Math.abs(dataPoint.value[this.firstDimension]);
                }
                if (Math.abs(dataPoint.value[this.secondDimension]) > maximumY) {
                    maximumY = Math.abs(dataPoint.value[this.secondDimension]);
                }
                // Creates a new vertex for the data point
                var vertex = new three__WEBPACK_IMPORTED_MODULE_3__["Vector3"](dataPoint.value[this.firstDimension], dataPoint.value[this.secondDimension], -1);
                pointsGeometry.vertices.push(vertex);
                // Generates a color for the data point based on its cluster
                var color = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.75, 0.5);
                pointsGeometry.colors.push(color);
            }
        }
        catch (e_2_1) { e_2 = { error: e_2_1 }; }
        finally {
            try {
                if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
            }
            finally { if (e_2) throw e_2.error; }
        }
        // Scales all data points so that they fill out the whole viewport
        pointsGeometry.scale(width / maximumX, height / maximumY, 1);
        // Creates the material for the points (setting the size attenuation to false means that the points always have
        // the same size no matter the zoom level)
        var pointsMaterial = new three__WEBPACK_IMPORTED_MODULE_3__["PointsMaterial"]({
            size: 8,
            sizeAttenuation: false,
            vertexColors: three__WEBPACK_IMPORTED_MODULE_3__["VertexColors"],
            map: this.dataPointTexture,
            transparent: true,
            depthTest: false
        });
        // Generates the scene object that contains all the data points and adds it to the scene
        this.embeddingObject = new three__WEBPACK_IMPORTED_MODULE_3__["Points"](pointsGeometry, pointsMaterial);
        this.scene.add(this.embeddingObject);
        // Resets the camera
        this.cameraController.reset();
    };
    /**
     * Is invoked after the view was initialized (and the view children are available). Initializes the renderer.
     */
    EmbeddingVisualizerComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        // Gets a reference to the canvas onto which the embedding will be rendered
        var renderTargetNativeElement = this.renderTarget.nativeElement;
        // Determines the size of the render target
        var width = renderTargetNativeElement.clientWidth;
        var height = renderTargetNativeElement.clientHeight;
        // Creates the renderer
        this.renderer = new three__WEBPACK_IMPORTED_MODULE_3__["WebGLRenderer"]({
            canvas: renderTargetNativeElement,
            antialias: true
        });
        this.renderer.setSize(width, height);
        var backgroundColor = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setStyle(this.backgroundColor || '#FFFFFF');
        this.renderer.setClearColor(backgroundColor);
        // Creates the scene
        this.scene = new three__WEBPACK_IMPORTED_MODULE_3__["Scene"]();
        // Creates the camera
        this.camera = new three__WEBPACK_IMPORTED_MODULE_3__["OrthographicCamera"](width / -2, width / 2, height / 2, height / -2, -10, 1000);
        this.camera.position.set(0, 0, 1);
        this.scene.add(this.camera);
        // Adds a camera controller for zooming and panning
        this.cameraController = new three_orbitcontrols__WEBPACK_IMPORTED_MODULE_4__(this.camera, renderTargetNativeElement);
        this.cameraController.minZoom = 0.5;
        this.cameraController.maxZoom = 5.0;
        this.cameraController.screenSpacePanning = true;
        this.cameraController.enableRotate = false;
        // Loads the texture that is used to display the data points
        this.dataPointTexture = new three__WEBPACK_IMPORTED_MODULE_3__["TextureLoader"]().load('assets/images/circle-sprite.png');
        // This should be run outside angular zones, because it could trigger heavy change detection cycles
        this.ngZone.runOutsideAngular(function () {
            // Subscribes to the window resize event, in which case the camera and the renderer have to be updated
            window.addEventListener('resize', function () { return _this.onWindowResize(); });
            // Starts the rendering
            _this.render();
        });
        // Subscribes to the mouse move event of the canvas, which is used to raise the hover events
        renderTargetNativeElement.addEventListener('mousemove', this.onMouseMoveRenderTarget);
        // Subscribes to the mouse events, which are used for making a selection
        renderTargetNativeElement.addEventListener('mousedown', this.onMouseDown);
        window.addEventListener('mousemove', this.onMouseMoveWindow);
        window.addEventListener('mouseup', this.onMouseUp);
        // The initialization has finished
        this.isInitialized = true;
        this.updateVisualizer();
    };
    /**
     * Is invoked when the component is being destroyed. Aborts the animation.
     */
    EmbeddingVisualizerComponent.prototype.ngOnDestroy = function () {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    };
    /**
     * Changes the selected data points.
     * @param value The new selected data points.
     */
    EmbeddingVisualizerComponent.prototype.writeValue = function (value) {
        // Stores the selected data points
        this.selectedDataPoints = value ? value : new Array();
        // Checks if the user selected data points or deselected everything, if the user selected data points, then the
        // saturation of the selected data points is increased and the saturation of the data points that are not
        // selected is decreased, if the user deselected everything, then the saturation of the data points is reset
        if (this.embeddingObject) {
            if (this.selectedDataPoints.length !== 0) {
                for (var index = 0; index < this.embedding.length; index++) {
                    var dataPoint = this.embedding[index];
                    if (this.selectedDataPoints.indexOf(dataPoint) === -1) {
                        this.embeddingObject.geometry.colors[index] = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.25, 0.5);
                    }
                    else {
                        this.embeddingObject.geometry.colors[index] = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 1, 0.5);
                    }
                }
            }
            else {
                for (var index = 0; index < this.embedding.length; index++) {
                    var dataPoint = this.embedding[index];
                    this.embeddingObject.geometry.colors[index] = new three__WEBPACK_IMPORTED_MODULE_3__["Color"]().setHSL((360 / this.numberOfClusters * dataPoint.cluster) / 360, 0.5, 0.5);
                }
            }
            this.embeddingObject.geometry.colorsNeedUpdate = true;
        }
        // Propagates the change
        this.onSelectedDataPointsChange(this.selectedDataPoints);
        this.onSelectedDataPointsTouched();
    };
    /**
     * Registers a callback, which is invoked, when the selected data points change.
     * @param callback The callback that is invoked, when the selected data points change.
     */
    EmbeddingVisualizerComponent.prototype.registerOnChange = function (callback) {
        this.onSelectedDataPointsChange = callback;
    };
    /**
     * Registers a callback, which is invoked, when the selected data points were touched.
     * @param callback The callback that is invoked, when the selected data points were touched.
     */
    EmbeddingVisualizerComponent.prototype.registerOnTouched = function (callback) {
        this.onSelectedDataPointsTouched = callback;
    };
    /**
     * Sets whether the visualizer is enabled or disabled.
     * @param isDisabled Determines whether the visualizer is disabled.
     */
    EmbeddingVisualizerComponent.prototype.setDisabledState = function (isDisabled) {
        this.disabled = isDisabled;
    };
    var EmbeddingVisualizerComponent_1;
    EmbeddingVisualizerComponent.ctorParameters = function () { return [
        { type: _angular_core__WEBPACK_IMPORTED_MODULE_1__["NgZone"] }
    ]; };
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ViewChild"])('renderTarget', { static: false })
    ], EmbeddingVisualizerComponent.prototype, "renderTarget", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ViewChild"])('selectionBox', { static: false })
    ], EmbeddingVisualizerComponent.prototype, "selectionBox", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], EmbeddingVisualizerComponent.prototype, "disabled", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], EmbeddingVisualizerComponent.prototype, "embedding", null);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], EmbeddingVisualizerComponent.prototype, "firstDimension", null);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], EmbeddingVisualizerComponent.prototype, "secondDimension", null);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Input"])()
    ], EmbeddingVisualizerComponent.prototype, "backgroundColor", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Output"])()
    ], EmbeddingVisualizerComponent.prototype, "onHover", void 0);
    tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Output"])()
    ], EmbeddingVisualizerComponent.prototype, "onUnhover", void 0);
    EmbeddingVisualizerComponent = EmbeddingVisualizerComponent_1 = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
            selector: 'app-embedding-visualizer',
            template: tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! raw-loader!./embedding-visualizer.component.html */ "./node_modules/raw-loader/dist/cjs.js!./src/app/components/embedding-visualizer/embedding-visualizer.component.html")).default,
            providers: [{
                    provide: _angular_forms__WEBPACK_IMPORTED_MODULE_2__["NG_VALUE_ACCESSOR"],
                    useExisting: Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["forwardRef"])(function () { return EmbeddingVisualizerComponent_1; }),
                    multi: true
                }],
            styles: [tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! ./embedding-visualizer.component.scss */ "./src/app/components/embedding-visualizer/embedding-visualizer.component.scss")).default]
        })
    ], EmbeddingVisualizerComponent);
    return EmbeddingVisualizerComponent;
}());



/***/ }),

/***/ "./src/app/modules/projects/pages/index/index.page.scss":
/*!**************************************************************!*\
  !*** ./src/app/modules/projects/pages/index/index.page.scss ***!
  \**************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony default export */ __webpack_exports__["default"] = ("#panels-container {\n  display: grid;\n  grid-template-rows: 85px 1fr 250px 35px;\n  grid-template-columns: 1fr 250px;\n  grid-template-areas: \"options-pane options-pane\" \"embedding-plot cluster-pane\" \"selected-attributions selected-attributions\" \"status-bar status-bar\";\n}\n#panels-container #cluster-pane {\n  grid-area: cluster-pane;\n  background-color: #EFEFEF;\n  height: calc(100vh - 430px);\n  overflow-x: hidden;\n  overflow-y: auto;\n}\n#panels-container #cluster-pane .cluster-selection-buttons-container {\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n}\n#panels-container #cluster-pane .cluster-selection-buttons-container button {\n  margin-right: 0;\n  width: 200px;\n}\n#panels-container #embedding-plot {\n  grid-area: embedding-plot;\n  width: calc(100vw - 250px);\n  height: calc(100vh - 430px);\n  background-color: #EFEFEF;\n}\n#panels-container #embedding-plot #attribution-hover-preview {\n  position: absolute;\n  top: 169px;\n  left: 24px;\n  min-width: 128px;\n  min-height: 128px;\n  max-width: 256px;\n  max-height: 256px;\n  z-index: 9999;\n  -ms-interpolation-mode: nearest-neighbor;\n      image-rendering: -moz-crisp-edges;\n      image-rendering: pixelated;\n}\n#panels-container #options-pane {\n  grid-area: options-pane;\n  display: flex;\n  align-items: center;\n  background-color: #EFEFEF;\n  margin: 0;\n  z-index: 1;\n  overflow-x: auto;\n  overflow-y: hidden;\n}\n#panels-container #options-pane clr-select-container, #panels-container #options-pane img {\n  margin: 0 0 0 24px;\n}\n#panels-container #options-pane img {\n  padding-right: 24px;\n  width: 174px;\n  height: 40px;\n}\n#panels-container #selected-attributions {\n  grid-area: selected-attributions;\n  height: 100%;\n  width: 100%;\n  background-color: #EFEFEF;\n  overflow-x: auto;\n  overflow-y: hidden;\n  white-space: nowrap;\n}\n#panels-container #selected-attributions .spinner-locally-centered {\n  position: relative;\n  top: calc(50% - 1.5rem);\n  left: calc(50% - 1.5rem);\n}\n#panels-container #selected-attributions #selection-hint {\n  display: table;\n  height: calc(100% - 24px);\n  width: calc(100% - 24px);\n  margin: 12px 12px 12px 12px;\n  border: 1px dashed silver;\n  border-radius: 5px;\n  text-align: center;\n}\n#panels-container #selected-attributions #selection-hint p {\n  vertical-align: middle;\n  display: table-cell;\n}\n#panels-container #selected-attributions #selected-attribution-list {\n  display: flex;\n  align-items: center;\n  height: 226px;\n  margin: 12px;\n}\n#panels-container #selected-attributions #selected-attribution-list .selected-attribution {\n  min-width: 180px;\n  min-height: 210px;\n  max-width: 180px;\n  max-height: 210px;\n  margin-left: 12px;\n}\n#panels-container #selected-attributions #selected-attribution-list .selected-attribution:first-child {\n  margin-left: 0;\n}\n#panels-container #selected-attributions #selected-attribution-list .selected-attribution:last-child {\n  margin-right: 12px;\n}\n#panels-container #selected-attributions #selected-attribution-list p {\n  margin-top: 6px;\n  text-align: center;\n}\n#panels-container #status-bar {\n  grid-area: status-bar;\n  display: flex;\n  align-items: center;\n  padding-left: 1rem;\n  z-index: 1;\n  background-color: #271335;\n  color: white;\n}\n#panels-container #status-bar strong {\n  margin-left: 5px;\n  margin-right: 5px;\n}\n#panels-container #status-bar clr-icon:not(:first-child) {\n  margin-left: 20px;\n}\n/*# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2RuZXVtYW5uL1JlcG9zaXRvcmllcy9zcHJpbmNsL3Zpc3ByX3ZuZXh0L2Zyb250ZW5kL3NyYy9hcHAvbW9kdWxlcy9wcm9qZWN0cy9wYWdlcy9pbmRleC9pbmRleC5wYWdlLnNjc3MiLCJzcmMvYXBwL21vZHVsZXMvcHJvamVjdHMvcGFnZXMvaW5kZXgvaW5kZXgucGFnZS5zY3NzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUNBO0VBQ0ksYUFBQTtFQUNBLHVDQUFBO0VBQ0EsZ0NBQUE7RUFDQSxvSkFDSTtBQ0RSO0FET0k7RUFDSSx1QkFBQTtFQUVBLHlCQUFBO0VBRUEsMkJBQUE7RUFDQSxrQkFBQTtFQUNBLGdCQUFBO0FDUFI7QURTUTtFQU9JLGFBQUE7RUFDQSxzQkFBQTtFQUNBLG1CQUFBO0FDYlo7QURNWTtFQUNJLGVBQUE7RUFDQSxZQUFBO0FDSmhCO0FEYUk7RUFDSSx5QkFBQTtFQUNBLDBCQUFBO0VBQ0EsMkJBQUE7RUFFQSx5QkFBQTtBQ1pSO0FEY1E7RUFDSSxrQkFBQTtFQUVBLFVBQUE7RUFDQSxVQUFBO0VBQ0EsZ0JBQUE7RUFDQSxpQkFBQTtFQUNBLGdCQUFBO0VBQ0EsaUJBQUE7RUFFQSxhQUFBO0VBRUEsd0NBQUE7TUFBQSxpQ0FBQTtNQUFBLDBCQUFBO0FDZlo7QURtQkk7RUFDSSx1QkFBQTtFQUVBLGFBQUE7RUFDQSxtQkFBQTtFQUVBLHlCQUFBO0VBQ0EsU0FBQTtFQUNBLFVBQUE7RUFFQSxnQkFBQTtFQUNBLGtCQUFBO0FDcEJSO0FEc0JRO0VBQ0ksa0JBQUE7QUNwQlo7QUR1QlE7RUFDSSxtQkFBQTtFQUNBLFlBQUE7RUFDQSxZQUFBO0FDckJaO0FEeUJJO0VBQ0ksZ0NBQUE7RUFDQSxZQUFBO0VBQ0EsV0FBQTtFQUVBLHlCQUFBO0VBRUEsZ0JBQUE7RUFDQSxrQkFBQTtFQUNBLG1CQUFBO0FDekJSO0FEMkJRO0VBQ0ksa0JBQUE7RUFDQSx1QkFBQTtFQUNBLHdCQUFBO0FDekJaO0FENEJRO0VBQ0ksY0FBQTtFQUVBLHlCQUFBO0VBQ0Esd0JBQUE7RUFDQSwyQkFBQTtFQUVBLHlCQUFBO0VBQ0Esa0JBQUE7RUFFQSxrQkFBQTtBQzdCWjtBRCtCWTtFQUNJLHNCQUFBO0VBQ0EsbUJBQUE7QUM3QmhCO0FEaUNRO0VBQ0ksYUFBQTtFQUNBLG1CQUFBO0VBRUEsYUFBQTtFQUNBLFlBQUE7QUNoQ1o7QURrQ1k7RUFDSSxnQkFBQTtFQUNBLGlCQUFBO0VBQ0EsZ0JBQUE7RUFDQSxpQkFBQTtFQUVBLGlCQUFBO0FDakNoQjtBRG1DZ0I7RUFDSSxjQUFBO0FDakNwQjtBRG9DZ0I7RUFDSSxrQkFBQTtBQ2xDcEI7QURzQ1k7RUFDSSxlQUFBO0VBQ0Esa0JBQUE7QUNwQ2hCO0FEeUNJO0VBQ0kscUJBQUE7RUFFQSxhQUFBO0VBQ0EsbUJBQUE7RUFFQSxrQkFBQTtFQUNBLFVBQUE7RUFDQSx5QkFBQTtFQUNBLFlBQUE7QUN6Q1I7QUQyQ1E7RUFDSSxnQkFBQTtFQUNBLGlCQUFBO0FDekNaO0FENkNZO0VBQ0ksaUJBQUE7QUMzQ2hCIiwiZmlsZSI6InNyYy9hcHAvbW9kdWxlcy9wcm9qZWN0cy9wYWdlcy9pbmRleC9pbmRleC5wYWdlLnNjc3MiLCJzb3VyY2VzQ29udGVudCI6WyJcbiNwYW5lbHMtY29udGFpbmVyIHtcbiAgICBkaXNwbGF5OiBncmlkO1xuICAgIGdyaWQtdGVtcGxhdGUtcm93czogODVweCAxZnIgMjUwcHggMzVweDtcbiAgICBncmlkLXRlbXBsYXRlLWNvbHVtbnM6IDFmciAyNTBweDtcbiAgICBncmlkLXRlbXBsYXRlLWFyZWFzOlxuICAgICAgICBcIm9wdGlvbnMtcGFuZSBvcHRpb25zLXBhbmVcIlxuICAgICAgICBcImVtYmVkZGluZy1wbG90IGNsdXN0ZXItcGFuZVwiXG4gICAgICAgIFwic2VsZWN0ZWQtYXR0cmlidXRpb25zIHNlbGVjdGVkLWF0dHJpYnV0aW9uc1wiXG4gICAgICAgIFwic3RhdHVzLWJhciBzdGF0dXMtYmFyXCJcbiAgICA7XG5cbiAgICAjY2x1c3Rlci1wYW5lIHtcbiAgICAgICAgZ3JpZC1hcmVhOiBjbHVzdGVyLXBhbmU7XG5cbiAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogI0VGRUZFRjtcblxuICAgICAgICBoZWlnaHQ6IGNhbGMoMTAwdmggLSA0MzBweCk7XG4gICAgICAgIG92ZXJmbG93LXg6IGhpZGRlbjtcbiAgICAgICAgb3ZlcmZsb3cteTogYXV0bztcblxuICAgICAgICAuY2x1c3Rlci1zZWxlY3Rpb24tYnV0dG9ucy1jb250YWluZXIge1xuXG4gICAgICAgICAgICBidXR0b24ge1xuICAgICAgICAgICAgICAgIG1hcmdpbi1yaWdodDogMDtcbiAgICAgICAgICAgICAgICB3aWR0aDogMjAwcHg7XG4gICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xuICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAgICAgICAgfVxuICAgIH1cblxuICAgICNlbWJlZGRpbmctcGxvdCB7XG4gICAgICAgIGdyaWQtYXJlYTogZW1iZWRkaW5nLXBsb3Q7XG4gICAgICAgIHdpZHRoOiBjYWxjKDEwMHZ3IC0gMjUwcHgpO1xuICAgICAgICBoZWlnaHQ6IGNhbGMoMTAwdmggLSA0MzBweCk7XG5cbiAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogI0VGRUZFRjtcblxuICAgICAgICAjYXR0cmlidXRpb24taG92ZXItcHJldmlldyB7XG4gICAgICAgICAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG5cbiAgICAgICAgICAgIHRvcDogMTY5cHg7XG4gICAgICAgICAgICBsZWZ0OiAyNHB4O1xuICAgICAgICAgICAgbWluLXdpZHRoOiAxMjhweDtcbiAgICAgICAgICAgIG1pbi1oZWlnaHQ6IDEyOHB4O1xuICAgICAgICAgICAgbWF4LXdpZHRoOiAyNTZweDtcbiAgICAgICAgICAgIG1heC1oZWlnaHQ6IDI1NnB4O1xuXG4gICAgICAgICAgICB6LWluZGV4OiA5OTk5O1xuXG4gICAgICAgICAgICBpbWFnZS1yZW5kZXJpbmc6IHBpeGVsYXRlZDtcbiAgICAgICAgfVxuICAgIH1cblxuICAgICNvcHRpb25zLXBhbmUge1xuICAgICAgICBncmlkLWFyZWE6IG9wdGlvbnMtcGFuZTtcblxuICAgICAgICBkaXNwbGF5OiBmbGV4O1xuICAgICAgICBhbGlnbi1pdGVtczogY2VudGVyO1xuXG4gICAgICAgIGJhY2tncm91bmQtY29sb3I6ICNFRkVGRUY7XG4gICAgICAgIG1hcmdpbjogMDtcbiAgICAgICAgei1pbmRleDogMTtcblxuICAgICAgICBvdmVyZmxvdy14OiBhdXRvO1xuICAgICAgICBvdmVyZmxvdy15OiBoaWRkZW47XG5cbiAgICAgICAgY2xyLXNlbGVjdC1jb250YWluZXIsIGltZyB7XG4gICAgICAgICAgICBtYXJnaW46IDAgMCAwIDI0cHg7XG4gICAgICAgIH1cblxuICAgICAgICBpbWcge1xuICAgICAgICAgICAgcGFkZGluZy1yaWdodDogMjRweDtcbiAgICAgICAgICAgIHdpZHRoOiAxNzRweDtcbiAgICAgICAgICAgIGhlaWdodDogNDBweDtcbiAgICAgICAgfVxuICAgIH1cblxuICAgICNzZWxlY3RlZC1hdHRyaWJ1dGlvbnMge1xuICAgICAgICBncmlkLWFyZWE6IHNlbGVjdGVkLWF0dHJpYnV0aW9ucztcbiAgICAgICAgaGVpZ2h0OiAxMDAlO1xuICAgICAgICB3aWR0aDogMTAwJTtcblxuICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjRUZFRkVGO1xuXG4gICAgICAgIG92ZXJmbG93LXg6IGF1dG87XG4gICAgICAgIG92ZXJmbG93LXk6IGhpZGRlbjtcbiAgICAgICAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcblxuICAgICAgICAuc3Bpbm5lci1sb2NhbGx5LWNlbnRlcmVkIHtcbiAgICAgICAgICAgIHBvc2l0aW9uOiByZWxhdGl2ZTtcbiAgICAgICAgICAgIHRvcDogY2FsYyg1MCUgLSAxLjVyZW0pO1xuICAgICAgICAgICAgbGVmdDogY2FsYyg1MCUgLSAxLjVyZW0pO1xuICAgICAgICB9XG5cbiAgICAgICAgI3NlbGVjdGlvbi1oaW50IHtcbiAgICAgICAgICAgIGRpc3BsYXk6IHRhYmxlO1xuXG4gICAgICAgICAgICBoZWlnaHQ6IGNhbGMoMTAwJSAtIDI0cHgpO1xuICAgICAgICAgICAgd2lkdGg6IGNhbGMoMTAwJSAtIDI0cHgpO1xuICAgICAgICAgICAgbWFyZ2luOiAxMnB4IDEycHggMTJweCAxMnB4O1xuXG4gICAgICAgICAgICBib3JkZXI6IDFweCBkYXNoZWQgcmdiKDE5MiwgMTkyLCAxOTIpO1xuICAgICAgICAgICAgYm9yZGVyLXJhZGl1czogNXB4O1xuXG4gICAgICAgICAgICB0ZXh0LWFsaWduOiBjZW50ZXI7XG5cbiAgICAgICAgICAgIHAge1xuICAgICAgICAgICAgICAgIHZlcnRpY2FsLWFsaWduOiBtaWRkbGU7XG4gICAgICAgICAgICAgICAgZGlzcGxheTogdGFibGUtY2VsbDtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuXG4gICAgICAgICNzZWxlY3RlZC1hdHRyaWJ1dGlvbi1saXN0IHtcbiAgICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgICBhbGlnbi1pdGVtczogY2VudGVyO1xuXG4gICAgICAgICAgICBoZWlnaHQ6IDIyNnB4O1xuICAgICAgICAgICAgbWFyZ2luOiAxMnB4O1xuXG4gICAgICAgICAgICAuc2VsZWN0ZWQtYXR0cmlidXRpb24ge1xuICAgICAgICAgICAgICAgIG1pbi13aWR0aDogMTgwcHg7XG4gICAgICAgICAgICAgICAgbWluLWhlaWdodDogMjEwcHg7XG4gICAgICAgICAgICAgICAgbWF4LXdpZHRoOiAxODBweDtcbiAgICAgICAgICAgICAgICBtYXgtaGVpZ2h0OiAyMTBweDtcblxuICAgICAgICAgICAgICAgIG1hcmdpbi1sZWZ0OiAxMnB4O1xuXG4gICAgICAgICAgICAgICAgJjpmaXJzdC1jaGlsZCB7XG4gICAgICAgICAgICAgICAgICAgIG1hcmdpbi1sZWZ0OiAwO1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgICAgICY6bGFzdC1jaGlsZCB7XG4gICAgICAgICAgICAgICAgICAgIG1hcmdpbi1yaWdodDogMTJweDtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIHAge1xuICAgICAgICAgICAgICAgIG1hcmdpbi10b3A6IDZweDtcbiAgICAgICAgICAgICAgICB0ZXh0LWFsaWduOiBjZW50ZXI7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICAjc3RhdHVzLWJhciB7XG4gICAgICAgIGdyaWQtYXJlYTogc3RhdHVzLWJhcjtcblxuICAgICAgICBkaXNwbGF5OiBmbGV4O1xuICAgICAgICBhbGlnbi1pdGVtczogY2VudGVyO1xuXG4gICAgICAgIHBhZGRpbmctbGVmdDogMXJlbTtcbiAgICAgICAgei1pbmRleDogMTtcbiAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzI3MTMzNTtcbiAgICAgICAgY29sb3I6IHdoaXRlO1xuXG4gICAgICAgIHN0cm9uZyB7XG4gICAgICAgICAgICBtYXJnaW4tbGVmdDogNXB4O1xuICAgICAgICAgICAgbWFyZ2luLXJpZ2h0OiA1cHg7XG4gICAgICAgIH1cblxuICAgICAgICBjbHItaWNvbiB7XG4gICAgICAgICAgICAmOm5vdCg6Zmlyc3QtY2hpbGQpIHtcbiAgICAgICAgICAgICAgICBtYXJnaW4tbGVmdDogMjBweDtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbn1cbiIsIiNwYW5lbHMtY29udGFpbmVyIHtcbiAgZGlzcGxheTogZ3JpZDtcbiAgZ3JpZC10ZW1wbGF0ZS1yb3dzOiA4NXB4IDFmciAyNTBweCAzNXB4O1xuICBncmlkLXRlbXBsYXRlLWNvbHVtbnM6IDFmciAyNTBweDtcbiAgZ3JpZC10ZW1wbGF0ZS1hcmVhczogXCJvcHRpb25zLXBhbmUgb3B0aW9ucy1wYW5lXCIgXCJlbWJlZGRpbmctcGxvdCBjbHVzdGVyLXBhbmVcIiBcInNlbGVjdGVkLWF0dHJpYnV0aW9ucyBzZWxlY3RlZC1hdHRyaWJ1dGlvbnNcIiBcInN0YXR1cy1iYXIgc3RhdHVzLWJhclwiO1xufVxuI3BhbmVscy1jb250YWluZXIgI2NsdXN0ZXItcGFuZSB7XG4gIGdyaWQtYXJlYTogY2x1c3Rlci1wYW5lO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjRUZFRkVGO1xuICBoZWlnaHQ6IGNhbGMoMTAwdmggLSA0MzBweCk7XG4gIG92ZXJmbG93LXg6IGhpZGRlbjtcbiAgb3ZlcmZsb3cteTogYXV0bztcbn1cbiNwYW5lbHMtY29udGFpbmVyICNjbHVzdGVyLXBhbmUgLmNsdXN0ZXItc2VsZWN0aW9uLWJ1dHRvbnMtY29udGFpbmVyIHtcbiAgZGlzcGxheTogZmxleDtcbiAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNjbHVzdGVyLXBhbmUgLmNsdXN0ZXItc2VsZWN0aW9uLWJ1dHRvbnMtY29udGFpbmVyIGJ1dHRvbiB7XG4gIG1hcmdpbi1yaWdodDogMDtcbiAgd2lkdGg6IDIwMHB4O1xufVxuI3BhbmVscy1jb250YWluZXIgI2VtYmVkZGluZy1wbG90IHtcbiAgZ3JpZC1hcmVhOiBlbWJlZGRpbmctcGxvdDtcbiAgd2lkdGg6IGNhbGMoMTAwdncgLSAyNTBweCk7XG4gIGhlaWdodDogY2FsYygxMDB2aCAtIDQzMHB4KTtcbiAgYmFja2dyb3VuZC1jb2xvcjogI0VGRUZFRjtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNlbWJlZGRpbmctcGxvdCAjYXR0cmlidXRpb24taG92ZXItcHJldmlldyB7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgdG9wOiAxNjlweDtcbiAgbGVmdDogMjRweDtcbiAgbWluLXdpZHRoOiAxMjhweDtcbiAgbWluLWhlaWdodDogMTI4cHg7XG4gIG1heC13aWR0aDogMjU2cHg7XG4gIG1heC1oZWlnaHQ6IDI1NnB4O1xuICB6LWluZGV4OiA5OTk5O1xuICBpbWFnZS1yZW5kZXJpbmc6IHBpeGVsYXRlZDtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNvcHRpb25zLXBhbmUge1xuICBncmlkLWFyZWE6IG9wdGlvbnMtcGFuZTtcbiAgZGlzcGxheTogZmxleDtcbiAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAgYmFja2dyb3VuZC1jb2xvcjogI0VGRUZFRjtcbiAgbWFyZ2luOiAwO1xuICB6LWluZGV4OiAxO1xuICBvdmVyZmxvdy14OiBhdXRvO1xuICBvdmVyZmxvdy15OiBoaWRkZW47XG59XG4jcGFuZWxzLWNvbnRhaW5lciAjb3B0aW9ucy1wYW5lIGNsci1zZWxlY3QtY29udGFpbmVyLCAjcGFuZWxzLWNvbnRhaW5lciAjb3B0aW9ucy1wYW5lIGltZyB7XG4gIG1hcmdpbjogMCAwIDAgMjRweDtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNvcHRpb25zLXBhbmUgaW1nIHtcbiAgcGFkZGluZy1yaWdodDogMjRweDtcbiAgd2lkdGg6IDE3NHB4O1xuICBoZWlnaHQ6IDQwcHg7XG59XG4jcGFuZWxzLWNvbnRhaW5lciAjc2VsZWN0ZWQtYXR0cmlidXRpb25zIHtcbiAgZ3JpZC1hcmVhOiBzZWxlY3RlZC1hdHRyaWJ1dGlvbnM7XG4gIGhlaWdodDogMTAwJTtcbiAgd2lkdGg6IDEwMCU7XG4gIGJhY2tncm91bmQtY29sb3I6ICNFRkVGRUY7XG4gIG92ZXJmbG93LXg6IGF1dG87XG4gIG92ZXJmbG93LXk6IGhpZGRlbjtcbiAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNzZWxlY3RlZC1hdHRyaWJ1dGlvbnMgLnNwaW5uZXItbG9jYWxseS1jZW50ZXJlZCB7XG4gIHBvc2l0aW9uOiByZWxhdGl2ZTtcbiAgdG9wOiBjYWxjKDUwJSAtIDEuNXJlbSk7XG4gIGxlZnQ6IGNhbGMoNTAlIC0gMS41cmVtKTtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNzZWxlY3RlZC1hdHRyaWJ1dGlvbnMgI3NlbGVjdGlvbi1oaW50IHtcbiAgZGlzcGxheTogdGFibGU7XG4gIGhlaWdodDogY2FsYygxMDAlIC0gMjRweCk7XG4gIHdpZHRoOiBjYWxjKDEwMCUgLSAyNHB4KTtcbiAgbWFyZ2luOiAxMnB4IDEycHggMTJweCAxMnB4O1xuICBib3JkZXI6IDFweCBkYXNoZWQgc2lsdmVyO1xuICBib3JkZXItcmFkaXVzOiA1cHg7XG4gIHRleHQtYWxpZ246IGNlbnRlcjtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNzZWxlY3RlZC1hdHRyaWJ1dGlvbnMgI3NlbGVjdGlvbi1oaW50IHAge1xuICB2ZXJ0aWNhbC1hbGlnbjogbWlkZGxlO1xuICBkaXNwbGF5OiB0YWJsZS1jZWxsO1xufVxuI3BhbmVscy1jb250YWluZXIgI3NlbGVjdGVkLWF0dHJpYnV0aW9ucyAjc2VsZWN0ZWQtYXR0cmlidXRpb24tbGlzdCB7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGFsaWduLWl0ZW1zOiBjZW50ZXI7XG4gIGhlaWdodDogMjI2cHg7XG4gIG1hcmdpbjogMTJweDtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNzZWxlY3RlZC1hdHRyaWJ1dGlvbnMgI3NlbGVjdGVkLWF0dHJpYnV0aW9uLWxpc3QgLnNlbGVjdGVkLWF0dHJpYnV0aW9uIHtcbiAgbWluLXdpZHRoOiAxODBweDtcbiAgbWluLWhlaWdodDogMjEwcHg7XG4gIG1heC13aWR0aDogMTgwcHg7XG4gIG1heC1oZWlnaHQ6IDIxMHB4O1xuICBtYXJnaW4tbGVmdDogMTJweDtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNzZWxlY3RlZC1hdHRyaWJ1dGlvbnMgI3NlbGVjdGVkLWF0dHJpYnV0aW9uLWxpc3QgLnNlbGVjdGVkLWF0dHJpYnV0aW9uOmZpcnN0LWNoaWxkIHtcbiAgbWFyZ2luLWxlZnQ6IDA7XG59XG4jcGFuZWxzLWNvbnRhaW5lciAjc2VsZWN0ZWQtYXR0cmlidXRpb25zICNzZWxlY3RlZC1hdHRyaWJ1dGlvbi1saXN0IC5zZWxlY3RlZC1hdHRyaWJ1dGlvbjpsYXN0LWNoaWxkIHtcbiAgbWFyZ2luLXJpZ2h0OiAxMnB4O1xufVxuI3BhbmVscy1jb250YWluZXIgI3NlbGVjdGVkLWF0dHJpYnV0aW9ucyAjc2VsZWN0ZWQtYXR0cmlidXRpb24tbGlzdCBwIHtcbiAgbWFyZ2luLXRvcDogNnB4O1xuICB0ZXh0LWFsaWduOiBjZW50ZXI7XG59XG4jcGFuZWxzLWNvbnRhaW5lciAjc3RhdHVzLWJhciB7XG4gIGdyaWQtYXJlYTogc3RhdHVzLWJhcjtcbiAgZGlzcGxheTogZmxleDtcbiAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAgcGFkZGluZy1sZWZ0OiAxcmVtO1xuICB6LWluZGV4OiAxO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjcxMzM1O1xuICBjb2xvcjogd2hpdGU7XG59XG4jcGFuZWxzLWNvbnRhaW5lciAjc3RhdHVzLWJhciBzdHJvbmcge1xuICBtYXJnaW4tbGVmdDogNXB4O1xuICBtYXJnaW4tcmlnaHQ6IDVweDtcbn1cbiNwYW5lbHMtY29udGFpbmVyICNzdGF0dXMtYmFyIGNsci1pY29uOm5vdCg6Zmlyc3QtY2hpbGQpIHtcbiAgbWFyZ2luLWxlZnQ6IDIwcHg7XG59Il19 */");

/***/ }),

/***/ "./src/app/modules/projects/pages/index/index.page.ts":
/*!************************************************************!*\
  !*** ./src/app/modules/projects/pages/index/index.page.ts ***!
  \************************************************************/
/*! exports provided: IndexPage */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "IndexPage", function() { return IndexPage; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! src/services/projects/projects.service */ "./src/services/projects/projects.service.ts");
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/router */ "./node_modules/@angular/router/fesm5/router.js");
/* harmony import */ var src_services_analyses_analyses_service__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! src/services/analyses/analyses.service */ "./src/services/analyses/analyses.service.ts");
/* harmony import */ var src_services_attributions_attributions_service__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! src/services/attributions/attributions.service */ "./src/services/attributions/attributions.service.ts");
/* harmony import */ var src_services_dataset_dataset_service__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! src/services/dataset/dataset.service */ "./src/services/dataset/dataset.service.ts");
/* harmony import */ var src_services_colorMaps_color_maps_service__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! src/services/colorMaps/color-maps.service */ "./src/services/colorMaps/color-maps.service.ts");
/* harmony import */ var three__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! three */ "./node_modules/three/build/three.module.js");









/**
 * Represents the index page of a project
 */
var IndexPage = /** @class */ (function () {
    /**
     * Initializes a new IndexPage instance.
     * @param projectsService The service which is used to manage projects.
     * @param analysesService The service which is used to manage analyses.
     * @param attributionsService The service which is used to manage attributions.
     * @param datasetService The service which is used to manage the datasets.
     * @param colorMapsService The service which is used to manage color maps.
     * @param route The currently activated route.
     */
    function IndexPage(projectsService, analysesService, attributionsService, datasetService, colorMapsService, route) {
        this.projectsService = projectsService;
        this.analysesService = analysesService;
        this.attributionsService = attributionsService;
        this.datasetService = datasetService;
        this.colorMapsService = colorMapsService;
        this.route = route;
        /**
         * Contains the index of the dimension of the embedding that is to be displayed in the plot.
         */
        this.firstDimension = 0;
        /**
         * Contains the index of the dimension of the embedding that is to be displayed in the plot.
         */
        this.secondDimension = 1;
        /**
         * Contains the layout of the plot of the eigen values.
         */
        this.eigenValuesGraphLayout = {
            title: 'Eigen Values',
            margin: {
                l: 32,
                r: 16,
                t: 32,
                b: 48,
                pad: 0
            },
            xaxis: {
                autotick: false,
                ticks: 'outside',
                tick0: 0,
                dtick: 5,
                fixedrange: true
            },
            yaxis: {
                fixedrange: true
            },
            paper_bgcolor: '#00000000',
            plot_bgcolor: '#00000000'
        };
    }
    Object.defineProperty(IndexPage.prototype, "embeddingDimensions", {
        /**
         * Gets a list of all the dimensions that are available in the currently selected embedding.
         */
        get: function () {
            if (!this.analysis || this.analysis.embedding.length === 0) {
                return new Array();
            }
            return new Array(this.analysis.embedding[0].value.length).fill(0).map(function (_, index) { return index; });
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(IndexPage.prototype, "selectedAnalysisMethod", {
        /**
         * Gets the analysis method that was selected by the user.
         */
        get: function () {
            return this._selectedAnalysisMethod;
        },
        /**
         * Sets the analysis method that was selected by the user.
         */
        set: function (value) {
            this._selectedAnalysisMethod = value;
            if (value) {
                this.selectedDataPoints = null;
                this.selectedCategory = this.selectedAnalysisMethod.categories[0];
                var initialClustering = this.selectedAnalysisMethod.clusterings.filter(function (clustering) { return parseInt(clustering, 10) === 10; });
                if (initialClustering.length > 0) {
                    this.selectedClustering = initialClustering[0];
                }
                else {
                    this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
                }
                if (this.selectedAnalysisMethod.embeddings.filter(function (embedding) { return embedding === 'tsne'; }).length > 0) {
                    this.selectedEmbedding = 'tsne';
                }
                else {
                    this.selectedEmbedding = this.selectedAnalysisMethod.embeddings[0];
                }
                this.refreshAnalysisAsync();
            }
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(IndexPage.prototype, "selectedCategory", {
        /**
         * Gets the name of the selected category.
         */
        get: function () {
            return this._selectedCategory;
        },
        /**
         * Sets the name of the selected category.
         */
        set: function (value) {
            this._selectedCategory = value;
            if (value) {
                this.refreshAnalysisAsync();
            }
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(IndexPage.prototype, "selectedClustering", {
        /**
         * Gets the name of the selected clustering.
         */
        get: function () {
            return this._selectedClustering;
        },
        /**
         * Sets the name of the selected clustering.
         */
        set: function (value) {
            this._selectedClustering = value;
            if (value) {
                this.refreshAnalysisAsync();
            }
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(IndexPage.prototype, "selectedEmbedding", {
        /**
         * Gets the name of the selected embedding.
         */
        get: function () {
            return this._selectedEmbedding;
        },
        /**
         * Sets the name of the selected embedding.
         */
        set: function (value) {
            // Sets the new value
            this._selectedEmbedding = value;
            // Resets the dimensions that are to be displayed
            this.firstDimension = 0;
            this.secondDimension = 1;
            // Refreshes the analysis
            if (value) {
                this.refreshAnalysisAsync();
            }
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(IndexPage.prototype, "analysis", {
        /**
         * Gets the current analysis.
         */
        get: function () {
            return this._analysis;
        },
        /**
         * Sets the current analysis.
         * @param value The
         */
        set: function (value) {
            var e_1, _a;
            var _this = this;
            // Stores the new value
            this._analysis = value;
            // Determines the total number of clusters, which is needed to determine the number of colors that are needed
            // for the visualization
            if (this.analysis.embedding) {
                var clusters = new Array();
                try {
                    for (var _b = tslib__WEBPACK_IMPORTED_MODULE_0__["__values"](this.analysis.embedding.map(function (dataPoint) { return dataPoint.cluster; })), _c = _b.next(); !_c.done; _c = _b.next()) {
                        var cluster = _c.value;
                        if (clusters.indexOf(cluster) === -1) {
                            clusters.push(cluster);
                        }
                    }
                }
                catch (e_1_1) { e_1 = { error: e_1_1 }; }
                finally {
                    try {
                        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
                    }
                    finally { if (e_1) throw e_1.error; }
                }
                clusters.sort();
                this.numberOfClusters = clusters.length;
                this.availableClusters = clusters.map(function (cluster) {
                    return {
                        index: cluster,
                        color: new three__WEBPACK_IMPORTED_MODULE_8__["Color"]().setHSL((360 / _this.numberOfClusters * cluster) / 360, 0.5, 0.5).getStyle()
                    };
                });
            }
            // Refreshes the plot that displays the eigen values
            this.refreshEigenValuePlot();
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(IndexPage.prototype, "selectedDataPoints", {
        /**
         * Gets the data points that were selected by the user.
         */
        get: function () {
            return this._selectedDataPoints;
        },
        /**
         * Sets the data points that were selected by the user.
         */
        set: function (value) {
            this._selectedDataPoints = value;
            this.refreshAttributionsAsync();
        },
        enumerable: true,
        configurable: true
    });
    /**
     * Refreshes the eigen value plot.
     */
    IndexPage.prototype.refreshEigenValuePlot = function () {
        if (!this.analysis) {
            return;
        }
        this.eigenValuesGraphData = new Array();
        this.eigenValuesGraphData.push({
            name: 'Eigen Values',
            x: this.analysis.eigenValues.map(function (_, index) { return index; }).reverse(),
            y: this.analysis.eigenValues,
            type: 'bar',
            width: 0.25,
            hoverinfo: 'x',
            color: 'y'
        });
    };
    /**
     * Reloads the project and all its information.
     */
    IndexPage.prototype.refreshProjectAsync = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            var _a, initialClustering;
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.isLoading = true;
                        _a = this;
                        return [4 /*yield*/, this.projectsService.getByIdAsync(this.id)];
                    case 1:
                        _a.project = _b.sent();
                        this.selectedDataPoints = null;
                        this._selectedAnalysisMethod = this.project.analysisMethods[0];
                        this._selectedCategory = this.selectedAnalysisMethod.categories[0];
                        initialClustering = this.selectedAnalysisMethod.clusterings.filter(function (clustering) { return parseInt(clustering, 10) === 10; });
                        if (initialClustering.length > 0) {
                            this.selectedClustering = initialClustering[0];
                        }
                        else {
                            this.selectedClustering = this.selectedAnalysisMethod.clusterings[0];
                        }
                        if (this.selectedAnalysisMethod.embeddings.filter(function (embedding) { return embedding === 'tsne'; }).length > 0) {
                            this._selectedEmbedding = 'tsne';
                        }
                        else {
                            this._selectedEmbedding = this.selectedAnalysisMethod.embeddings[0];
                        }
                        return [4 /*yield*/, this.refreshAnalysisAsync()];
                    case 2:
                        _b.sent();
                        this.isLoading = false;
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Reloads the analysis and all its information.
     */
    IndexPage.prototype.refreshAnalysisAsync = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            var _a;
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!this.selectedAnalysisMethod ||
                            !this.selectedCategory ||
                            !this.selectedClustering ||
                            !this.selectedEmbedding) {
                            return [2 /*return*/];
                        }
                        this.isLoading = true;
                        this.selectedDataPoints = null;
                        _a = this;
                        return [4 /*yield*/, this.analysesService.getAsync(this.project.id, this.selectedAnalysisMethod.name, this.selectedCategory.name, this.selectedClustering, this.selectedEmbedding)];
                    case 1:
                        _a.analysis = _b.sent();
                        this.isLoading = false;
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Is invoked when the user selects data points. Updates the attributions that are displayed
     */
    IndexPage.prototype.refreshAttributionsAsync = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            var dataPoints, attributionIndices, attributions, datasetSamples, _loop_1, this_1, index;
            var _this = this;
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0:
                        // Checks if any data points were selected, if not, then the attributions can be removed
                        if (!this.selectedDataPoints || this.selectedDataPoints.length === 0) {
                            this.selectedAttributions = null;
                            return [2 /*return*/];
                        }
                        // Gets the attributions of the data points that were selected
                        this.isLoadingAttributions = true;
                        dataPoints = this.selectedDataPoints;
                        attributionIndices = dataPoints.map(function (dataPoint) { return dataPoint.attributionIndex; }).slice(0, 20);
                        return [4 /*yield*/, Promise.all(attributionIndices.map(function (index) { return _this.attributionsService.getAsync(_this.project.id, index); }))];
                    case 1:
                        attributions = _a.sent();
                        return [4 /*yield*/, Promise.all(attributions.map(function (attribution) { return _this.datasetService.getAsync(_this.project.id, attribution.index); }))];
                    case 2:
                        datasetSamples = _a.sent();
                        // Assigns the dataset sample to their respective attribution
                        this.selectedAttributions = [];
                        _loop_1 = function (index) {
                            this_1.selectedAttributions.push({
                                attribution: attributions[index],
                                sample: datasetSamples.filter(function (sample) { return sample.index === attributions[index].index; })[0],
                                color: this_1.availableClusters.filter(function (cluster) { return cluster.index === dataPoints[index].cluster; })[0].color,
                                clusterIndex: dataPoints[index].cluster
                            });
                        };
                        this_1 = this;
                        for (index = 0; index < attributions.length; index++) {
                            _loop_1(index);
                        }
                        this.isLoadingAttributions = false;
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Is invoked when the component is initialized. Retrieves the ID of the project from the URL and loads it
     */
    IndexPage.prototype.ngOnInit = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            var _a, defaultColorMaps;
            var _this = this;
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_b) {
                switch (_b.label) {
                    case 0:
                        // Subscribes for changes of the route, when the route has changed, then the project ID is retrieved from the
                        // URL and the project is loaded
                        this.route.paramMap.subscribe(function (paramMap) {
                            if (paramMap.has('id') && paramMap.get('id')) {
                                _this.id = parseInt(paramMap.get('id'), 10);
                                _this.refreshProjectAsync();
                            }
                        });
                        // Loads the color maps from the RESTful API
                        _a = this;
                        return [4 /*yield*/, this.colorMapsService.getAsync()];
                    case 1:
                        // Loads the color maps from the RESTful API
                        _a.colorMaps = _b.sent();
                        defaultColorMaps = this.colorMaps.filter(function (colorMap) { return colorMap.name === 'black-fire-red'; });
                        if (defaultColorMaps.length > 0) {
                            this.selectedColorMap = defaultColorMaps[0];
                        }
                        else {
                            this.selectedColorMap = this.colorMaps[0];
                        }
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Is invoked when the user hovers the mouse over an embedding.
     * @param event The event object that contains the information about the embedding that the user hovered over.
     */
    IndexPage.prototype.onHoverAsync = function (event) {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            var embedding, attribution, _a;
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.isHovering = true;
                        embedding = event.dataPoint;
                        return [4 /*yield*/, this.attributionsService.getAsync(this.project.id, embedding.attributionIndex)];
                    case 1:
                        attribution = _b.sent();
                        _a = this;
                        return [4 /*yield*/, this.datasetService.getAsync(this.project.id, attribution.index)];
                    case 2:
                        _a.datasetSampleHoverPreview = _b.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Is invoked when the user moves the mouse away from a sample.
     */
    IndexPage.prototype.onUnhover = function () {
        this.isHovering = false;
        this.datasetSampleHoverPreview = null;
    };
    /**
     * Selects the data points of the cluster with the specified index.
     * @param index The index of the cluster that is to be selected.
     */
    IndexPage.prototype.selectCluster = function (index) {
        var dataPointsOfCluster = this.analysis.embedding.filter(function (dataPoint) { return dataPoint.cluster === index; });
        this.selectedDataPoints = dataPointsOfCluster;
    };
    IndexPage.ctorParameters = function () { return [
        { type: src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_2__["ProjectsService"] },
        { type: src_services_analyses_analyses_service__WEBPACK_IMPORTED_MODULE_4__["AnalysesService"] },
        { type: src_services_attributions_attributions_service__WEBPACK_IMPORTED_MODULE_5__["AttributionsService"] },
        { type: src_services_dataset_dataset_service__WEBPACK_IMPORTED_MODULE_6__["DatasetService"] },
        { type: src_services_colorMaps_color_maps_service__WEBPACK_IMPORTED_MODULE_7__["ColorMapsService"] },
        { type: _angular_router__WEBPACK_IMPORTED_MODULE_3__["ActivatedRoute"] }
    ]; };
    IndexPage = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["Component"])({
            selector: 'page-projects-index',
            template: tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! raw-loader!./index.page.html */ "./node_modules/raw-loader/dist/cjs.js!./src/app/modules/projects/pages/index/index.page.html")).default,
            styles: [tslib__WEBPACK_IMPORTED_MODULE_0__["__importDefault"](__webpack_require__(/*! ./index.page.scss */ "./src/app/modules/projects/pages/index/index.page.scss")).default]
        })
    ], IndexPage);
    return IndexPage;
}());



/***/ }),

/***/ "./src/app/modules/projects/projects.module.ts":
/*!*****************************************************!*\
  !*** ./src/app/modules/projects/projects.module.ts ***!
  \*****************************************************/
/*! exports provided: ProjectsModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ProjectsModule", function() { return ProjectsModule; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/platform-browser */ "./node_modules/@angular/platform-browser/fesm5/platform-browser.js");
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/router */ "./node_modules/@angular/router/fesm5/router.js");
/* harmony import */ var _clr_angular__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @clr/angular */ "./node_modules/@clr/angular/fesm5/clr-angular.js");
/* harmony import */ var plotly_js_dist_plotly_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! plotly.js/dist/plotly.js */ "./node_modules/plotly.js/dist/plotly.js");
/* harmony import */ var plotly_js_dist_plotly_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(plotly_js_dist_plotly_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var angular_plotly_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! angular-plotly.js */ "./node_modules/angular-plotly.js/fesm5/angular-plotly.js.js");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm5/forms.js");
/* harmony import */ var src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! src/services/projects/projects.service */ "./src/services/projects/projects.service.ts");
/* harmony import */ var _projects_routes__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./projects.routes */ "./src/app/modules/projects/projects.routes.ts");
/* harmony import */ var _pages_index_index_page__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./pages/index/index.page */ "./src/app/modules/projects/pages/index/index.page.ts");
/* harmony import */ var src_services_analyses_analyses_service__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! src/services/analyses/analyses.service */ "./src/services/analyses/analyses.service.ts");
/* harmony import */ var src_services_attributions_attributions_service__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! src/services/attributions/attributions.service */ "./src/services/attributions/attributions.service.ts");
/* harmony import */ var src_services_dataset_dataset_service__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! src/services/dataset/dataset.service */ "./src/services/dataset/dataset.service.ts");
/* harmony import */ var src_app_components_components_module__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! src/app/components/components.module */ "./src/app/components/components.module.ts");
/* harmony import */ var src_services_colorMaps_color_maps_service__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! src/services/colorMaps/color-maps.service */ "./src/services/colorMaps/color-maps.service.ts");
















angular_plotly_js__WEBPACK_IMPORTED_MODULE_6__["PlotlyModule"].plotlyjs = plotly_js_dist_plotly_js__WEBPACK_IMPORTED_MODULE_5__;
/**
 * Represents the module that contains the project pages.
 */
var ProjectsModule = /** @class */ (function () {
    function ProjectsModule() {
    }
    ProjectsModule = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["NgModule"])({
            declarations: [
                _pages_index_index_page__WEBPACK_IMPORTED_MODULE_10__["IndexPage"]
            ],
            imports: [
                _angular_platform_browser__WEBPACK_IMPORTED_MODULE_2__["BrowserModule"],
                _angular_forms__WEBPACK_IMPORTED_MODULE_7__["FormsModule"],
                _clr_angular__WEBPACK_IMPORTED_MODULE_4__["ClarityModule"],
                angular_plotly_js__WEBPACK_IMPORTED_MODULE_6__["PlotlyModule"],
                src_app_components_components_module__WEBPACK_IMPORTED_MODULE_14__["ComponentsModule"],
                _angular_router__WEBPACK_IMPORTED_MODULE_3__["RouterModule"].forChild(_projects_routes__WEBPACK_IMPORTED_MODULE_9__["projectRoutes"])
            ],
            exports: [],
            providers: [
                src_services_projects_projects_service__WEBPACK_IMPORTED_MODULE_8__["ProjectsService"],
                src_services_analyses_analyses_service__WEBPACK_IMPORTED_MODULE_11__["AnalysesService"],
                src_services_attributions_attributions_service__WEBPACK_IMPORTED_MODULE_12__["AttributionsService"],
                src_services_dataset_dataset_service__WEBPACK_IMPORTED_MODULE_13__["DatasetService"],
                src_services_colorMaps_color_maps_service__WEBPACK_IMPORTED_MODULE_15__["ColorMapsService"]
            ]
        })
    ], ProjectsModule);
    return ProjectsModule;
}());



/***/ }),

/***/ "./src/app/modules/projects/projects.routes.ts":
/*!*****************************************************!*\
  !*** ./src/app/modules/projects/projects.routes.ts ***!
  \*****************************************************/
/*! exports provided: projectRoutes */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "projectRoutes", function() { return projectRoutes; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _pages_index_index_page__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./pages/index/index.page */ "./src/app/modules/projects/pages/index/index.page.ts");


/**
 * Defines the routes of the projects module.
 */
var projectRoutes = [
    { path: 'projects/:id', component: _pages_index_index_page__WEBPACK_IMPORTED_MODULE_1__["IndexPage"] }
];


/***/ }),

/***/ "./src/environments/environment.ts":
/*!*****************************************!*\
  !*** ./src/environments/environment.ts ***!
  \*****************************************/
/*! exports provided: environment */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "environment", function() { return environment; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");

// Contains the environment variables for the debug environment
var environment = {
    production: false,
    apiBaseUrl: 'http://localhost:8080'
};


/***/ }),

/***/ "./src/main.ts":
/*!*********************!*\
  !*** ./src/main.ts ***!
  \*********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/platform-browser-dynamic */ "./node_modules/@angular/platform-browser-dynamic/fesm5/platform-browser-dynamic.js");
/* harmony import */ var _app_app_module__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app/app.module */ "./src/app/app.module.ts");
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./environments/environment */ "./src/environments/environment.ts");





if (_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].production) {
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["enableProdMode"])();
}
Object(_angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_2__["platformBrowserDynamic"])()
    .bootstrapModule(_app_app_module__WEBPACK_IMPORTED_MODULE_3__["AppModule"])
    .catch(function (error) { return console.error(error); });


/***/ }),

/***/ "./src/services/analyses/analyses.service.ts":
/*!***************************************************!*\
  !*** ./src/services/analyses/analyses.service.ts ***!
  \***************************************************/
/*! exports provided: AnalysesService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AnalysesService", function() { return AnalysesService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var src_environments_environment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! src/environments/environment */ "./src/environments/environment.ts");
/* harmony import */ var _analysis__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./analysis */ "./src/services/analyses/analysis.ts");






/**
 * Represents a service for managing analyses of a project.
 */
var AnalysesService = /** @class */ (function () {
    /**
     * Initializes a new AnalysesService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    function AnalysesService(httpClient) {
        this.httpClient = httpClient;
    }
    /**
     * Gets the specified analysis from the project.
     * @param projectId The ID of the project from which the analysis is to be retrieved.
     * @param analysisMethod The name of the analysis method from which the analysis is to be retrieved.
     * @param category The name of the category from which the analysis is to be retrieved.
     * @param clustering The name of the clustering that was applied to the analysis.
     * @param embedding The name of the embedding that was applied to the analysis.
     */
    AnalysesService.prototype.getAsync = function (projectId, analysisMethod, category, clustering, embedding) {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.httpClient
                            .get(src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl + "/api/projects/" + projectId + "/analyses/" + analysisMethod + "?category=" + category + "&clustering=" + clustering + "&embedding=" + embedding, {
                            headers: new _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpHeaders"]({ 'Content-Type': 'application/json' })
                        })
                            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_1__["map"])(function (analysis) { return new _analysis__WEBPACK_IMPORTED_MODULE_5__["Analysis"](analysis); }))
                            .toPromise()];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    AnalysesService.ctorParameters = function () { return [
        { type: _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpClient"] }
    ]; };
    AnalysesService = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["Injectable"])()
    ], AnalysesService);
    return AnalysesService;
}());



/***/ }),

/***/ "./src/services/analyses/analysis.ts":
/*!*******************************************!*\
  !*** ./src/services/analyses/analysis.ts ***!
  \*******************************************/
/*! exports provided: Analysis */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Analysis", function() { return Analysis; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _embedding__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./embedding */ "./src/services/analyses/embedding.ts");


/**
 * Represents a single analysis.
 */
var Analysis = /** @class */ (function () {
    /**
     * Initializes a new Analysis instance.
     * @param analysis The JSON object that was retrieved from the RESTful API.
     */
    function Analysis(analysis) {
        if (analysis) {
            this.categoryName = analysis.categoryName;
            this.humanReadableCategoryName = analysis.humanReadableCategoryName;
            this.clusteringName = analysis.clusteringName;
            this.embeddingName = analysis.embeddingName;
            if (analysis.embedding) {
                this.embedding = analysis.embedding.map(function (embedding) { return new _embedding__WEBPACK_IMPORTED_MODULE_1__["Embedding"](embedding); });
            }
            this.eigenValues = analysis.eigenValues;
            this.baseEmbeddingName = analysis.baseEmbeddingName;
            this.baseEmbeddingAxesIndices = analysis.baseEmbeddingAxesIndices;
        }
    }
    return Analysis;
}());



/***/ }),

/***/ "./src/services/analyses/embedding.ts":
/*!********************************************!*\
  !*** ./src/services/analyses/embedding.ts ***!
  \********************************************/
/*! exports provided: Embedding */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Embedding", function() { return Embedding; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");

/**
 * Represents a single embedding.
 */
var Embedding = /** @class */ (function () {
    /**
     * Initializes a new Embedding instance.
     * @param embedding The JSON object that was retrieved from the RESTful service.
     */
    function Embedding(embedding) {
        if (embedding) {
            this.cluster = embedding.cluster;
            this.attributionIndex = embedding.attributionIndex;
            this.value = embedding.value;
        }
    }
    return Embedding;
}());



/***/ }),

/***/ "./src/services/attributions/attribution.ts":
/*!**************************************************!*\
  !*** ./src/services/attributions/attribution.ts ***!
  \**************************************************/
/*! exports provided: Attribution */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Attribution", function() { return Attribution; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");

/**
 * Represents a single attribution.
 */
var Attribution = /** @class */ (function () {
    /**
     * Initializes a new Attribution instance.
     * @param attribution The JSON object that was retrieved from the RESTful API.
     * @param baseUrl The base URL that is added to the heatmap URLs.
     */
    function Attribution(attribution, baseUrl) {
        if (attribution) {
            this.index = attribution.index;
            this.labels = attribution.labels;
            this.prediction = attribution.prediction;
            this.width = attribution.width;
            this.height = attribution.height;
            this.url = attribution.url;
            this.urls = attribution.urls;
            if (baseUrl) {
                this.url = baseUrl + this.url;
                for (var colorMap in this.urls) {
                    if (this.urls.hasOwnProperty(colorMap)) {
                        this.urls[colorMap] = baseUrl + this.urls[colorMap];
                    }
                }
            }
        }
    }
    Object.defineProperty(Attribution.prototype, "labelDisplay", {
        /**
         * Gets a comma-separated list of all labels, which can be used for displaying the labels.
         */
        get: function () {
            if (Array.isArray(this.labels)) {
                return this.labels.join(', ');
            }
            return this.labels;
        },
        enumerable: true,
        configurable: true
    });
    return Attribution;
}());



/***/ }),

/***/ "./src/services/attributions/attributions.service.ts":
/*!***********************************************************!*\
  !*** ./src/services/attributions/attributions.service.ts ***!
  \***********************************************************/
/*! exports provided: AttributionsService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AttributionsService", function() { return AttributionsService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var src_environments_environment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! src/environments/environment */ "./src/environments/environment.ts");
/* harmony import */ var _attribution__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./attribution */ "./src/services/attributions/attribution.ts");






/**
 * Represents a service for managing attributions of a project.
 */
var AttributionsService = /** @class */ (function () {
    /**
     * Initializes a new AttributionsService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    function AttributionsService(httpClient) {
        this.httpClient = httpClient;
    }
    /**
     * Gets the attribution with the specified index.
     * @param projectId The ID of the project from which the attribution is to be retrieved.
     * @param index The index of the attribution that is to be retrieved.
     */
    AttributionsService.prototype.getAsync = function (projectId, index) {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.httpClient
                            .get(src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl + "/api/projects/" + projectId + "/attributions/" + index, {
                            headers: new _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpHeaders"]({ 'Content-Type': 'application/json' })
                        })
                            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_1__["map"])(function (attribution) { return new _attribution__WEBPACK_IMPORTED_MODULE_5__["Attribution"](attribution, src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl); }))
                            .toPromise()];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    AttributionsService.ctorParameters = function () { return [
        { type: _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpClient"] }
    ]; };
    AttributionsService = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["Injectable"])()
    ], AttributionsService);
    return AttributionsService;
}());



/***/ }),

/***/ "./src/services/colorMaps/color-map.ts":
/*!*********************************************!*\
  !*** ./src/services/colorMaps/color-map.ts ***!
  \*********************************************/
/*! exports provided: ColorMap */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ColorMap", function() { return ColorMap; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");

/**
 * Represents a color map that can be used to render heatmaps.
 */
var ColorMap = /** @class */ (function () {
    /**
     * Initializes a new ColorMap instance.
     * @param colorMap The JSON object that was retrieved from the RESTful API.
     * @param baseUrl The base URL that is added to the heatmap URLs.
     */
    function ColorMap(colorMap, baseUrl) {
        if (colorMap) {
            this.name = colorMap.name;
            this.humanReadableName = colorMap.humanReadableName;
            this.url = colorMap.url;
            if (baseUrl) {
                this.url = baseUrl + this.url;
            }
        }
    }
    return ColorMap;
}());



/***/ }),

/***/ "./src/services/colorMaps/color-maps.service.ts":
/*!******************************************************!*\
  !*** ./src/services/colorMaps/color-maps.service.ts ***!
  \******************************************************/
/*! exports provided: ColorMapsService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ColorMapsService", function() { return ColorMapsService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var src_environments_environment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! src/environments/environment */ "./src/environments/environment.ts");
/* harmony import */ var _color_map__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./color-map */ "./src/services/colorMaps/color-map.ts");






/**
 * Represents a service for managing color maps.
 */
var ColorMapsService = /** @class */ (function () {
    /**
     * Initializes a new ColorMapsService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    function ColorMapsService(httpClient) {
        this.httpClient = httpClient;
    }
    /**
     * Gets all color maps.
     */
    ColorMapsService.prototype.getAsync = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.httpClient
                            .get(src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl + "/api/color-maps", {
                            headers: new _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpHeaders"]({ 'Content-Type': 'application/json' })
                        })
                            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_1__["map"])(function (colorMaps) { return colorMaps.map(function (colorMap) { return new _color_map__WEBPACK_IMPORTED_MODULE_5__["ColorMap"](colorMap, src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl); }); }))
                            .toPromise()];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    ColorMapsService.ctorParameters = function () { return [
        { type: _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpClient"] }
    ]; };
    ColorMapsService = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["Injectable"])()
    ], ColorMapsService);
    return ColorMapsService;
}());



/***/ }),

/***/ "./src/services/dataset/dataset.service.ts":
/*!*************************************************!*\
  !*** ./src/services/dataset/dataset.service.ts ***!
  \*************************************************/
/*! exports provided: DatasetService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "DatasetService", function() { return DatasetService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var src_environments_environment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! src/environments/environment */ "./src/environments/environment.ts");
/* harmony import */ var _sample__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./sample */ "./src/services/dataset/sample.ts");






/**
 * Represents a service for managing dataset samples of a project.
 */
var DatasetService = /** @class */ (function () {
    /**
     * Initializes a new DatasetService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    function DatasetService(httpClient) {
        this.httpClient = httpClient;
    }
    /**
     * Gets the dataset sample with the specified index.
     * @param projectId The ID of the project from which the dataset sample is to be retrieved.
     * @param index The index of the dataset sample that is to be retrieved.
     */
    DatasetService.prototype.getAsync = function (projectId, index) {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.httpClient
                            .get(src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl + "/api/projects/" + projectId + "/dataset/" + index, {
                            headers: new _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpHeaders"]({ 'Content-Type': 'application/json' })
                        })
                            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_1__["map"])(function (sample) { return new _sample__WEBPACK_IMPORTED_MODULE_5__["Sample"](sample, src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl); }))
                            .toPromise()];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    DatasetService.ctorParameters = function () { return [
        { type: _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpClient"] }
    ]; };
    DatasetService = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["Injectable"])()
    ], DatasetService);
    return DatasetService;
}());



/***/ }),

/***/ "./src/services/dataset/sample.ts":
/*!****************************************!*\
  !*** ./src/services/dataset/sample.ts ***!
  \****************************************/
/*! exports provided: Sample */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Sample", function() { return Sample; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");

/**
 * Represents a single sample from the dataset for which the analyses were performed.
 */
var Sample = /** @class */ (function () {
    /**
     * Initializes a new Sample instance.
     * @param sample The JSON object that was retrieved from the RESTful API.
     * @param baseUrl The base URL that is added to the image URL.
     */
    function Sample(sample, baseUrl) {
        if (sample) {
            this.index = sample.index;
            this.labels = sample.labels;
            this.width = sample.width;
            this.height = sample.height;
            this.url = sample.url;
            if (baseUrl) {
                this.url = baseUrl + this.url;
            }
        }
    }
    Object.defineProperty(Sample.prototype, "labelDisplay", {
        /**
         * Gets a comma-separated list of all labels, which can be used for displaying the labels.
         */
        get: function () {
            if (Array.isArray(this.labels)) {
                return this.labels.join(', ');
            }
            return this.labels;
        },
        enumerable: true,
        configurable: true
    });
    return Sample;
}());



/***/ }),

/***/ "./src/services/projects/analysis-category.ts":
/*!****************************************************!*\
  !*** ./src/services/projects/analysis-category.ts ***!
  \****************************************************/
/*! exports provided: AnalysisCategory */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AnalysisCategory", function() { return AnalysisCategory; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");

/**
 * Represents a single category in an analysis. One category can contain many analyses for different attributions. The
 * category name is usually an umbrella term for all the attributions contained in the analysis. This is most-likely
 * a class name.
 */
var AnalysisCategory = /** @class */ (function () {
    /**
     * Initializes a new AnalysisCategory instance.
     * @param analysisCategory The JSON object that was retrieved from the RESTful API.
     */
    function AnalysisCategory(analysisCategory) {
        if (analysisCategory) {
            this.name = analysisCategory.name;
            this.humanReadableName = analysisCategory.humanReadableName;
        }
    }
    return AnalysisCategory;
}());



/***/ }),

/***/ "./src/services/projects/analysis-method.ts":
/*!**************************************************!*\
  !*** ./src/services/projects/analysis-method.ts ***!
  \**************************************************/
/*! exports provided: AnalysisMethod */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AnalysisMethod", function() { return AnalysisMethod; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _analysis_category__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./analysis-category */ "./src/services/projects/analysis-category.ts");


/**
 * Represents an analysis method.
 */
var AnalysisMethod = /** @class */ (function () {
    /**
     * Initializes a new AnalysisMethod instance.
     * @param analysisMethod The JSON object that was retrieved from the RESTful API.
     */
    function AnalysisMethod(analysisMethod) {
        if (analysisMethod) {
            this.name = analysisMethod.name;
            if (analysisMethod.categories) {
                this.categories = analysisMethod.categories.map(function (category) { return new _analysis_category__WEBPACK_IMPORTED_MODULE_1__["AnalysisCategory"](category); });
            }
            this.clusterings = analysisMethod.clusterings;
            this.embeddings = analysisMethod.embeddings;
        }
    }
    return AnalysisMethod;
}());



/***/ }),

/***/ "./src/services/projects/project.ts":
/*!******************************************!*\
  !*** ./src/services/projects/project.ts ***!
  \******************************************/
/*! exports provided: Project */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Project", function() { return Project; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var _analysis_method__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./analysis-method */ "./src/services/projects/analysis-method.ts");


/**
 * Represents a single project from the workspace.
 */
var Project = /** @class */ (function () {
    /**
     * Initializes a new Project instance.
     * @param project The JSON object that was retrieved from the RESTful API.
     */
    function Project(project) {
        if (project) {
            this.id = project.id;
            this.name = project.name;
            this.model = project.model;
            this.dataset = project.dataset;
            if (project.analysisMethods) {
                this.analysisMethods = project.analysisMethods.map(function (analysisMethod) { return new _analysis_method__WEBPACK_IMPORTED_MODULE_1__["AnalysisMethod"](analysisMethod); });
            }
        }
    }
    return Project;
}());



/***/ }),

/***/ "./src/services/projects/projects.service.ts":
/*!***************************************************!*\
  !*** ./src/services/projects/projects.service.ts ***!
  \***************************************************/
/*! exports provided: ProjectsService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ProjectsService", function() { return ProjectsService; });
/* harmony import */ var tslib__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tslib */ "./node_modules/tslib/tslib.es6.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var src_environments_environment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! src/environments/environment */ "./src/environments/environment.ts");
/* harmony import */ var _project__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./project */ "./src/services/projects/project.ts");






/**
 * Represents a service for managing projects in the current workspace.
 */
var ProjectsService = /** @class */ (function () {
    /**
     * Initializes a new ProjectsService instance.
     * @param httpClient The HTTP client, which is used to interface with the RESTful API.
     */
    function ProjectsService(httpClient) {
        this.httpClient = httpClient;
    }
    /**
     * Gets all projects from the current workspace.
     */
    ProjectsService.prototype.getAsync = function () {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.httpClient
                            .get(src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl + "/api/projects", {
                            headers: new _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpHeaders"]({ 'Content-Type': 'application/json' })
                        })
                            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_1__["map"])(function (projects) { return projects.map(function (project) { return new _project__WEBPACK_IMPORTED_MODULE_5__["Project"](project); }); }))
                            .toPromise()];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    /**
     * Gets the project with the specified ID.
     * @param id The ID of the project that is to be retrieved.
     */
    ProjectsService.prototype.getByIdAsync = function (id) {
        return tslib__WEBPACK_IMPORTED_MODULE_0__["__awaiter"](this, void 0, void 0, function () {
            return tslib__WEBPACK_IMPORTED_MODULE_0__["__generator"](this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.httpClient
                            .get(src_environments_environment__WEBPACK_IMPORTED_MODULE_4__["environment"].apiBaseUrl + "/api/projects/" + id, {
                            headers: new _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpHeaders"]({ 'Content-Type': 'application/json' })
                        })
                            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_1__["map"])(function (project) { return new _project__WEBPACK_IMPORTED_MODULE_5__["Project"](project); }))
                            .toPromise()];
                    case 1: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    ProjectsService.ctorParameters = function () { return [
        { type: _angular_common_http__WEBPACK_IMPORTED_MODULE_3__["HttpClient"] }
    ]; };
    ProjectsService = tslib__WEBPACK_IMPORTED_MODULE_0__["__decorate"]([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_2__["Injectable"])()
    ], ProjectsService);
    return ProjectsService;
}());



/***/ }),

/***/ 0:
/*!***************************!*\
  !*** multi ./src/main.ts ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(/*! /home/dneumann/Repositories/sprincl/vispr_vnext/frontend/src/main.ts */"./src/main.ts");


/***/ })

},[[0,"runtime","vendor"]]]);
//# sourceMappingURL=main.js.map