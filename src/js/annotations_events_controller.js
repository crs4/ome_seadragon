function AnnotationsEventsController(annotations_controller) {

    this.DUMMY_TOOL = 'dummy_tool';
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

    // Create a tool that simply ignores mouse events, this will be used, for example, to avoid
    // events propagation when capturing events on Shapes
    this.initializeDummyTool = function() {
        if (! (this.DUMMY_TOOL in this.initialized_tools)) {
            this.initialized_tools[this.DUMMY_TOOL] = new paper.Tool();
        }
    };

    this.initializeImageMarkingTool = function(marker_size, markers_config, markers_limit, switch_id) {
        // by default, initialize dummy tool
        this.initializeDummyTool();

        if(! (this.IMAGE_MARKING_TOOL in this.initialized_tools)) {
            
            this.annotation_controller._activate_paper_scope();

            this.annotation_controller.markers_id = [];

            this.annotation_controller.markers_config = markers_config;

            if ((typeof markers_limit !== 'undefined') || (markers_limit > 0)) {
                this.annotation_controller.max_markers_count = markers_limit;
            } else {
                this.annotation_controller.max_markers_count = 0;
            }

            this.annotation_controller._check_markers_limit = function() {
                if (this.markers_id.length > 0 && (this.markers_id.length >= this.max_markers_count))
                    return false;
                return true;
            };

            this.annotation_controller.getMarkersID = function() {
                return this.markers_id.slice();
            };

            // extending behaviour for delete shape when markers tool is enabled
            var oldDeleteShape = this.annotation_controller.deleteShape;
            this.annotation_controller.deleteShape = function(shape_id, refresh_view) {
                var delete_status = oldDeleteShape.apply(this, [shape_id, refresh_view]);
                if (delete_status == true && ($.inArray(shape_id, this.markers_id) !== -1)) {
                    this.markers_id.splice(this.markers_id.indexOf(shape_id), 1);
                    $("#" + this.canvas_id).trigger('marker_deleted', [shape_id]);
                }
            };

            this.annotation_controller.removeMarker = function(marker_id) {
                if ($.inArray(marker_id, this.markers_id) != -1) {
                    this.deleteShape(marker_id);
                } else {
                    console.warn(marker_id + ' is not the ID of a marker');
                }
            };

            this.annotation_controller.clearMarkers = function() {
                this.deleteShapes(this.markers_id);
            };

            this.annotation_controller._createMarker = function(x, y, radius, shape_id) {
                if (typeof(shape_id) === 'undefined') {
                    shape_id = this._getShapeId('marker');
                }
                this.drawCircle(shape_id, x, y, radius, undefined, this.markers_config, true);
                this.markers_id.push(shape_id);
                $("#" + this.canvas_id).trigger('marker_created', [shape_id]);
            };

            this.annotation_controller.addMarker = function(event) {
                var add_new_marker = this._check_markers_limit();
                if (add_new_marker === true) {
                    console.log('Adding marker');
                    var img_x = event.point.x + this.x_offset;
                    var img_y = event.point.y + this.y_offset;
                    this._createMarker(img_x, img_y, event.marker_radius);
                }
            };

            this.annotation_controller.shapeToMarker = function(shape_id) {
                try {
                    var shape_json = this.getShape(shape_id).toJSON();
                    // if shape is not already a marker as ONLY if it's a Circle
                    if ($.inArray(shape_id, this.markers_id) === -1 && shape_json.type === 'circle') {
                        // delete the shape
                        this.deleteShape(shape_id);
                        // use the _createMaker function to create the shape again as a marker
                        this._createMarker(shape_json.center_x, shape_json.center_y,
                            shape_json.radius, shape_id);
                    } else {
                        console.warn('Shape ' + shape_id + ' of type ' + shape_json.type +
                            ' can\'t be converted to maker');
                    }
                } catch (e) {
                    if (e instanceof TypeError) {
                        console.warn('There is no shape with ID: ' + shape_id);
                    }
                }
            };

            this.annotation_controller.shapesToMarkers = function(shape_ids) {
                var controller = this;
                shape_ids.filter( function(shape_id) {
                    controller.shapeToMarker(shape_id);
                })
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

    this.activateTool = function(tool_label, disable_events_on_shapes) {
        if (tool_label in this.initialized_tools) {
            var sh_ev_off = (typeof disable_events_on_shapes === 'undefined') ? true : disable_events_on_shapes;
            if (sh_ev_off === true)
                this.annotation_controller.disableEventsOnShapes();
            var tool = this.initialized_tools[tool_label];
            tool.activate();
            this.annotation_controller.enableMouseEvents();
        } else {
            console.warn('Tool ' + tool_label + ' not initialized');
        }
    };
}
