function Shape(id, transform_matrix) {
    this.id = id;
    this.original_transform_matrix = transform_matrix;
    this.paper_shape = undefined;

    this.fill_color = undefined;
    this.stroke_color = undefined;
    this.stroke_width = undefined;

    this._configJSON = function() {
        var fill_color_json = ColorsAdapter.paperColorToHex(this.fill_color);
        var stroke_color_json = ColorsAdapter.paperColorToHex(this.stroke_color);
        return {
            'shape_id': this.id,
            'transform': (typeof this.original_transform_matrix !== 'undefined') ?
                this.original_transform_matrix.toJSON() : undefined,
            'fill_color': fill_color_json.hex_color,
            'fill_alpha': fill_color_json.alpha,
            'stroke_color': stroke_color_json.hex_color,
            'stroke_alpha': stroke_color_json.alpha,
            'stroke_width': this.stroke_width,
            'hidden': this.isHidden()
        }
    };

    this._bindWrapper = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.shape_wrapper = this;
        }
    };

    this._shapeToPath = function() {
        try {
            return this.paper_shape.toPath(false);
        } catch(err) {
            return this.paper_shape;
        }
    };

    this.setId = function(id) {
        this.id = id;
    };

    this.enableDashedBorder = function(dash, gap) {
        this.paper_shape.setDashArray([dash, gap]);
    };

    this.disableDashedBorder = function() {
        this.paper_shape.setDashArray([]);
    };

    this.setStrokeColor = function(color, alpha) {
        var color_value = (typeof color === 'undefined') ? this.stroke_color.toCSS(true) : color;
        var alpha_value = (typeof alpha === 'undefined') ? this.stroke_color.getAlpha() : alpha;
        this.stroke_color = ColorsAdapter.hexToPaperColor(color_value, alpha_value);
        this.paper_shape.setStrokeColor(this.stroke_color);
    };

    this.setFillColor = function(color, alpha) {
        var color_value = (typeof color === 'undefined') ? this.fill_color.toCSS(true) : color;
        var alpha_value = (typeof alpha === 'undefined') ? this.fill_color.getAlpha() : alpha;
        this.fill_color = ColorsAdapter.hexToPaperColor(color_value, alpha_value);
        this.paper_shape.setFillColor(this.fill_color);
    };

    this.setStrokeWidth = function(stroke_width) {
        this.stroke_width = stroke_width;
        this.paper_shape.setStrokeWidth = this.stroke_width;
    };

    this.transformShape = function(transform_matrix) {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.transform(transform_matrix);
        } else {
            console.info('Shape not initialized');
        }
    };

    this.getCenter = function() {
        if (typeof this.paper_shape !== 'undefined') {
            var bbox = this.paper_shape.bounds;
            return {
                'x': bbox.center.x,
                'y': bbox.center.y
            }
        } else {
            console.info('Shape not initialized');
        }
    };

    this.getPathSegments = function() {
        if (typeof this.paper_shape !== 'undefined') {
            return this._shapeToPath().getSegments();
        } else {
            return undefined;
        }
    };

    this.getArea = function(pixel_size, decimal_digits) {
        var decimals = (typeof decimal_digits === 'undefined') ? 2 : decimal_digits;
        if (typeof this.paper_shape !== 'undefined') {
            var area = Math.abs(this._shapeToPath().area * Math.pow(pixel_size, 2));
            return Number(area.toFixed(decimals));
        } else {
            console.log('Shape not initialized');
            return undefined;
        }
    };

    this.getPerimeter = function(pixel_size, decimal_digits) {
        var decimals = (typeof decimal_digits === 'undefined') ? 2 : decimal_digits;
        if (typeof this.paper_shape !== 'undefined') {
            var perimeter = this._shapeToPath().length * pixel_size;
            return Number(perimeter.toFixed(decimals));
        } else {
            console.log('Shape not initialized');
        }
    };

    this.getBoundingBoxDimensions = function() {
        if (typeof this.paper_shape !== 'undefined') {
            var bbox = this.paper_shape.bounds;
            return {
                'width': bbox.width,
                'height': bbox.height
            };
        } else {
            console.info('Shape not initialized');
        }
    };

    this.containsPoint = function(point_x, point_y) {
        var point_obj = new paper.Point(point_x, point_y);
        if (typeof this.paper_shape !== 'undefined')
            return this.paper_shape.contains(point_obj);
        else
            console.info('Shape not initialized');
    };

    this.containsShape = function(shape) {
        var shape_segments = shape.getPathSegments(shape);
        if ((typeof this.paper_shape !== 'undefined') && (typeof shape_segments !== 'undefined')) {
            for (var segment_id in shape_segments) {
                if (!this.paper_shape.contains(shape_segments[segment_id].point)) {
                    return false;
                }
            }
            return true;
        }
        else {
            console.error('Both shapes must be initialized');
            return undefined;
        }
    };

    this.intersectsShape = function(shape) {
        return this._shapeToPath().intersects(shape._shapeToPath());
    };

    this.getIntersection = function(shape, draw_intersection) {
        var draw = typeof draw_intersection === 'undefined' ? false : draw_intersection;
        return this._shapeToPath().intersect(shape._shapeToPath(), {insert: draw});
    };

    this.getCoveragePercentage = function(shape) {
        var shape_area = shape.getArea(1);
        if ((typeof this.paper_shape !== 'undefined') && (typeof shape_area !== 'undefined')) {
            var intersection = this.getIntersection(shape);
            // passing 1 as pixel size because we only need area in pixels to get the coverage ratio
            var coverage_ratio = Math.abs(intersection.area) / this.getArea(1);
            intersection.remove();
            return (coverage_ratio * 100);
        } else {
            console.error('Both shapes must be initialized');
            return undefined;
        }
    };

    this.configure = function(shape_config) {
        if (typeof this.paper_shape !== 'undefined') {
            this.fill_color = ColorsAdapter.hexToPaperColor(shape_config.fill_color, shape_config.fill_alpha);
            this.paper_shape.setFillColor(this.fill_color);
            this.stroke_color = ColorsAdapter.hexToPaperColor(shape_config.stroke_color, shape_config.stroke_alpha);
            this.paper_shape.setStrokeColor(this.stroke_color);
            this.stroke_width = shape_config.stroke_width;
            this.paper_shape.setStrokeWidth(this.stroke_width);
        }
    };

    this.enableEvents = function(events_list) {
        if (typeof events_list === 'undefined') {
            for (var ev in this.default_events) {
                this.paper_shape[this.default_events[ev]] = true;
            }
        } else {
            for (var ev in events_list) {
                if (this.default_events.indexOf(events_list[ev]) !== -1) {
                    this.paper_shape[events_list[ev]] = true;
                } else {
                    console.warn('Unknown event ' + events_list[ev]);
                }
            }
        }
    };

    this.disableEvents = function(events_list) {
        if (typeof events_list === 'undefined') {
            for (var ev in this.default_events) {
                this.paper_shape[this.default_events[ev]] = false;
            }
        } else {
            for (var ev in events_list) {
                if (this.default_events.indexOf(events_list[ev]) !== -1) {
                    this.paper_shape[events_list[ev]] = false;
                } else {
                    console.warn('Unknown event ' + events_list[ev]);
                }
            }
        }
    };

    this._buildEvents = function() {
        this.paper_shape.on({
            mousedrag: function(event) {
                if (this[Shape.MOUSE_DRAG_EVENT] === true) {
                    document.body.style.cursor = 'move';
                    this.position = new paper.Point(
                        this.position.x + event.delta.x,
                        this.position.y + event.delta.y
                    );
                    this.shape_wrapper.updateShapePosition(event.delta.x, event.delta.y);
                }
            },
            mouseup:  function(event) {
                document.body.style.cursor = 'auto';
            }
        });
    };

    this.initializeEvents = function(activate_events) {
        var activate = (typeof activate_events === 'undefined') ? false : activate_events;
        this._buildEvents();
        if (activate) {
            this.enableEvents();
        } else {
            this.disableEvents();
        }
    };

    this.select = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.selected = true;
        }
    };

    this.deselect = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.selected = false;
        }
    };

    this.isSelected = function() {
        if (typeof this.paper_shape !== 'undefined') {
            return this.paper_shape.selected;
        } else {
            return undefined;
        }
    };

    this.show = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.setVisible(true);
        }
    };

    this.hide = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.setVisible(false);
        }
    };

    this.isHidden = function() {
        if (typeof this.paper_shape !== 'undefined') {
            return !(this.paper_shape.getVisible());
        }
    };

    this.delete = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.remove();
        }
    };
}

