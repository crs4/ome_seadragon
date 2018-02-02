AnnotationsEventsController.FREEHAND_DRAWING_TOOL_PLUS = 'freehand_drawer_plus';

AnnotationsEventsController.prototype.initializeFreehandDrawingToolPlus = function(path_config, switch_on_id, label_prefix) {
    // by default, initialize dummy tool
    this.initializeDummyTool();

    if(!(AnnotationsEventsController.FREEHAND_DRAWING_TOOL_PLUS in this.initialized_tools)) {

        this.annotation_controller.tmp_freehand_plus_path = undefined;
        this.annotation_controller.tmp_path_plus_id = 'tmp_freehand_plus_path';
        this.annotation_controller.path_plus_config = path_config;
        this.annotation_controller.fhp_label_prefix = (typeof label_prefix === 'undefined') ? 'polygon' : label_prefix;
        this.annotation_controller.tmp_shape_history = undefined;

        this.annotation_controller.updateFHPlusPathConfig = function (path_config) {
            this.path_plus_config = path_config;
        };

        this.annotation_controller.extendFHPlusPathConfig = function (path_config) {
            this.path_plus_config = $.extend({}, this.path_plus_config, path_config);
        };

        this.annotation_controller.setFHPlusPathLabelPrefix = function (label_prefix) {
            if (typeof label_prefix !== 'undefined') {
                this.fhp_label_prefix = label_prefix;
            }
        };

        this.annotation_controller.freehandPlusShapeExists = function () {
            return typeof this.tmp_freehand_plus_path !== 'undefined';
        };

        this.annotation_controller._setCheckpoint = function () {
            var shape_json = this.getShapeJSON(this.tmp_path_plus_id);
            // remove last point from the shape, it was not included in the previous version of the polygon
            shape_json.segments.pop();
            this.tmp_shape_history.push(JSON.stringify(shape_json));
        };

        this.annotation_controller.shapeHistoryExist = function () {
            return (typeof this.tmp_shape_history !== 'undefined') && (this.tmp_shape_history.length > 0);
        };

        this.annotation_controller.rollbackFreehandPathPlus = function() {
            this.deleteShape(this.tmp_path_plus_id, false);
            var stop_rollback = false;
            if (this.shapeHistoryExist()) {
                var prev_shape_json = JSON.parse(this.tmp_shape_history.pop());
                this.drawShapeFromJSON(prev_shape_json, false);
                this.tmp_freehand_plus_path = this.getShape(this.tmp_path_plus_id);
                this.selectShape(this.tmp_path_plus_id);
            } else {
                this.clearTemporaryFreehandPlus();
                stop_rollback = true;
            }
            this.refreshView();
            return stop_rollback;
        };

        this.annotation_controller._initShape = function(x, y, trigger_label) {
            this.selectShape(this.tmp_path_plus_id);
            this.tmp_freehand_plus_path = this.getShape(this.tmp_path_plus_id);
            this.tmp_freehand_plus_path.addPoint(x, y);
            $("#" + this.canvas_id).trigger(trigger_label, [{'x': x, 'y': y}]);
            this.refreshView();
        };

        this.annotation_controller.createFreehandPlusPath = function (x, y) {
            // initialize shape's history
            this.tmp_shape_history = [];
            this.drawPolygon(this.tmp_path_plus_id, [], undefined, this.path_plus_config, false);
            this._initShape(x, y, 'freehand_polygon_plus_created');
        };

        this.annotation_controller.continueFreehandPlusPath = function (x, y) {
            this._initShape(x, y, 'freehand_polygon_plus_updated');
        };

        this.annotation_controller.addPointToFreehandPathPlus = function (x, y) {
            this.tmp_freehand_plus_path.addPoint(x, y);
            this.refreshView();
        };

        this.annotation_controller.pauseFreehandPathPlus = function () {
            this._setCheckpoint();
            $("#" + this.canvas_id).trigger('freehand_polygon_plus_paused');
        };

        this.annotation_controller.saveTemporaryFreehandPathPlus = function () {
            this.tmp_freehand_plus_path.simplifyPath(this.x_offset, this.y_offset);
            var tmp_path_json = this.getShapeJSON(this.tmp_path_plus_id);
            this.deleteShape(this.tmp_path_plus_id, false);
            tmp_path_json.shape_id = this.getFirstAvailableLabel(this.fhp_label_prefix);
            this.drawShapeFromJSON(tmp_path_json, true);
            this.tmp_freehand_plus_path =undefined;
            this.tmp_shape_history = undefined;
            $("#" + this.canvas_id).trigger('freehand_polygon_plus_saved', [tmp_path_json.shape_id]);
        };

        this.annotation_controller.clearTemporaryFreehandPlus = function () {
            if (typeof this.tmp_freehand_plus_path !== 'undefined') {
                this.deleteShape(this.tmp_path_plus_id);
                this.tmp_freehand_plus_path = undefined;
                this.tmp_shape_history = undefined;
                $("#" + this.canvas_id).trigger('freehand_polygon_plus_cleared');
            }
        };

        var freehand_drawing_tool_plus = new paper.Tool();

        freehand_drawing_tool_plus.annotations_controller = this.annotation_controller;

        freehand_drawing_tool_plus.onMouseDown = function (event) {
            if (this.annotations_controller.freehandPlusShapeExists()) {
                this.annotations_controller.continueFreehandPlusPath(event.point.x, event.point.y);
            } else {
                this.annotations_controller.createFreehandPlusPath(event.point.x, event.point.y);
            }
        };

        freehand_drawing_tool_plus.onMouseDrag = function (event) {
            this.annotations_controller.addPointToFreehandPathPlus(event.point.x, event.point.y);
        };

        freehand_drawing_tool_plus.onMouseUp = function() {
            this.annotations_controller.pauseFreehandPathPlus();
        };

        this.initialized_tools[AnnotationsEventsController.FREEHAND_DRAWING_TOOL_PLUS] = freehand_drawing_tool_plus;

        if (typeof switch_on_id !== 'undefined') {
            this._bind_switch(switch_on_id, AnnotationsEventsController.FREEHAND_DRAWING_TOOL_PLUS);
        }

    } else {
        console.warn('Tool"' + AnnotationsEventsController.FREEHAND_DRAWING_TOOL_PLUS + '" already initialized');
    }
};