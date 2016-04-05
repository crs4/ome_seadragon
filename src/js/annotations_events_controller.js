function AnnotationsEventsController(annotations_controller) {

    this.DUMMY_TOOL = 'dummy_tool';
    this.IMAGE_MARKING_TOOL = 'image_marker';
    this.POLYGON_DRAWING_TOOL = 'polygon_drawer';

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
            
            this.annotation_controller.updateMarkersConfig = function(markers_config) {
                this.markers_config = markers_config;
            };

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
    
    this.initializePolygonDrawingTool = function(polygon_config, switch_on_id, save_figure_id) {
        // by default, initialize dummy tool
        this.initializeDummyTool();
        
        if (! (this.POLYGON_DRAWING_TOOL in this.initialized_tools)) {
            
            this.annotation_controller.tmp_polygon = undefined;
            this.annotation_controller.tmp_polygon_id = 'tmp_polygon';
            this.annotation_controller.polygon_config = polygon_config;
            
            this.annotation_controller.updatePolygonConfig = function(polygon_config) {
                this.polygon_config = polygon_config;
            };

            this.annotation_controller._pointToPolygon = function(x, y) {
                var trigger_label = undefined;
                if (this.tmp_polygon) {
                    this.tmp_polygon.addPoint(x, y);
                    trigger_label = 'polygon_add_point';
                } else {
                    this.drawPolygon(this.tmp_polygon_id, [], true, undefined,
                        this.polygon_config, false);
                    this.selectShape(this.tmp_polygon_id);
                    this.tmp_polygon = this.getShape(this.tmp_polygon_id);
                    this.tmp_polygon.addPoint(x, y);
                    trigger_label = 'polygon_created';
                }
                this.refreshView();
                $("#" + this.canvas_id).trigger(trigger_label, [{'x': x, 'y': y}]);
            };

            this.annotation_controller.addPointToPolygon = function(event) {
                this._pointToPolygon(event.point.x, event.point.y);
            };

            this.annotation_controller.replaceLastPoint = function(event) {
                this.tmp_polygon.removePoint();
                this.addPointToPolygon(event);
            };

            this.annotation_controller.removeLastPoint = function() {
                try {
                    this.tmp_polygon.removePoint();
                    this.refreshView();
                } catch(err) {
                    this.clearTemporaryPolygon();
                }
            };

            this.annotation_controller.clearTemporaryPolygon = function() {
                if (typeof this.tmp_polygon !== 'undefined') {
                    this.deleteShape(this.tmp_polygon_id);
                    this.tmp_polygon = undefined;
                    $('#' + this.canvas_id).trigger('polygon_cleared');
                }
            };

            this.annotation_controller.saveTemporaryPolygon = function() {
                var tmp_polygon_json = this.getShapeJSON(this.tmp_polygon_id);
                this.deleteShape(this.tmp_polygon_id, false);
                tmp_polygon_json.shape_id = this._getShapeId('polygon');
                // apply translation
                var ac = this;
                tmp_polygon_json.points = $.map(tmp_polygon_json.points, function(point) {
                    return {
                        'x': point.x + ac.x_offset,
                        'y': point.y + ac.y_offset
                    }
                });
                this.drawShapeFromJSON(tmp_polygon_json, true);
                this.tmp_polygon = undefined;
                $("#" + this.canvas_id).trigger('polygon_saved', [tmp_polygon_json.shape_id]);
            };

            var marking_tool = new paper.Tool();

            marking_tool.annotations_controller = this.annotation_controller;

            marking_tool.onMouseDown = function(event) {
                this.annotations_controller.addPointToPolygon(event);
            };

            marking_tool.onMouseDrag = function(event) {
                this.annotations_controller.replaceLastPoint(event);
            };

            this.initialized_tools[this.POLYGON_DRAWING_TOOL] = marking_tool;

            if (typeof switch_on_id !== 'undefined') {
                this._bind_switch(switch_on_id, this.POLYGON_DRAWING_TOOL);
            }

            // if a "switch off" element is provided, bind it to the save polygon action
            if (typeof save_figure_id !== 'undefined') {
                $("#" + save_figure_id).bind(
                    'click',
                    {'annotation_controller': this.annotation_controller},
                    function(event) {
                        console.log(event.data);
                        event.data.annotation_controller.saveTemporaryPolygon();
                    }
                );
            }
        } else {
            console.warn('Tool"' + this.POLYGON_DRAWING_TOOL + '" already initialized');
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
