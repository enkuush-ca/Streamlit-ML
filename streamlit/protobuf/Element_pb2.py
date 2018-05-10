# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Element.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import Text_pb2 as Text__pb2
import DataFrame_pb2 as DataFrame__pb2
import Chart_pb2 as Chart__pb2
import Image_pb2 as Image__pb2
import Progress_pb2 as Progress__pb2
import DocString_pb2 as DocString__pb2
import Exception_pb2 as Exception__pb2
import Empty_pb2 as Empty__pb2
import Map_pb2 as Map__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='Element.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\rElement.proto\x1a\nText.proto\x1a\x0f\x44\x61taFrame.proto\x1a\x0b\x43hart.proto\x1a\x0bImage.proto\x1a\x0eProgress.proto\x1a\x0f\x44ocString.proto\x1a\x0f\x45xception.proto\x1a\x0b\x45mpty.proto\x1a\tMap.proto\"\x8f\x02\n\x07\x45lement\x12\x15\n\x04text\x18\x01 \x01(\x0b\x32\x05.TextH\x00\x12\x17\n\x05\x65mpty\x18\x02 \x01(\x0b\x32\x06.EmptyH\x00\x12 \n\ndata_frame\x18\x03 \x01(\x0b\x32\n.DataFrameH\x00\x12\x17\n\x05\x63hart\x18\x04 \x01(\x0b\x32\x06.ChartH\x00\x12\x1d\n\x08progress\x18\x05 \x01(\x0b\x32\t.ProgressH\x00\x12\x1a\n\x04imgs\x18\x06 \x01(\x0b\x32\n.ImageListH\x00\x12 \n\ndoc_string\x18\x07 \x01(\x0b\x32\n.DocStringH\x00\x12\x1f\n\texception\x18\x08 \x01(\x0b\x32\n.ExceptionH\x00\x12\x13\n\x03map\x18\t \x01(\x0b\x32\x04.MapH\x00\x42\x06\n\x04typeb\x06proto3')
  ,
  dependencies=[Text__pb2.DESCRIPTOR,DataFrame__pb2.DESCRIPTOR,Chart__pb2.DESCRIPTOR,Image__pb2.DESCRIPTOR,Progress__pb2.DESCRIPTOR,DocString__pb2.DESCRIPTOR,Exception__pb2.DESCRIPTOR,Empty__pb2.DESCRIPTOR,Map__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_ELEMENT = _descriptor.Descriptor(
  name='Element',
  full_name='Element',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='text', full_name='Element.text', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='empty', full_name='Element.empty', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_frame', full_name='Element.data_frame', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='chart', full_name='Element.chart', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='progress', full_name='Element.progress', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='imgs', full_name='Element.imgs', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='doc_string', full_name='Element.doc_string', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exception', full_name='Element.exception', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='map', full_name='Element.map', index=8,
      number=9, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='type', full_name='Element.type',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=147,
  serialized_end=418,
)

_ELEMENT.fields_by_name['text'].message_type = Text__pb2._TEXT
_ELEMENT.fields_by_name['empty'].message_type = Empty__pb2._EMPTY
_ELEMENT.fields_by_name['data_frame'].message_type = DataFrame__pb2._DATAFRAME
_ELEMENT.fields_by_name['chart'].message_type = Chart__pb2._CHART
_ELEMENT.fields_by_name['progress'].message_type = Progress__pb2._PROGRESS
_ELEMENT.fields_by_name['imgs'].message_type = Image__pb2._IMAGELIST
_ELEMENT.fields_by_name['doc_string'].message_type = DocString__pb2._DOCSTRING
_ELEMENT.fields_by_name['exception'].message_type = Exception__pb2._EXCEPTION
_ELEMENT.fields_by_name['map'].message_type = Map__pb2._MAP
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['text'])
_ELEMENT.fields_by_name['text'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['empty'])
_ELEMENT.fields_by_name['empty'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['data_frame'])
_ELEMENT.fields_by_name['data_frame'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['chart'])
_ELEMENT.fields_by_name['chart'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['progress'])
_ELEMENT.fields_by_name['progress'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['imgs'])
_ELEMENT.fields_by_name['imgs'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['doc_string'])
_ELEMENT.fields_by_name['doc_string'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['exception'])
_ELEMENT.fields_by_name['exception'].containing_oneof = _ELEMENT.oneofs_by_name['type']
_ELEMENT.oneofs_by_name['type'].fields.append(
  _ELEMENT.fields_by_name['map'])
_ELEMENT.fields_by_name['map'].containing_oneof = _ELEMENT.oneofs_by_name['type']
DESCRIPTOR.message_types_by_name['Element'] = _ELEMENT

Element = _reflection.GeneratedProtocolMessageType('Element', (_message.Message,), dict(
  DESCRIPTOR = _ELEMENT,
  __module__ = 'Element_pb2'
  # @@protoc_insertion_point(class_scope:Element)
  ))
_sym_db.RegisterMessage(Element)


# @@protoc_insertion_point(module_scope)
