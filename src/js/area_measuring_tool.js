AnnotationsEventsController.AREA_MEASURING_TOOL = 'area_measuring_tool';

AnnotationsEventsController.prototype.initializeAreaMeasuringTool = function(path_config) {
    //by default, initialize dummy tool
    this.initializeDummyTool();

    if (!(AnnotationsEventsController.AREA_MEASURING_TOOL in this.initialized_tools)) {

        this.annotation_controller.area_ruler = undefined;
        this.annotation_controller.area_ruler_id = 'tmp_area_ruler';
        this.annotation_controller.area_ruler_config =
            (typeof path_config === 'undefined') ? {} : path_config;

        this.annotation_controller.area_ruler_out_id = undefined;
        this.annotation_controller.area_ruler_binding_shape_id = undefined;

        this.annotation_controller.updateAreaRulerConfig = function(ruler_config) {
            this.area_ruler_config = ruler_config;
        };

        this.annotation_controller.extendAreaRulerConfig = function(ruler_config) {
            this.area_ruler_config = $.extend({}, this.area_ruler_config, ruler_config);
        };

        this.annotation_controller.createAreaRulerPath = function (x, y) {
            this.drawPolygon(this.area_ruler_id, [], undefined, this.area_ruler_config, false);
            this.selectShape(this.area_ruler_id);
            this.area_ruler = this.getShape(this.area_ruler_id);
            this.area_ruler.addPoint(x, y);
            $("#" + this.area_ruler_out_id).trigger('area_ruler_created', [{'x': x, 'y': y}]);
            this.refreshView();
        };

        this.annotation_controller.addPointToAreaRuler = function (x, y) {
            this.area_ruler.addPoint(x, y);
            this.refreshView();
        };

        this.annotation_controller.clearAreaRuler = function (ruler_saved) {
            if (typeof this.area_ruler !== 'undefined') {
                this.deleteShape(this.area_ruler_id);
                this.area_ruler_id = undefined;
            }
            $("#" + this.area_ruler_out_id).trigger('area_ruler_cleared', [ruler_saved]);
        };

        this.annotation_controller.adaptRulerToShape = function () {
            var intersection = this.area_ruler.getIntersection(
                this.getShape(this.area_ruler_binding_shape_id)
            );
            var intersection_path = ShapeConverter.extractPathSegments(intersection,
                this.x_offset, this.y_offset);
            if (intersection_path.length === 0) {
                this.deleteShape(this.area_ruler_id);
                this.area_ruler = undefined;
                $("#" + this.area_ruler_out_id).trigger('area_ruler_empty_intersection');
            } else {
                var ruler_json = this.getShapeJSON(this.area_ruler_id);
                // replace segments of the ruler with the ones of the intersection
                ruler_json.segments = intersection_path;
                this.deleteShape(this.area_ruler_id);
                intersection.remove();
                this.drawShapeFromJSON(ruler_json);
                this.area_ruler = this.getShape(this.area_ruler_id);
                this.refreshView();
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
                ruler_json.shape_id = this._getShapeId('area_ruler');
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
            this.annotations_controller.createAreaRulerPath(event.point.x, event.point.y);
        };

        area_ruler_tool.onMouseDrag = function (event) {
            this.annotations_controller.addPointToAreaRuler(event.point.x, event.point.y);
        };

        area_ruler_tool.onMouseUp = function () {
            this.annotations_controller.serializeAreaRuler();
            this.annotations_controller.updateAreaRulerOutputField();
            this.annotations_controller.clearAreaRuler();
        };

        this.initialized_tools[AnnotationsEventsController.AREA_MEASURING_TOOL] = area_ruler_tool;

    } else {
        console.warn('Tool "' + AnnotationsEventsController.AREA_MEASURING_TOOL + '" already initialized');
    }
};