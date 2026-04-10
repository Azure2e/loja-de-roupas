# core/templatetags/form_filters.py
from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """Adiciona uma classe CSS ao campo de formulário"""
    if not field:
        return field
    
    # Garante que o widget tem attrs
    attrs = field.field.widget.attrs.copy()
    existing_classes = attrs.get('class', '')
    
    # Adiciona a nova classe sem duplicar
    if existing_classes:
        new_classes = f"{existing_classes} {css_class}"
    else:
        new_classes = css_class
    
    attrs['class'] = new_classes
    field.field.widget.attrs = attrs
    
    return field