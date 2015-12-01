function Shape(id) {
    this.id = id;
    this.paper_shape = undefined;

    this.fill_color = undefined;
    this.stroke_color = undefined;
    this.stroke_width = undefined;

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
    }
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
        this.initializeEvents(activate_events);
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
        this.initializeEvents(activate_events);
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
        this.initializeEvents(activate_events);
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
        this.initializeEvents(activate_events);
    };
}

Line.prototype = new Shape();