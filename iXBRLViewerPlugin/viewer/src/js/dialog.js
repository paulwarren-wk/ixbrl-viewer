// Copyright 2019 Workiva Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
import $ from 'jquery';

export var dialogStack = new DialogStack();

function DialogStack() {
    this._stack = [];
    var ds = this;
    $(document).bind("keyup",function (e) {
        if (e.keyCode === 27) {
            ds.closeTop();
        }
    });
}

DialogStack.prototype.add = function (dialog) {
    this._stack.push(dialog);
    var z = this._stack.length * 100;
    dialog.element.css("z-index", z);
    $(".dialog-mask").show().css("z-index", z - 5);
    $('.close', dialog.element)
        .off('click')
        .on('click', function () { dialogStack.closeTop(); });
}

DialogStack.prototype.closeTop = function () {
    var dialog = this._stack.pop();
    dialog.element.remove();
    var z = this._stack.length * 100;
    if (z > 0) {
        $(".dialog-mask").show().css("z-index", z - 5);
    }
    else {
        $(".dialog-mask").hide();
    }
}

export function Dialog(contents, options) {
    this._options = options || {};
    this._contents = contents;
}

Dialog.prototype.show = function () {
    this.element = $('<div class="dialog"></div>')
        .append($('<div class="close"></div>'))
        .append($('<div class="contents"></div>').append(this._contents))
        .appendTo($('#dialog-container'));
    if (this._options.fullscreen) {
        this.element.addClass("dialog-fullscreen");
    }
    dialogStack.add(this);
}


