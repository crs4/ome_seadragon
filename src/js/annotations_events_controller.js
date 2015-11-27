function AnnotationsEventsController(annotations_controller) {
    this.SIMPLE_CLICK_EVENT_TOOL = 'simple_click';

    this.annotation_controller = annotations_controller;
    this.initialized_tools = {};

    this.initializeSimpleClickEvent = function(switch_id) {
        if (! (this.SIMPLE_CLICK_EVENT_TOOL in this.initialized_tools)) {
            AnnotationsController.prototype.clickFeedback = function (event) {
                console.log('Hello I\'m ' + this.canvas_id);
                console.log('You clicked on X: ' + event.point.x + ' Y: ' + event.point.y);
            };

            var simple_click_tool = new paper.Tool();

            simple_click_tool.annotations_controller = this.annotation_controller;

            simple_click_tool.onMouseDown = function (event) {
                this.annotations_controller.clickFeedback(event);
            };

            this.initialized_tools[this.SIMPLE_CLICK_EVENT_TOOL] = simple_click_tool;

            if (typeof switch_id !== 'undefined') {
                $('#' + switch_id).bind(
                    'click',
                    {'events_controller': this, 'tool_label': this.SIMPLE_CLICK_EVENT_TOOL},
                    function(event) {
                        event.data.events_controller.activateTool(event.data.tool_label);
                    }
                );
            }
        } else {
            console.warn('Tool "' + this.SIMPLE_CLICK_EVENT_TOOL + '" already initialized');
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
