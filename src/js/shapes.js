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


function Rectangle(id, origin_x, origin_y, width, height) {
    Shape.call(this, id);

    this.origin_x = origin_x;
    this.origin_y = origin_y;
    this.width = width;
    this.height = height;

    this.toPaperShape = function() {
        var rect = new paper.Shape.Rectangle({
            point: [this.origin_x, this.origin_y],
            size: [this.width, this.height]
        });
        this.paper_shape = rect;
    };
}

Rectangle.prototype = new Shape();


function Ellipse(id, center_x, center_y, radius_x, radius_y) {
    Shape.call(this, id);

    this.center_x = center_x;
    this.center_y = center_y;
    this.radius_x = radius_x;
    this.radius_y = radius_y;

    this.toPaperShape = function() {
        var ellipse = new paper.Shape.Ellipse({
            center: [this.center_x, this.center_y],
            radius: [this.radius_x, this.radius_y]
        });
        this.paper_shape = ellipse;
    };
}

Ellipse.prototype = new Shape();


function Circle(id, center_x, center_y, radius) {
    Shape.call(this, id);

    this.center_x = center_x;
    this.center_y = center_y;
    this.radius = radius;

    this.toPaperShape = function() {
        var circle = new paper.Shape.Circle({
            center: [this.center_x, this.center_y],
            radius: this.radius
        });
        this.paper_shape = circle;
    };
}

Circle.prototype = new Shape();


function Line(id, from_x, from_y, to_x, to_y) {
    Shape.call(this, id);

    this.from_x = from_x;
    this.from_y = from_y;
    this.to_x = to_x;
    this.to_y = to_y;

    this.toPaperShape = function() {
        var line = new paper.Path.Line({
            from: [this.from_x, this.from_y],
            to: [this.to_x, this.to_y]
        });
        this.paper_shape = line;
    };
}

Line.prototype = new Shape();