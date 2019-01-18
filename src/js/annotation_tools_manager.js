/*
 * Copyright (c) 2019, CRS4
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

function AnnotationsEventsController(annotations_controller) {
    this.annotation_controller = annotations_controller;
    this.initialized_tools = {};
}

AnnotationsEventsController.DUMMY_TOOL = 'dummy_tool';

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
    if (!(AnnotationsEventsController.DUMMY_TOOL in this.initialized_tools)) {
        this.initialized_tools[AnnotationsEventsController.DUMMY_TOOL] = new paper.Tool();
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