Shape.MOUSE_DRAG_EVENT = 'mouse_drag_event';
Shape.prototype.default_events = [
    Shape.MOUSE_DRAG_EVENT
];


function Rectangle(id, origin_x, origin_y, width, height, transform_matrix) {
    Shape.call(this, id, transform_matrix);

    this.origin_x = origin_x;
    this.origin_y = origin_y;
    this.width = width;
    this.height = height;

    this.toPaperShape = function(activate_events) {
        var rect = new paper.Shape.Rectangle({
            point: [this.origin_x, this.origin_y],
            size: [this.width, this.height]
        });
        this.paper_shape = rect;
        if (typeof this.original_transform_matrix !== 'undefined')
            this.transformShape(this.original_transform_matrix);
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapePosition = function(delta_x, delta_y) {
        this.origin_x += delta_x;
        this.origin_y += delta_y;
    };

    this.toJSON = function() {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'origin_x': this.origin_x,
                'origin_y': this.origin_y,
                'width': this.width,
                'height': this.height,
                'type': 'rectangle'
            });
        return shape_json;
    };
}

Rectangle.prototype = new Shape();


function Ellipse(id, center_x, center_y, radius_x, radius_y, transform_matrix) {
    Shape.call(this, id, transform_matrix);

    this.center_x = center_x;
    this.center_y = center_y;
    this.radius_x = radius_x;
    this.radius_y = radius_y;

    this.toPaperShape = function(activate_events) {
        var ellipse = new paper.Shape.Ellipse({
            center: [this.center_x, this.center_y],
            radius: [this.radius_x, this.radius_y]
        });
        this.paper_shape = ellipse;
        if (typeof this.original_transform_matrix !== 'undefined')
            this.transformShape(this.original_transform_matrix);
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapePosition = function(delta_x, delta_y) {
        this.center_x += delta_x;
        this.center_y += delta_y;
    };

    this.toJSON = function() {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'center_x': this.center_x,
                'center_y': this.center_y,
                'radius_x': this.radius_x,
                'radius_y': this.radius_y,
                'type': 'ellipse'
            });
        return shape_json;
    };
}

