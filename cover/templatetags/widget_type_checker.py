from django import template


register = template.Library()

@register.filter
def is_field_password(widget):
    widget_type = widget.widget_type
    return widget_type == "password"

@register.filter
def is_field_checkbox(widget):
    widget_type = widget.widget_type
    return widget_type == "checkbox"

@register.filter
def is_field_file(widget):
    widget_type = widget.widget_type
    return widget_type == "clearablefile" or widget_type == "file"

@register.filter
def is_field_date(widget):
    widget_type = widget.widget_type
    return widget_type == "date"

@register.filter
def is_field_datetime(widget):
    widget_type = widget.widget_type
    return widget_type == "datetime"

@register.filter
def is_field_textarea(widget):
    widget_type = widget.widget_type
    return widget_type == "textarea"

@register.filter
def is_field_radio(widget):
    widget_type = widget.widget_type
    return widget_type == "radioselect"

@register.filter
def widget_col_width(widget):
    col_width = "col-md-12"
    if hasattr(widget.field, 'col_width'):
        col_width = "col-md-" + str(widget.field.col_width)
    return col_width
