import os
from textx import metamodel_from_file, TextXSyntaxError, TextXSemanticError
from textx.export import metamodel_export, model_export
import textx.scoping as scoping
import textx.scoping.providers as scoping_providers

builtin_field_types = ['TextField', 'ChoiceField', 'DropDownField', 'DateField', 'TimeField',  'NumberField']


class FieldType(object):
    def __init__(self, name, template_path, attributes):
        self.name = name
        self.template_path = template_path
        self.attributes = attributes

    def __str__(self):
        return self.name


class Attribute(object):
    def __init__(self, name, required, attribute_type, value=None):
        self.name = name
        self.required = required
        self.attribute_type = attribute_type
        self.value = value

    def __str__(self):
        return self.name


def add_content_object_checker(add_content):

    field_names = []
    for section in add_content.sections:
        add_content.extend([field.name for field in section.fields])

    errors = [field_name for field_name in field_names if field_names.count(field_name) > 1]
    for error in errors:
        raise TextXSemanticError(f'Field with the name {error} already exists! Field names must be unique.')


def field_type_object_checker(field_type):

    global builtin_field_types

    if field_type.template_path == '':
        raise TextXSemanticError('Template path for a field type can not be empty!')

    if field_type.name in builtin_field_types:
        raise TextXSemanticError(f'A predefined field type {field_type.name} already exists!')

    attr_names = []
    for attribute in field_type.attributes:
        attr_names.append(attribute.name)

    errors = [attribute_name for attribute_name in attr_names if attr_names.count(attribute_name) > 1]
    for error in errors:
        raise TextXSemanticError(
            f"Attribute with the name {error} already exists in the field type {field_type.name}!"
            f" Names of attributes in a field type must be unique.")


def field_object_checker(field):
    attributes_in_field = []
    for attr in field.attributes:
        attributes_in_field.append(attr.attribute)

    errors = [attr for attr in field.type.attributes if attr.required == True and attr not in attributes_in_field]
    for error in errors:
        raise TextXSemanticError(
                f'A required attribute {error} of field type {field.type.name} is missing from the field {field.name}!')

    errors = [attr for attr in attributes_in_field if attributes_in_field.count(attr) > 1]
    for error in errors:
        raise TextXSemanticError(
            f'Attribute {error} of field type {field.type.name} has been defined twice in field {field.name}')

    attributes_dict = {}
    for attr in field.attributes:
        attributes_dict[attr.attribute.name] = attr.value.value
    field.attributes = attributes_dict


def attribute_value_object_checker(attribute_value):
    pass


def get_field_types_meta_model():

    grammar_path = os.path.join(os.path.dirname(__file__), 'field_types.tx')

    text_field = get_text_area_field_builtin()
    choice_field = get_choice_builtin()
    dropdown_field = get_dropdown_builtin()
    number_field = get_number_field_builtin()
    date_field = get_date_field_builtin()
    time_field = get_time_field_builtin()

    built_in_objects = {
        'TextField': text_field,
        'ChoiceField': choice_field,
        'DropDownField': dropdown_field,
        'DateField': date_field,
        'TimeField': time_field,
        'NumberField': number_field
    }

    object_checkers = {
        'FieldType': field_type_object_checker
    }

    # build metamodel
    metamodel = metamodel_from_file(grammar_path, classes=[Attribute, FieldType],
                                    builtins=built_in_objects, global_repository=True)

    metamodel.register_obj_checkers(object_checkers)

    return metamodel


def get_text_area_field_builtin():
    multiline_attribute = Attribute('multiline', True, 'boolean', True)
    min_char_attribute = Attribute('min_length', False, 'integer', 0)
    max_char_attribute = Attribute('max_length', False, 'integer', 10)
    placeholder_attribute = Attribute('placeholder', False, 'string', 'input value')
    text_field = FieldType('TextField',  '', [multiline_attribute, max_char_attribute, min_char_attribute,
                                              placeholder_attribute])
    return text_field


def get_choice_builtin():
    choices_atribute = Attribute('choices', True, 'string[]')
    multiple_attribute = Attribute('multiple', True, 'boolean')
    choice_field = FieldType('ChoiceField', '', [choices_atribute, multiple_attribute])
    return choice_field


def get_dropdown_builtin():
    # drop down field
    options_attribute = Attribute('options', True, 'string[]')
    dropdown_field = FieldType('DropDownField',  '', [options_attribute])
    return dropdown_field


def get_number_field_builtin():
    min_number_attribute = Attribute('min', False, 'integer', 0)
    max_number_attribute = Attribute('max', False, 'integer', 10)
    placeholder_number_attribute = Attribute('placeholder', False, 'string', "Input value")
    number_field = FieldType('NumberField', '', [min_number_attribute, max_number_attribute,
                                                 placeholder_number_attribute])
    return number_field


def get_date_field_builtin():
    return FieldType('DateField', '', [])


def get_time_field_builtin():
    return FieldType('TimeField', '', [])


def get_add_meta_model():
    grammar_path = os.path.join(os.path.dirname(__file__), '../model.tx')

    object_checkers = {
        'SurveyContent': add_content_object_checker,
        'Field': field_object_checker,
        'AttributeValue': attribute_value_object_checker,
    }

    text_field = get_text_area_field_builtin()
    choice_field = get_choice_builtin()
    dropdown_field = get_dropdown_builtin()
    number_field = get_number_field_builtin()
    date_field = get_date_field_builtin()
    time_field = get_time_field_builtin()

    built_in_objects = {
        'TextField': text_field,
        'ChoiceField': choice_field,
        'DropDownField': dropdown_field,
        'DateField': date_field,
        'TimeField': time_field,
        'NumberField': number_field
    }

    metamodel = metamodel_from_file(grammar_path, classes=[Attribute, FieldType],
                                    builtins=built_in_objects, global_repository=True)

    metamodel.register_scope_providers({
        "*.*": scoping_providers.PlainNameImportURI(),
        "AttributeValue.attribute": scoping_providers.RelativeName(
            "parent.type.attributes"),
    })

    metamodel.register_obj_checkers(object_checkers)
