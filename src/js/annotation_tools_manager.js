function AnnotationsEventsController(annotations_controller) {
    this.DUMMY_TOOL = 'dummy_tool';
    this.annotation_controller = annotations_controller;
    this.initialized_tools = {};
}

AnnotationsEventsController.prototype._bind_switch = function (switch_id, tool_label) {
    $("#" + switch_id).bind(
        'click',
        {'events_controller': this, 'tool_label': tool_label},
        function (event) {
            event.data.events_controller.activateTool(event.data.tool_label);
        }
    );
};

// Create a tool that simply ignores mouse events, this will be used, for example, to avoid
// events propagation when capturing events on Shapes
AnnotationsEventsController.prototype.initializeDummyTool = function () {
    if (!(this.DUMMY_TOOL in this.initialized_tools)) {
        this.initialized_tools[this.DUMMY_TOOL] = new paper.Tool();
    }
};

AnnotationsEventsController.prototype.activateTool = function (tool_label, disable_events_on_shapes) {
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

