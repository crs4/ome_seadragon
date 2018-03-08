AnnotationsEventsController.POLYGON_DRAWING_TOOL = 'polygon_drawer';

AnnotationsEventsController.prototype.initializePolygonDrawingTool = function (polygon_config, 
                                                                               switch_on_id, save_figure_id) {
    // by default, initialize dummy tool
    this.initializeDummyTool();

    if (!(AnnotationsEventsController.POLYGON_DRAWING_TOOL in this.initialized_tools)) {

        this.annotation_controller.tmp_polygon = undefined;
        this.annotation_controller.tmp_polygon_id = 'tmp_polygon';
        this.annotation_controller.polygon_config = polygon_config;
        this.annotation_controller.tmp_polygon_redo_history = undefined;

        this.annotation_controller.updatePolygonConfig = function (polygon_config) {
            this.polygon_config = polygon_config;
        };

        this.annotation_controller.extendPolygonConfig = function (polygon_config) {
            this.polygon_config = $.extend({}, this.polygon_config, polygon_config);
        };

        this.annotation_controller._pointToPolygon = function (x, y, redo) {
            var trigger_label = undefined;
            if (this.tmp_polygon) {
                this.tmp_polygon.addPoint(x, y);
                if (!redo) {
                    trigger_label = 'polygon_add_point';
                } else {
                    trigger_label = 'polygon_redo';
                }
            } else {
                this.drawPolygon(this.tmp_polygon_id, [], undefined,
                    this.polygon_config, false);
                this.selectShape(this.tmp_polygon_id);
                this.tmp_polygon = this.getShape(this.tmp_polygon_id);
                this.tmp_polygon.addPoint(x, y);
                if (!redo) {
                    trigger_label = 'polygon_created';
                } else {
                    trigger_label = 'polygon_restored';
                }
            }
            this.refreshView();
            $("#" + this.canvas_id).trigger(trigger_label, [{'x': x, 'y': y}]);
        };

        this.annotation_controller._setPolygonRedoCheckpoint = function (point) {
            this.tmp_polygon_redo_history.push(point);
        };

        this.annotation_controller.polygonRedoHistoryExists = function () {
            return (typeof this.tmp_polygon_redo_history !== 'undefined') && (this.tmp_polygon_redo_history.length > 0);
        };

        this.annotation_controller.temporaryPolygonExists = function () {
            return typeof this.tmp_polygon !== 'undefined';
        };

        this.annotation_controller._removeLastPolygonPoint = function (clear_tmp_polygon) {
            try {
                var removed_point = this.tmp_polygon.removePoint();
                this.refreshView();
                return removed_point;
            } catch (err) {
                if (clear_tmp_polygon) {
                    this.clearTemporaryPolygon();
                } else {
                    return undefined;
                }
            }
        };

        this.annotation_controller.rollbackPolygon = function () {
            if (this.temporaryPolygonExists()) {
                var removed_point = this._removeLastPolygonPoint(false);
                if (typeof removed_point !== 'undefined') {
                    this._setPolygonRedoCheckpoint(removed_point);
                }
                if  (this.tmp_polygon.isEmpty()) {
                    this.deleteShape(this.tmp_polygon_id);
                    this.tmp_polygon = undefined;
                }
            }
        };

        this.annotation_controller.restorePolygon = function () {
            if (this.polygonRedoHistoryExists()) {
                var to_be_restored = this.tmp_polygon_redo_history.pop();
                this._pointToPolygon(to_be_restored.x, to_be_restored.y, true);
            }
        };

        this.annotation_controller.addPointToPolygon = function (x, y) {
            this._pointToPolygon(x, y, false);
        };

        this.annotation_controller.replaceLastPolygonPoint = function (event) {
            this.tmp_polygon.removePoint();
            this.addPointToPolygon(event.point.x, event.point.y);
        };

        this.annotation_controller.clearTemporaryPolygon = function () {
            if (typeof this.tmp_polygon !== 'undefined') {
                this.deleteShape(this.tmp_polygon_id);
                this.tmp_polygon = undefined;
                this.tmp_polygon_redo_history = undefined;
                $('#' + this.canvas_id).trigger('polygon_cleared');
            }
        };

        this.annotation_controller.saveTemporaryPolygon = function (label_prefix) {
            var tmp_polygon_json = this.getShapeJSON(this.tmp_polygon_id);
            this.deleteShape(this.tmp_polygon_id, false);
            var polygon_label_prefix = (typeof label_prefix === 'undefined') ? 'polygon' : label_prefix;
            tmp_polygon_json.shape_id = this.getFirstAvailableLabel(polygon_label_prefix);
            this.drawShapeFromJSON(tmp_polygon_json, true);
            this.tmp_polygon = undefined;
            this.tmp_polygon_redo_history = undefined;
            $("#" + this.canvas_id).trigger('polygon_saved', [tmp_polygon_json.shape_id]);
        };

        var polygon_drawing_tool = new paper.Tool();

        polygon_drawing_tool.annotations_controller = this.annotation_controller;

        polygon_drawing_tool.onMouseDown = function (event) {
            this.annotations_controller.tmp_polygon_redo_history = [];
            this.annotations_controller.addPointToPolygon(event.point.x, event.point.y);
        };

        polygon_drawing_tool.onMouseDrag = function (event) {
            this.annotations_controller.replaceLastPolygonPoint(event);
        };

        this.initialized_tools[AnnotationsEventsController.POLYGON_DRAWING_TOOL] = polygon_drawing_tool;

        if (typeof switch_on_id !== 'undefined') {
            this._bind_switch(switch_on_id, AnnotationsEventsController.POLYGON_DRAWING_TOOL);
        }

        // if a "switch off" element is provided, bind it to the save polygon action
        if (typeof save_figure_id !== 'undefined') {
            $("#" + save_figure_id).bind(
                'click',
                {'annotation_controller': this.annotation_controller},
                function (event) {
                    event.data.annotation_controller.saveTemporaryPolygon();
                }
            );
        }
    } else {
        console.warn('Tool"' + AnnotationsEventsController.POLYGON_DRAWING_TOOL + '" already initialized');
    }
};
