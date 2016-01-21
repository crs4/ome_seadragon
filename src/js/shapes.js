function Shape(id) {
    this.id = id;
    this.paper_shape = undefined;

    this.fill_color = undefined;
    this.stroke_color = undefined;
    this.stroke_width = undefined;

    this._configJSON = function() {
        var fill_color_json = ColorsAdapter.paperColorToHex(this.fill_color);
        var stroke_color_json = ColorsAdapter.paperColorToHex(this.stroke_color);
        return {
            'shape_id': this.id,
            'fill_color': fill_color_json.hex_color,
            'fill_alpha': fill_color_json.alpha,
            'stroke_color': stroke_color_json.hex_color,
            'stroke_alpha': stroke_color_json.alpha,
            'stroke_width': this.stroke_width
        }
    };

    this._bindWrapper = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.shape_wrapper = this;
        }
    };

    this.updateShapeDetails = function() {
        console.log('Using default updateShapeDetails method');
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

    this.contains = function(point_x, point_y) {
        var point_obj = new paper.Point(point_x, point_y);
        if (typeof this.paper_shape !== 'undefined')
            return this.paper_shape.contains(point_obj);
        else
            console.warn('Paper.js shape not initialized');
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
                }
            },
            mouseup:  function(event) {
                this.shape_wrapper.updateShapeDetails();
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
            this.paper_shape.setSelected(true);
        }
    };

    this.deselect = function() {
        if (typeof this.paper_shape !== 'undefined') {
            this.paper_shape.setSelected(false);
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


function Rectangle(id, origin_x, origin_y, width, height) {
    Shape.call(this, id);

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
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapeDetails = function() {
        this.origin_x = this.paper_shape.point.x;
        this.origin_y = this.paper_shape.point.y;
        this.width = this.paper_shape.size.width;
        this.height = this.paper_shape.size.height;
    };

    this.toJSON = function(x_offset, y_offset) {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'origin_x': this.origin_x + x_offset,
                'origin_y': this.origin_y + y_offset,
                'width': this.width,
                'height': this.height,
                'type': 'rectangle'
            });
        return shape_json;
    };
}

Rectangle.prototype = new Shape();


function Ellipse(id, center_x, center_y, radius_x, radius_y) {
    Shape.call(this, id);

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
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapeDetails = function() {
        this.center_x = this.paper_shape.position.x;
        this.center_y = this.paper_shape.position.y;
        this.radius_x = this.paper_shape.radius.width;
        this.radius_y = this.paper_shape.radius.height;
    };

    this.toJSON = function(x_offset, y_offset) {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'center_x': this.center_x + x_offset,
                'center_y': this.center_y + y_offset,
                'radius_x': this.radius_x,
                'radius_y': this.radius_y,
                'type': 'ellipse'
            });
        return shape_json;
    };
}

Ellipse.prototype = new Shape();


function Circle(id, center_x, center_y, radius) {
    Shape.call(this, id);

    this.center_x = center_x;
    this.center_y = center_y;
    this.radius = radius;

    this.toPaperShape = function(activate_events) {
        var circle = new paper.Shape.Circle({
            center: [this.center_x, this.center_y],
            radius: this.radius
        });
        this.paper_shape = circle;
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapeDetails = function() {
        this.center_x = this.paper_shape.position.x;
        this.center_y = this.paper_shape.position.y;
        this.radius = this.paper_shape.radius;
    };

    this.toJSON = function(x_offset, y_offset) {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'center_x': this.center_x + x_offset,
                'center_y': this.center_y + y_offset,
                'radius': this.radius,
                'type': 'circle'
            });
        return shape_json;
    };
}

Circle.prototype = new Shape();


function Line(id, from_x, from_y, to_x, to_y) {
    Shape.call(this, id);

    this.from_x = from_x;
    this.from_y = from_y;
    this.to_x = to_x;
    this.to_y = to_y;

    this.toPaperShape = function(activate_events) {
        var line = new paper.Path.Line({
            from: [this.from_x, this.from_y],
            to: [this.to_x, this.to_y]
        });
        this.paper_shape = line;
        this._bindWrapper();
        this.initializeEvents(activate_events);
    };

    this.updateShapeDetails = function() {
        this.from_x = this.paper_shape.segments[0].point.x;
        this.from_y = this.paper_shape.segments[0].point.y;
        this.to_x = this.paper_shape.segments[1].point.x;
        this.to_y = this.paper_shape.segments[1].point.y;
    };

    this.toJSON = function(x_offset, y_offset) {
        var shape_json = this._configJSON();
        $.extend(
            shape_json,
            {
                'from_x': this.from_x + x_offset,
                'from_y': this.from_y + y_offset,
                'to_x': this.to_x + x_offset,
                'to_y': this.to_y + y_offset,
                'type': 'line'
            });
        return shape_json;
    };
}

Line.prototype = new Shape();