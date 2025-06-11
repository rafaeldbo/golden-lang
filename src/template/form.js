class ElementController {
    constructor(elementId, attribute = "innerHTML", type = "text") {
        this.element = document.getElementById(elementId);
        if (!this.element) {
            throw new Error(`Element with ID '${elementId}' not found.`);
        }
        this.attribute = attribute;
        this.type = type;
    }

    get() { 
        if (this.type === "boolean") return this.element[this.attribute]
        else if (this.type === "date") return new DateWrapper(this.element[this.attribute]);
        else if (this.type === "time") return new TimeWrapper(this.element[this.attribute]);
        return this.element?.[this.attribute] || ""; 
    }
    set(value) { if (this.element) this.element[this.attribute] = value.toString(); }
}

class ListElementController {
    constructor(elementId, childrenTag) {
        this.element = document.getElementById(elementId);
        if (!this.element) {
            throw new Error(`Elemento com ID '${elementId}' não encontrado.`);
        }
        this.childrenTag = childrenTag;
    }

    get length() { return this.element.children.length; }

    getItems() { return Array.from(this.element.children).map(item => item.innerHTML); }

    setItems(items) {
        this.element.innerHTML = "";
        items.forEach(item => this.addItem(item));
    }

    addItem(value) {
        const itemElement = this.createItemElement(value);
        this.element.appendChild(itemElement);
    }

    removeItem(value) {
        const items = Array.from(this.element.children);
        const index = items.findIndex(item => item.innerHTML === value);
        if (index !== -1) {
            items[index].remove();
        }
        return index;
    }

    updateItem(index, newValue) {
        const items = this.element.children;
        if (index >= 0 && index < items.length) {
            items[index].value = newValue;
            items[index].innerHTML = newValue;
        }
    }

    pop() {
        if (this.length > 0) {
            const lastItem = this.element.children[this.length - 1];
            lastItem.remove();
            return lastItem.innerHTML;
        }
        return null;
    }

    push(value) { this.addItem(value); }

    delete(index) {
        const items = this.element.children;
        if (index >= 0 && index < items.length) {
            items[index].remove();
        }
    }

    createItemElement(value) {
        const itemElement = document.createElement(this.childrenTag);
        itemElement.value = value.toString();
        itemElement.innerHTML = value.toString();
        return itemElement;
    }

    get(index) {
        const items = this.element.children;
        return index >= 0 && index < items.length ? items[index].innerHTML : undefined;
    }

    set(index, value) {  this.updateItem(index, value); }
}

export class FormField {
    constructor(fieldName, type, initial = {}) {
        this.name = fieldName;
        this.type = type;
        this.input = document.getElementById(fieldName);

        this.title = new ElementController(`${fieldName}-title`);
        if (initial.title) this.title.set(initial.title);

        this.description = new ElementController(`${fieldName}-description`);
        if (initial.description) this.description.set(initial.description);

        if (this.type !== "select") {
            this.placeholder = new ElementController(fieldName, "placeholder");
            if (initial.placeholder) this.placeholder.set(initial.placeholder);
        }
        this.required = new ElementController(fieldName, "required", "boolean");
        if (initial.required) this.required.set(initial.required);

        this.value = new ElementController(fieldName, "value", type);
        if (initial.defaultValue) this.value.set(initial.defaultValue);

        if (type === "select" && initial.options) {
            this.options = new ListElementController(fieldName, "option");
            this.options.setItems(initial.options);
        }

        if (initial.onChange) {
            this.onChange = initial.onChange;
            this.input.addEventListener("input", () => {
                if (this.onChange && !this.onChange()) {
                    // código para bloquear submição
                }
            });
        }
    }
};

