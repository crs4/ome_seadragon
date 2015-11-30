function AnnotationsEventsController(annotations_controller) {

    this.IMAGE_MARKING_TOOL = 'image_marker';

    this.annotation_controller = annotations_controller;
    this.initialized_tools = {};

    this._bind_switch = function(switch_id, tool_label) {
        $("#" + switch_id).bind(
            'click',
            {'events_controller': this, 'tool_label': tool_label},
            function(event) {
                event.data.events_controller.activateTool(event.data.tool_label);
            }
        );
    };

    this.initializeImageMarkingTool = function(marker_size, markers_limit, switch_id) {
        if(! (this.IMAGE_MARKING_TOOL in this.initialized_tools)) {

            AnnotationsController.prototype.markers_counter = 0;

            if ((typeof markers_limit !== 'undefined') || (markers_limit > 0)) {
                AnnotationsController.prototype.max_markers_count = markers_limit;
            } else {
                AnnotationsController.prototype.max_markers_count = 0;
            }

            AnnotationsController.prototype._check_markers_limit = function() {
                if (this.max_markers_count > 0 && (this.markers_counter >= this.max_markers_count))
                    return false;
                return true;
            };

            AnnotationsController.prototype.removeMarker = function(marker_id) {
                var deleted = this.deleteShape(marker_id);
                if (deleted === true) {
                    this.markers_counter -= 1;
                }
            };

            AnnotationsController.prototype.addMarker = function(event) {
                var add_new_marker = this._check_markers_limit();
                if (add_new_marker === true) {
                    console.log('Adding marker');
                    var img_x = event.point.x + this.x_offset;
                    var img_y = event.point.y + this.y_offset;
                    var shape_id = this._getShapeId('marker');
                    this.drawCircle(shape_id, img_x, img_y, event.marker_radius, undefined, true);
                    this.markers_counter += 1;
                }
            };

            var marking_tool = new paper.Tool();

            marking_tool.annotations_controller = this.annotation_controller;
            marking_tool.marker_size = marker_size;

            marking_tool.onMouseDown = function(event) {
                event.marker_radius = this.marker_size / 2;
                this.annotations_controller.addMarker(event);
            };

            this.initialized_tools[this.IMAGE_MARKING_TOOL] = marking_tool;

            if (typeof switch_id !== 'undefined') {
                this._bind_switch(switch_id, this.IMAGE_MARKING_TOOL);
            }
        } else {
            console.warn('Tool "' + this.IMAGE_MARKING_TOOL + '" already initialized');
        }
    };

    this.activateTool = function(tool_label) {
        if (tool_label in this.initialized_tools) {
            var tool = this.initialized_tools[tool_label];
            tool.activate();
            this.annotation_controller.enableMouseEvents();
        } else {
            console.warn('Tool ' + tool_label + ' not initialized');
        }
    };
}
