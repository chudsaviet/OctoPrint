# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function, \
	division

__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Copyright (C) 2018 The OctoPrint Project - Released under terms of the AGPLv3 License"

import copy
import re

__registry = dict()

def _register_command_class(cls):
	__registry[cls.__name__] = cls

def to_command(line, type=None, tags=None, **kwargs):
	if isinstance(line, Command):
		return line

	for cls in __registry.values():
		if cls.pattern:
			# noinspection PyUnresolvedReferences,PyProtectedMember
			if isinstance(cls.pattern, re._pattern_type) and cls.pattern.match(line):
				return cls.from_line(line, type=type, tags=tags, **kwargs)
			elif callable(cls.pattern) and cls.pattern(line):
				return cls.from_line(line, type=type, tags=tags, **kwargs)

	return Command.from_line(line, type=type, tags=tags, **kwargs)

class CommandMetaClass(type):
	def __new__(mcs, *args, **kwargs):
		c = type.__new__(mcs, *args, **kwargs)
		_register_command_class(c)
		return c

class Command(object):
	__metaclass__ = CommandMetaClass

	pattern = None

	@classmethod
	def from_line(cls, line, type=None, tags=None, **kwargs):
		return cls(line, type=type, tags=tags, **kwargs)

	def __init__(self, line, type=None, tags=None, **kwargs):
		if tags is None:
			tags = set()

		self.line = line
		self.type = type
		self.tags = tags

	def __repr__(self):
		return "{}({!r},type={!r},tags={!r})".format(self.__class__.__name__, self.line, self.type, self.tags)

	def __str__(self):
		return self.line

	def __key(self):
		return self.line, self.type

	def __eq__(self, other):
		return self.__key() == other.__key()

	def __hash__(self):
		return hash(self.__key())

	def with_type(self, type):
		c = copy.deepcopy(self)
		c.type = type
		return c

	def with_tags(self, tags):
		if tags is None:
			return self

		c = copy.deepcopy(self)
		c.tags |= tags
		return c
