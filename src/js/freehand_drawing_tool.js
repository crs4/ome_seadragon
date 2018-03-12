AnnotationsEventsController.FREEHAND_DRAWING_TOOL = 'freehand_drawer';

AnnotationsEventsController.prototype.initializeFreehandDrawingTool = function(path_config, switch_on_id, label_prefix) {
    // by default, initialize dummy tool
    this.initializeDummyTool();

    if(!(AnnotationsEventsController.FREEHAND_DRAWING_TOOL in this.initialized_tools)) {

        this.annotation_controller.tmp_freehand_path = undefined;
        this.annotation_controller.tmp_path_id = 'tmp_freehand_path';
        this.annotation_controller.path_config = path_config;
        this.annotation_controller.label_prefix = (typeof label_prefix === 'undefined') ? 'polygon' : label_prefix;
        this.annotation_controller.tmp_shape_undo_history = undefined;
        this.annotation_controller.tmp_shape_redo_history = undefined;
        this.annotation_controller.preview_mode_on = false;
        this.annotation_controller.shape_updated_by_preview = false;

        this.annotation_controller.updatePathConfig = function (path_config) {
            this.path_config = path_config;
        };

        this.annotation_controller.extendPathConfig = function (path_config) {
            this.path_config = $.extend({}, this.path_config, path_config);
        };

        this.annotation_controller.setFreehandPathLabelPrefix = function (label_prefix) {
            if (typeof label_prefix !== 'undefined') {
                this.label_prefix = label_prefix;
            }
        };

        this.annotation_controller.replaceLastFreehandPathPoint = function (event) {
            this.tmp_freehand_path.removePoint();
            this.addPointToFreehandPath(event.point.x, event.point.y);
        };

        this.annotation_controller.freehandShapeExists = function () {
            return typeof this.tmp_freehand_path !== 'undefined';
        };

        this.annotation_controller.activatePreviewMode = function () {
            this.preview_mode_on = true;
        };

        this.annotation_controller.deactivatePreviewMode = function () {
            this.preview_mode_on = false;
            this.tmp_freehand_path.closePath();
            this.tmp_freehand_path.disableDashedBorder();
        };

        this.annotation_controller.previewModeActive = function () {
            return this.preview_mode_on;
        };

        this.annotation_controller.tmpFreehandPathExists = function () {
            return typeof this.tmp_freehand_path !== 'undefined';
        };

        this.annotation_controller.tmpFreehandPathValid = function() {
            if (this.tmpFreehandPathExists()) {
                return this.tmp_freehand_path.isValid();
            } else {
                return false;
            }
        };

        this.annotation_controller._setFreehandPathUndoCheckpoint = function (remove_last_point) {
            var shape_json = this.getShapeJSON(this.tmp_path_id);
            // remove last point from the shape, it was not included in the previous version of the polygon
            if (remove_last_point) {
                shape_json.segments.pop();
            }
            this.tmp_shape_undo_history.push(JSON.stringify(shape_json));
        };

        this.annotation_controller._setFreehandPathRedoCheckpoint = function () {
            var shape_json = this.getShapeJSON(this.tmp_path_id);
            this.tmp_shape_redo_history.push(JSON.stringify(shape_json));
        };

        this.annotation_controller.shapeUndoHistoryExists = function () {
            return (typeof this.tmp_shape_undo_history !== 'undefined') && (this.tmp_shape_undo_history.length > 0);
        };

        this.annotation_controller.shapeRedoHistoryExists = function () {
            return (typeof this.tmp_shape_redo_history !== 'undefined') && (this.tmp_shape_redo_history.length > 0);
        };

        this.annotation_controller.rollbackFreehandPath = function () {
            if (this.tmpFreehandPathExists()) {
                this._setFreehandPathRedoCheckpoint();
                this.deleteShape(this.tmp_path_id, false);
                if (this.shapeUndoHistoryExists()) {
                    var shape_json = JSON.parse(this.tmp_shape_undo_history.pop());
                    this.drawShapeFromJSON(shape_json, true);
                    this.tmp_freehand_path = this.getShape(this.tmp_path_id);
                    this.selectShape(this.tmp_path_id);
                } else {
                    this.tmp_freehand_path = undefined;
                    this.refreshView();
                }
            }
        };

        this.annotation_controller.restoreFreehandPath = function() {
            if (this.shapeRedoHistoryExists()) {
                if (this.tmpFreehandPathExists()) {
                    this._setFreehandPathUndoCheckpoint(false);
                }
                this.deleteShape(this.tmp_path_id, false);
                var shape_json = JSON.parse(this.tmp_shape_redo_history.pop());
                this.drawShapeFromJSON(shape_json, true);
                this.tmp_freehand_path = this.getShape(this.tmp_path_id);
                this.selectShape(this.tmp_path_id);
            }
        };

        this.annotation_controller._initShape = function (x, y, trigger_label) {
            this.selectShape(this.tmp_path_id);
            this.tmp_freehand_path = this.getShape(this.tmp_path_id);
            this.tmp_freehand_path.addPoint(x, y);
            $("#" + this.canvas_id).trigger(trigger_label, [{'x': x, 'y': y}]);
            this.refreshView();
        };

        this.annotation_controller.createFreehandPath = function (x, y) {
            // initialize shape's history
            this.tmp_shape_undo_history = [];
            this.tmp_shape_redo_history = [];
            this.drawPolygon(this.tmp_path_id, [], undefined, this.path_config, false);
            this._initShape(x, y, 'freehand_polygon_created');
        };

        this.annotation_controller.continueFreehandPath = function (x, y) {
            this._initShape(x, y, 'freehand_polygon_updated');
        };

        this.annotation_controller.addPointToFreehandPath = function (x, y) {
            this.tmp_freehand_path.addPoint(x, y);
            this.refreshView();
        };

        this.annotation_controller.pauseFreehandPath = function () {
            $("#" + this.canvas_id).trigger('freehand_polygon_paused', this.tmp_path_id);
        };

        this.annotation_controller.saveTemporaryFreehandPath = function () {
            this.tmp_freehand_path.simplifyPath(this.x_offset, this.y_offset);
            var tmp_path_json = this.getShapeJSON(this.tmp_path_id);
            this.deleteShape(this.tmp_path_id, false);
            tmp_path_json.shape_id = this.getFirstAvailableLabel(this.label_prefix);
            this.drawShapeFromJSON(tmp_path_json, true);
            this.tmp_freehand_path =undefined;
            this.tmp_shape_undo_history = undefined;
            this.tmp_shape_redo_history = undefined;
            this.preview_mode_on = false;
            $("#" + this.canvas_id).trigger('freehand_polygon_saved', [tmp_path_json.shape_id]);
        };

        this.annotation_controller.clearTemporaryFreehandPath = function () {
            if (typeof this.tmp_freehand_path !== 'undefined') {
                this.deleteShape(this.tmp_path_id);
                this.tmp_freehand_path = undefined;
                this.tmp_shape_undo_history = undefined;
                this.tmp_shape_redo_history = undefined;
                this.preview_mode_on = false;
                $("#" + this.canvas_id).trigger('freehand_polygon_cleared');
            }
        };

        var freehand_drawing_tool = new paper.Tool();

        freehand_drawing_tool.annotations_controller = this.annotation_controller;

        freehand_drawing_tool.onMouseDown = function (event) {
            if (this.annotations_controller.freehandShapeExists()) {
                this.annotations_controller._setFreehandPathUndoCheckpoint(true);
                // creating a "new" path will delete the redo history
                this.annotations_controller.tmp_shape_redo_history = [];
                this.annotations_controller.deactivatePreviewMode();
                this.annotations_controller.continueFreehandPath(event.point.x, event.point.y);
            } else {
                this.annotations_controller.createFreehandPath(event.point.x, event.point.y);
            }
            this.annotations_controller.shape_updated_by_preview = false;
        };

        freehand_drawing_tool.onMouseDrag = function (event) {
            this.annotations_controller.addPointToFreehandPath(event.point.x, event.point.y);
        };

        freehand_drawing_tool.onMouseUp = function () {
            this.annotations_controller.pauseFreehandPath();
        };

        freehand_drawing_tool.onMouseMove = function (event) {
            // check if preview mode is active and if the mouse is moving over the canvas
            if (this.annotations_controller.previewModeActive() &&
                this.annotations_controller.tmpFreehandPathExists() &&
                $("#" + this.annotations_controller.canvas_id).is(':hover')) {
                if (this.annotations_controller.shape_updated_by_preview) {
                    this.annotations_controller.replaceLastFreehandPathPoint(event);
                } else {
                    this.annotations_controller.addPointToFreehandPath(event.point.x, event.point.y);
                    this.annotations_controller.shape_updated_by_preview = true;
                }
            }
        };

        var canvasMouseEnter = function (event) {
            var annotation_controller = event.data.annotation_controller;
            if (annotation_controller.previewModeActive() && annotation_controller.tmpFreehandPathExists()) {
                annotation_controller.tmp_freehand_path.openPath();
                annotation_controller.tmp_freehand_path.deselect();
                annotation_controller.tmp_freehand_path.enableDashedBorder(100, 50);
            }
        };

        var canvasMouseLeave = function (event) {
            var annotation_controller = event.data.annotation_controller;
            if (annotation_controller.previewModeActive() && annotation_controller.tmpFreehandPathExists()) {
                annotation_controller.tmp_freehand_path.removePoint();
                annotation_controller.tmp_freehand_path.closePath();
                annotation_controller.tmp_freehand_path.select();
                annotation_controller.tmp_freehand_path.disableDashedBorder();
                annotation_controller.shape_updated_by_preview = false;
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

        this.initialized_tools[AnnotationsEventsController.FREEHAND_DRAWING_TOOL] = freehand_drawing_tool;

        if (typeof switch_on_id !== 'undefined') {
            this._bind_switch(switch_on_id, AnnotationsEventsController.FREEHAND_DRAWING_TOOL);
        }

    } else {
        console.warn('Tool"' + AnnotationsEventsController.FREEHAND_DRAWING_TOOL + '" already initialized');
    }
};