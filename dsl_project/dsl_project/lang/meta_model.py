import os
from textx import metamodel_from_file, TextXSyntaxError, TextXSemanticError


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
    parameter_type = attribute_value.parameter.parameter_type

    parameter_val = attribute_value.value.value

    types_dictionary = {
        "string": "str",
        "integer": "int",
        "float": "float",
        "boolean": "bool",
    }
    if ((parameter_type[:-2] in types_dictionary and (
            type(parameter_val).__name__ != "list" or type(parameter_val[0]).__name__ != types_dictionary[parameter_type])) or
            (parameter_type in types_dictionary and (type(parameter_val).__name__ != types_dictionary[parameter_type]))):
        raise TextXSemanticError(
            'The type of the parameter {} of question type {} must be {}.'.format(attribute_value.parameter.name,
                                                                                  attribute_value.parent.type.name,
                                                                                  parameter_type))