export class Form {
    constructor(formName, { fields = [], onSubmit = () => {} } = {}) {
        this.form = document.getElementById(formName);
        this.fields = {};
        fields.forEach(field => {
            this.fields[field.name] = field;
            this[field.name] = field; 
        });

        this.onSubmit = onSubmit;
        this.form.addEventListener("submit", (event) => {
            event.preventDefault();
            if (!this.onSubmit || this.onSubmit()) {
                const formData = this.getFormData();
                this.form.reset();
                console.log("Form submitted with data:", formData);
            }
        });
    }

    getFormData() {
        const data = {};
        Object.keys(this.fields).forEach(fieldName => {
            data[fieldName] = this.fields[fieldName].getValue();
        });
        return data;
    }

    setValues(values) {
        Object.keys(values).forEach(fieldName => {
            if (this.fields[fieldName]) {
                this.fields[fieldName].setValue(values[fieldName]);
            }
        });
    }
}

export function display(on, text) {
	document.getElementById(`${on}-display`).innerHTML = text.toString();
}

export class DateWrapper {
    constructor(value) {
        if (typeof value === "string") {
            const [year, month, day] = value.split("-").map(Number);
            this.value = new Date(year, month - 1, day);
            if (isNaN(this.value)) throw new Error("Invalid date format. Use YYYY-MM-DD.");
        } else if (value instanceof Date) {
            this.value = value;
        } else {
            throw new TypeError(`Expected string or Date, got ${typeof value}`);
        }
    }

    toString() { return this.value.toISOString().split("T")[0]; }

    valueOf() { return this.value.getTime(); } // timestamp

    subtract(other) {
        if (other instanceof DateWrapper) {
            return Math.floor((this.value - other.value) / (1000 * 60 * 60 * 24));
        }
        throw new TypeError(`Cannot subtract ${typeof other} from DateWrapper`);
    }

    add(days) {
        if (typeof days !== "number") throw new TypeError(`Cannot add ${typeof days} to DateWrapper`);
        const newDate = new Date(this.value);
        newDate.setDate(newDate.getDate() + days);
        return new DateWrapper(newDate);
    }

    equals(other) {
        if (other instanceof DateWrapper) {
            return this.valueOf() === other.valueOf();
        }
        throw new TypeError(`Cannot compare DateWrapper with ${typeof other}`);
    }
}

export class TimeWrapper {
    constructor(value) {
        if (typeof value === "string") {
            const [hours, minutes] = value.split(":").map(Number);
            if (isNaN(hours) || isNaN(minutes) || hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
                throw new Error("Invalid time format. Use HH:MM.");
            }
            this.value = new Date();
            this.value.setHours(hours, minutes, 0, 0);
        } else if (value instanceof Date) {
            this.value = value;
        } else if (typeof value === "number") {
            this.value = new Date();
            this.value.setHours(Math.floor(value / 60), value % 60, 0, 0);
        } else {
            throw new TypeError(`Expected string or Date, got ${typeof value}`);
        }
    }

    toString() { return this.value.toTimeString().slice(0, 5); }

    valueOf() { return this.value.getHours() * 60 + this.value.getMinutes(); } // minutes

    add(minutes) {
        if (typeof minutes !== "number") throw new TypeError(`Cannot add ${typeof minutes} to TimeWrapper`);
        return new TimeWrapper(new Date(this.value.getTime() + minutes * 60 * 1000).toTimeString().slice(0, 5));
    }

    subtract(other) {
        if (typeof other === "number") {
            return this.add(-other);
        } else if (other instanceof TimeWrapper) {
            return this.valueOf() - other.valueOf();
        }
        throw new TypeError(`Cannot subtract ${typeof other} from TimeWrapper`);
    }

    equals(other) {
        if (other instanceof TimeWrapper) {
            return this.valueOf() === other.valueOf();
        }
        throw new TypeError(`Cannot compare TimeWrapper with ${typeof other}`);
    }
}

Object.prototype.equals = function (other) {
    return this.valueOf() === other.valueOf();
};

Object.prototype.add = function (other) {
    return this.valueOf() + other.valueOf();
}

Object.prototype.subtract = function (other) {
    return this.valueOf() - other.valueOf(); 
};