Ellipse.prototype = new Shape();


function Circle(id, center_x, center_y, radius, transform_matrix) {
    Shape.call(this, id, transform_matrix);

    this.center_x = center_x;
    this.center_y = center_y;
    this.radius = radius;

    this.toPaperShape = function(activate_events) {
        var circle = new paper.Shape.Circle({
            center: [this.center_x, this.center_y],
            radius: this.radius
        });
        this.paper_shape = circle;
        if (typeof this.original_transform_matrix !== 'undefined')
            this.transformShape(this.original_transform_matrix);
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapePosition = function(delta_x, delta_y) {
        this.center_x += delta_x;
        this.center_y += delta_y;
    };

    this.toJSON = function() {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'center_x': this.center_x,
                'center_y': this.center_y,
                'radius': this.radius,
                'type': 'circle'
            });
        return shape_json;
    };
}

Circle.prototype = new Shape();

function Path(id, segments, closed, transform_matrix) {
    Shape.call(this, id, transform_matrix);

    this.segments = (typeof segments === 'undefined') ? [] : segments;
    this.closed = closed;

    this._normalize_segments = function() {
        var paper_segments = [];
        for (var i=0; i<this.segments.length; i++) {
            var seg = {
                'point': [this.segments[i].point.x, this.segments[i].point.y]
            };
            if (this.segments[i].hasOwnProperty('handle_in')) {
                seg['handleIn'] = [
                    this.segments[i].handle_in.x, this.segments[i].handle_in.y
                ];
            }
            if (this.segments[i].hasOwnProperty('handle_out')) {
                seg['handleOut'] = [
                    this.segments[i].handle_out.x, this.segments[i].handle_out.y
                ];
            }
            paper_segments.push(seg);
        }
        return paper_segments;
    };

    this.toPaperShape = function(activate_events) {
        var path = new paper.Path({
            segments: this._normalize_segments(),
            closed: this.closed
        });
        this.paper_shape = path;
        if (typeof this.original_transform_matrix !== 'undefined')
            this.transformShape(this.original_transform_matrix);
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.getPathSegments = function() {
        if (typeof this.paper_shape !== 'undefined') {
            return this.paper_shape.getSegments();
        } else {
            return undefined;
        }
    };

    this.updateShapePosition = function(delta_x, delta_y) {
        var path_segments = this.segments;
        this.segments.forEach(function(segment, index) {
            path_segments[index].point = {
                'x': segment.point.x + delta_x,
                'y': segment.point.y + delta_y
            }
        });
    };

    this.openPath = function() {
        this.closed = false;
        this.paper_shape.closed = false;
    };

    this.closePath = function() {
        this.closed = true;
        this.paper_shape.closed = true;
    };


    this.addPoint = function(point_x, point_y) {
        this.segments.push({'point': {'x': point_x, 'y': point_y}});
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.add(new paper.Point(point_x, point_y));
        }
    };

    this.isEmpty = function() {
        return this.segments.length === 0;
    };

    this.removePoint = function(index) {
        if (this.segments.length > 0) {
            //by default, remove the last inserted point
            var sg_index = (typeof index === 'undefined') ? (this.segments.length - 1) : index;
            var sg = this.paper_shape.removeSegment(sg_index);
            this.segments.splice(sg_index, 1);
            return {'x': sg.point.x, 'y': sg.point.y};
        } else {
            throw new Error('There is no point to remove');
        }
    };

    this.simplifyPath = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.simplify();
            // get new segments
            this.segments = [];
            this._extract_segments();
        } else {
            console.info('Shape not initialized');
        }
    };

    this._extract_segments = function() {
        if (this.paper_shape !== 'undefined') {
            this.segments = ShapeConverter.extractPathSegments(this.paper_shape);
        } else {
            throw new Error('Paper shape not initialized');
        }
    };

    this._get_segments_json = function(x_offset, y_offset) {
        if (this.segments.length === 0) {
            this._extract_segments();
        }
        return ShapeConverter.extractPathSegments(this.paper_shape, x_offset, y_offset);
    };

    this.toJSON = function(x_offset, y_offset) {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'segments': this._get_segments_json(x_offset, y_offset)
            }
        );
        return shape_json;
    }
}

Path.prototype = new Shape();

function Polyline(id, segments, transform_matrix) {
    Path.call(this, id, segments, false, transform_matrix);

    this.containsShape = function(shape) {
        return false;
    };

    this.getArea = function(pixel_size) {
        // lines have no area
        return undefined;
    };

    this.getCoveragePercentage = function(shape) {
        // lines have no area, it is impossible to calculate coverage
        return undefined;
    };

    var pathToJSON = this.toJSON;
    this.toJSON = function(x_offset, y_offset) {
        var shape_json = pathToJSON.apply(this, [x_offset, y_offset]);
        shape_json['type'] = 'polyline';
        return shape_json;
    };
}

Polyline.prototype = new Path();

function Polygon(id, segments, transform_matrix) {
    Path.call(this, id, segments, true, transform_matrix);

    var pathToJSON = this.toJSON;
    this.toJSON = function(x_offset, y_offset) {
        var shape_json = pathToJSON.apply(this, [x_offset, y_offset]);
        shape_json['type'] = 'polygon';
        return shape_json;
    };
}

Polygon.prototype = new Path();