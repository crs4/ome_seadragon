AnnotationsEventsController.FREEHAND_DRAWING_TOOL = 'freehand_drawer';

AnnotationsEventsController.prototype.initializeFreehandDrawingTool = function(path_config, switch_on_id, label_prefix) {
    //by default, initialize dummy tool
    this.initializeDummyTool();

    if (!(AnnotationsEventsController.FREEHAND_DRAWING_TOOL in this.initialized_tools)) {

        this.annotation_controller.tmp_freehand_path = undefined;
        this.annotation_controller.tmp_path_id = 'tmp_freehand_path';
        this.annotation_controller.path_config = path_config;
        this.annotation_controller.label_prefix = (typeof label_prefix === 'undefined') ? 'polygon' : label_prefix;

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

        this.annotation_controller.createFreehandPath = function (x, y) {
            this.drawPolygon(this.tmp_path_id, [], undefined,
                this.path_config, false);
            this.selectShape(this.tmp_path_id);
            this.tmp_freehand_path = this.getShape(this.tmp_path_id);
            this.tmp_freehand_path.addPoint(x, y);
            $("#" + this.canvas_id).trigger('freehand_polygon_created', [{'x': x, 'y': y}]);
            this.refreshView();
        };

        this.annotation_controller.addPointToFreehandPath = function (x, y) {
            this.tmp_freehand_path.addPoint(x, y);
            this.refreshView();
        };

        this.annotation_controller.clearTemporaryFreehandPath = function () {
            if (typeof this.tmp_freehand_path !== 'undefined') {
                this.deleteShape(this.tmp_path_id);
                this.tmp_freehand_path = undefined;
                $("#" + this.canvas_id).trigger('freehand_polygon_deleted');
            }
        };

        this.annotation_controller.saveTemporaryFreehandPath = function () {
            this.tmp_freehand_path.simplifyPath(this.x_offset, this.y_offset);
            var tmp_path_json = this.getShapeJSON(this.tmp_path_id);
            this.deleteShape(this.tmp_path_id, false);
            tmp_path_json.shape_id = this.getFirstAvailableLabel(this.label_prefix);
            this.drawShapeFromJSON(tmp_path_json, true);
            this.tmp_freehand_path = undefined;
            $("#" + this.canvas_id).trigger('freehand_polygon_saved', [tmp_path_json.shape_id]);
        };

        var freehand_drawing_tool = new paper.Tool();

        freehand_drawing_tool.annotations_controller = this.annotation_controller;

        freehand_drawing_tool.onMouseDown = function (event) {
            this.annotations_controller.createFreehandPath(event.point.x, event.point.y);
        };

        freehand_drawing_tool.onMouseDrag = function (event) {
            this.annotations_controller.addPointToFreehandPath(event.point.x, event.point.y);
        };

        freehand_drawing_tool.onMouseUp = function () {
            this.annotations_controller.saveTemporaryFreehandPath();
        };

        this.initialized_tools[AnnotationsEventsController.FREEHAND_DRAWING_TOOL] = freehand_drawing_tool;

        if (typeof switch_on_id !== 'undefined') {
            this._bind_switch(switch_on_id, AnnotationsEventsController.FREEHAND_DRAWING_TOOL);
        }

    } else {
        console.warn('Tool"' + AnnotationsEventsController.FREEHAND_DRAWING_TOOL + '" already initialized');
    }
};