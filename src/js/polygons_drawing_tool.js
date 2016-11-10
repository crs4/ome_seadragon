AnnotationsEventsController.POLYGON_DRAWING_TOOL = 'polygon_drawer';

AnnotationsEventsController.prototype.initializePolygonDrawingTool = function (polygon_config, 
                                                                               switch_on_id, save_figure_id) {
    // by default, initialize dummy tool
    this.initializeDummyTool();

    if (!(AnnotationsEventsController.POLYGON_DRAWING_TOOL in this.initialized_tools)) {

        this.annotation_controller.tmp_polygon = undefined;
        this.annotation_controller.tmp_polygon_id = 'tmp_polygon';
        this.annotation_controller.polygon_config = polygon_config;

        this.annotation_controller.updatePolygonConfig = function (polygon_config) {
            this.polygon_config = polygon_config;
        };

        this.annotation_controller.extendPolygonConfig = function (polygon_config) {
            this.polygon_config = $.extend({}, this.polygon_config, polygon_config);
        };

        this.annotation_controller._pointToPolygon = function (x, y) {
            var trigger_label = undefined;
            if (this.tmp_polygon) {
                this.tmp_polygon.addPoint(x, y);
                trigger_label = 'polygon_add_point';
            } else {
                this.drawPolygon(this.tmp_polygon_id, [], undefined,
                    this.polygon_config, false);
                this.selectShape(this.tmp_polygon_id);
                this.tmp_polygon = this.getShape(this.tmp_polygon_id);
                this.tmp_polygon.addPoint(x, y);
                trigger_label = 'polygon_created';
            }
            this.refreshView();
            $("#" + this.canvas_id).trigger(trigger_label, [{'x': x, 'y': y}]);
        };

        this.annotation_controller.addPointToPolygon = function (event) {
            this._pointToPolygon(event.point.x, event.point.y);
        };

        this.annotation_controller.replaceLastPolygonPoint = function (event) {
            this.tmp_polygon.removePoint();
            this.addPointToPolygon(event);
        };

        this.annotation_controller.removeLastPolygonPoint = function () {
            try {
                this.tmp_polygon.removePoint();
                this.refreshView();
            } catch (err) {
                this.clearTemporaryPolygon();
            }
        };

        this.annotation_controller.clearTemporaryPolygon = function () {
            if (typeof this.tmp_polygon !== 'undefined') {
                this.deleteShape(this.tmp_polygon_id);
                this.tmp_polygon = undefined;
                $('#' + this.canvas_id).trigger('polygon_cleared');
            }
        };

        this.annotation_controller.saveTemporaryPolygon = function (label_prefix) {
            var tmp_polygon_json = this.getShapeJSON(this.tmp_polygon_id);
            this.deleteShape(this.tmp_polygon_id, false);
            var polygon_label_prefix = (typeof label_prefix === 'undefined') ? 'polygon' : label_prefix;
            tmp_polygon_json.shape_id = this._getShapeId(polygon_label_prefix);
            // apply translation
            var ac = this;
            tmp_polygon_json.segments = $.map(tmp_polygon_json.segments, function (segment) {
                return {
                    'point': {
                        'x': segment.point.x + ac.x_offset,
                        'y': segment.point.y + ac.y_offset
                    }
                }
            });
            this.drawShapeFromJSON(tmp_polygon_json, true);
            this.tmp_polygon = undefined;
            $("#" + this.canvas_id).trigger('polygon_saved', [tmp_polygon_json.shape_id]);
        };

        var polygon_drawing_tool = new paper.Tool();

        polygon_drawing_tool.annotations_controller = this.annotation_controller;

        polygon_drawing_tool.onMouseDown = function (event) {
            this.annotations_controller.addPointToPolygon(event);
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
