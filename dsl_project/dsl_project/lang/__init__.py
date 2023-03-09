import os
from .meta_model import get_add_meta_model, field_type_object_checker, Attribute, FieldType, add_content_object_checker, \
   field_type_object_checker, field_object_checker, attribute_value_object_checker
from textx import metamodel_from_file, language
import textx.scoping.providers as scoping_providers

from os.path import dirname

@language('model_lang', '*.add')
def model_lang():
   grammar_path = os.path.join(os.path.dirname(__file__), '../model.tx')

   object_checkers = {
      'AddContent': add_content_object_checker,
      'Field': field_object_checker,
      'AttributeValue': attribute_value_object_checker,
   }

   metamodel = metamodel_from_file(grammar_path, classes=[Attribute, FieldType],
                                   global_repository=True)

   metamodel.register_scope_providers({
      "*.*": scoping_providers.PlainNameImportURI(),
      "AttributeValue.attribute": scoping_providers.RelativeName(
         "parent.type.attributes"),
   })

   metamodel.register_obj_checkers(object_checkers)
   return metamodel

@language('field_lang', '*.ft')
def field_lang():
   grammar_path = os.path.join(os.path.dirname(__file__), 'field_types.tx')
   object_checkers = {
      'FieldType': field_type_object_checker
   }
   metamodel = metamodel_from_file(grammar_path, classes=[Attribute, FieldType],
                                   global_repository=True)
   metamodel.register_obj_checkers(object_checkers)
   return metamodel

