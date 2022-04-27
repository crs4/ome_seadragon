#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import settings
class Configuration:
    def __getattr__(self, attr):
        return getattr(settings, attr)

