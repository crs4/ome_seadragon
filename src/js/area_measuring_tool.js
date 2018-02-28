AnnotationsEventsController.AREA_MEASURING_TOOL = 'area_measuring_tool';

AnnotationsEventsController.prototype.initializeAreaMeasuringTool = function(path_config) {
    //by default, initialize dummy tool
    this.initializeDummyTool();

    if (!(AnnotationsEventsController.AREA_MEASURING_TOOL in this.initialized_tools)) {

        this.annotation_controller.area_ruler = undefined;
        this.annotation_controller.area_ruler_id = 'tmp_area_ruler';
        this.annotation_controller.area_ruler_config =
            (typeof path_config === 'undefined') ? {} : path_config;
        this.annotation_controller.tmp_area_ruler_history = undefined;
        this.annotation_controller.area_ruler_preview_mode_on = false;
        this.annotation_controller.area_ruler_updated_by_preview = false;

        this.annotation_controller.area_ruler_out_id = undefined;
        this.annotation_controller.area_ruler_binding_shape_id = undefined;

        this.annotation_controller.updateAreaRulerConfig = function (ruler_config) {
            this.area_ruler_config = ruler_config;
        };

        this.annotation_controller.extendAreaRulerConfig = function (ruler_config) {
            this.area_ruler_config = $.extend({}, this.area_ruler_config, ruler_config);
        };

        this.annotation_controller.tmpAreaRulerExists = function () {
            return typeof this.area_ruler !== 'undefined';
        };

        this.annotation_controller.replaceLastAreaRulerPoint = function (event) {
            this.area_ruler.removePoint();
            this.addPointToAreaRuler(event.point.x, event.point.y);
        };

        this.annotation_controller.activateAreaRulerPreviewMode = function () {
            this.area_ruler_preview_mode_on = true;
        };

        this.annotation_controller.deactivateAreaRulerPreviewMode = function () {
            this.area_ruler_preview_mode_on = false;
            this.area_ruler.closePath();
            this.area_ruler.disableDashedBorder();
        };

        this.annotation_controller.areaRulerPreviewModeActive = function () {
            return this.area_ruler_preview_mode_on;
        };

        this.annotation_controller._setAreaRulerCheckpoint = function () {
            var shape_json = this.getShapeJSON(this.area_ruler_id);
            shape_json.segments.pop();
            this.tmp_area_ruler_history.push(JSON.stringify(shape_json));
        };

        this.annotation_controller.areaRulerHistoryExists = function () {
            return (typeof this.tmp_area_ruler_history !== 'undefined') && (this.tmp_area_ruler_history.length > 0);
        };

        this.annotation_controller.rollbackAreaRulerPath = function () {
            this.deleteShape(this.area_ruler_id, false);
            var stop_rollback = false;
            if (this.areaRulerHistoryExists()) {
                var prev_shape_json = JSON.parse(this.tmp_area_ruler_history.pop());
                this.drawShapeFromJSON(prev_shape_json, false);
                this.area_ruler = this.getShape(this.area_ruler_id);
                this.selectShape(this.area_ruler_id);
            } else {
                this.clearAreaRuler();
                stop_rollback = true;
            }
            this.refreshView();
            return stop_rollback;
        };

        this.annotation_controller._initAreaRuler = function (x, y, trigger_label) {
            this.selectShape(this.area_ruler_id);
            this.area_ruler = this.getShape(this.area_ruler_id);
            this.area_ruler.addPoint(x, y);
            $("#" +this.canvas_id).trigger(trigger_label, [{'x': x, 'y': y}]);
            this.refreshView();
        };

        this.annotation_controller.createAreaRulerPath = function (x, y) {
            this.tmp_area_ruler_history = [];
            this.drawPolygon(this.area_ruler_id, [], undefined, this.area_ruler_config, false);
            this._initAreaRuler(x, y, 'area_ruler_created');
        };

        this.annotation_controller.continueAreaRulerPath = function (x, y) {
            this._initAreaRuler(x, y, 'area_ruler_updated');
        };

        this.annotation_controller.addPointToAreaRuler = function (x, y) {
            this.area_ruler.addPoint(x, y);
            this.refreshView();
        };

        this.annotation_controller.pauseAreaRuler = function () {
            $("#" + this.area_ruler_out_id).trigger('area_ruler_paused', this.area_ruler_id);
        };

        this.annotation_controller.saveAreaRuler = function () {
            this.serializeAreaRuler();
            this.updateAreaRulerOutputField();
            this.clearAreaRuler(true);
        };

        this.annotation_controller.clearAreaRuler = function (ruler_saved) {
            if (typeof this.area_ruler !== 'undefined') {
                this.deleteShape(this.area_ruler_id);
                this.area_ruler_id = undefined;
                this.tmp_area_ruler_history = undefined;
                this.area_ruler_preview_mode_on = false;
                this.area_ruler = undefined;
            }
            $("#" + this.area_ruler_out_id).trigger('area_ruler_cleared', [ruler_saved]);
        };

        this.annotation_controller.adaptRulerToShape = function () {
            var binding_shape = this.getShape(this.area_ruler_binding_shape_id);
            if (
                this.area_ruler.intersectsShape(binding_shape) === true ||
                this.area_ruler.containsShape(binding_shape) ||
                binding_shape.containsShape(this.area_ruler)
            ) {
                this.intersectShapes(this.area_ruler, binding_shape, true, false, true, true);
                this.area_ruler = this.getShape(this.area_ruler_id);
            } else {
                this.deleteShape(this.area_ruler_id);
                this.area_ruler = undefined;
                $("#" + this.area_ruler_out_id).trigger('area_ruler_empty_intersection');
            }
        };

        this.annotation_controller.getAreaRulerMeasure = function (decimal_digits) {
            if (typeof this.area_ruler !== 'undefined') {
                return this.area_ruler.getArea(this.image_mpp, decimal_digits);
            }
        };

        this.annotation_controller.serializeAreaRuler = function () {
            this.area_ruler.simplifyPath();
            // check if ruler needs to be adapted to a given shape
            if (typeof this.area_ruler_binding_shape_id !== 'undefined') {
                this.adaptRulerToShape();
            }
            // check if there is still an intersection
            if (typeof this.area_ruler !== 'undefined') {
                // serialize ruler in output field's data
                var $ruler_out = $("#" + this.area_ruler_out_id);
                var ruler_json = this.getShapeJSON(this.area_ruler_id);
                ruler_json.shape_id = this.getFirstAvailableLabel('area_ruler');
                $ruler_out.data('ruler_json', ruler_json);
            }
        };

        this.annotation_controller.updateAreaRulerOutputField = function () {
            var measure = this.getAreaRulerMeasure();
            var $ruler_out = $("#" + this.area_ruler_out_id);
            $ruler_out.data('measure', measure)
                .trigger('area_ruler_updated');
        };

        var aec = this;
        this.annotation_controller.bindToAreaRuler = function (switch_on_id, output_id) {
            if (typeof output_id === 'undefined') {
                throw new Error('Missing mandatory output element');
            }
            aec._bind_switch(switch_on_id, AnnotationsEventsController.AREA_MEASURING_TOOL);
            $("#" + switch_on_id).bind(
                'click',
                {'annotation_controller': this},
                function(event) {
                    event.data.annotation_controller.area_ruler_out_id = output_id;
                    $("#" + output_id).trigger('start_new_area_ruler');
                }
            );
        };

        this.annotation_controller.bindAreaRulerToShape = function(shape_id) {
            this.area_ruler_binding_shape_id = shape_id;
        };

        var area_ruler_tool = new paper.Tool();

        area_ruler_tool.annotations_controller = this.annotation_controller;

        area_ruler_tool.onMouseDown = function (event) {
            if (this.annotations_controller.tmpAreaRulerExists()) {
                this.annotations_controller._setAreaRulerCheckpoint();
                this.annotations_controller.deactivateAreaRulerPreviewMode();
                this.annotations_controller.continueAreaRulerPath(event.point.x, event.point.y);
            } else {
                this.annotations_controller.createAreaRulerPath(event.point.x, event.point.y);
            }
            this.annotations_controller.area_ruler_updated_by_preview = false;
        };

        area_ruler_tool.onMouseDrag = function (event) {
            this.annotations_controller.addPointToAreaRuler(event.point.x, event.point.y);
        };

        area_ruler_tool.onMouseUp = function () {
            this.annotations_controller.pauseAreaRuler();
        };

        area_ruler_tool.onMouseMove = function (event) {
            if (this.annotations_controller.areaRulerPreviewModeActive() &&
                $("#" + this.annotations_controller.canvas_id).is(':hover')) {
                if (this.annotations_controller.area_ruler_updated_by_preview) {
                    this.annotations_controller.replaceLastAreaRulerPoint(event);
                } else {
                    this.annotations_controller.addPointToAreaRuler(event.point.x, event.point.y);
                    this.annotations_controller.area_ruler_updated_by_preview = true;
                }
            }
        };

        var canvasMouseEnter = function (event) {
            var annotation_controller = event.data.annotation_controller;
            if (annotation_controller.areaRulerPreviewModeActive()) {
                annotation_controller.area_ruler.openPath();
                annotation_controller.area_ruler.deselect();
                annotation_controller.area_ruler.enableDashedBorder(100, 50);
            }
        };

        var canvasMouseLeave = function (event) {
            var annotation_controller = event.data.annotation_controller;
            if (annotation_controller.areaRulerPreviewModeActive()) {
                annotation_controller.area_ruler.removePoint();
                annotation_controller.area_ruler.closePath();
                annotation_controller.area_ruler.select();
                annotation_controller.area_ruler.disableDashedBorder();
                annotation_controller.area_ruler_updated_by_preview = false;
            }
        };

        $("#" + this.annotation_controller.canvas_id)
            .mouseenter(
                { annotation_controller: this.annotation_controller },
                canvasMouseEnter
            )
            .mouseleave(
                { annotation_controller: this.annotation_controller },
                canvasMouseLeave
            );

        this.initialized_tools[AnnotationsEventsController.AREA_MEASURING_TOOL] = area_ruler_tool;

    } else {
        console.warn('Tool "' + AnnotationsEventsController.AREA_MEASURING_TOOL + '" already initialized');
    }
};