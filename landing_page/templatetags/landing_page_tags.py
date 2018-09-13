# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
from django import template
from django.apps import apps
from django.contrib.sites.models import Site
from django.utils.six.moves.urllib.parse import quote, urljoin

from django.template.base import TemplateSyntaxError, token_kwargs
from django.template.loader_tags import construct_relative_path, ExtendsNode, IncludeNode

from django.templatetags.static import StaticNode as BaseStaticNode, PrefixNode

from django.utils import timezone
import datetime
from django.conf import settings

register = template.Library()


class StaticNode(BaseStaticNode):
    @classmethod
    def handle_simple(cls, path):
        site = Site.objects.get_current()
        path = os.path.join(site.domain, path)
        if apps.is_installed('django.contrib.staticfiles'):
            from django.contrib.staticfiles.storage import staticfiles_storage
            return staticfiles_storage.url(path)
        else:
            return urljoin(PrefixNode.handle_simple("STATIC_URL"), quote(path))


def do_static(parser, token):
    """
    Joins the given path with the STATIC_URL setting.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}
    """
    return StaticNode.handle_token(parser, token)


register.tag('site_static')(do_static)
register.tag('lp_static')(do_static)


@register.tag('lp_extends')
def do_extends(parser, token):
    """
    Signal that this template extends a parent template.

    This tag may be used in two ways: ``{% extends "base" %}`` (with quotes)
    uses the literal value "base" as the name of the parent template to extend,
    or ``{% extends variable %}`` uses the value of ``variable`` as either the
    name of the parent template to extend (if it evaluates to a string) or as
    the parent template itself (if it evaluates to a Template object).
    """
    bits = token.split_contents()
    print('bits" ++++++++>', type(bits[1]))
    print('do_extends: ', token)
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    site = Site.objects.get_current()
    bits[1] = '"{0}/{1}"'.format(site.domain, bits[1].strip("'").strip('"'))
    print('parser.origin.template_name: ', parser.origin.template_name)
    bits[1] = construct_relative_path(parser.origin.template_name, bits[1])
    parent_name = parser.compile_filter(bits[1])
    print('parent_name: ----------------------->', type(parent_name), parent_name)
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    print(nodelist, parent_name)
    return ExtendsNode(nodelist, parent_name)


@register.tag('lp_include')
def do_include(parser, token):
    """
    Loads a template and renders it with the current context. You can pass
    additional context using keyword arguments.

    Example::

        {% include "foo/some_include" %}
        {% include "foo/some_include" with bar="BAZZ!" baz="BING!" %}

    Use the ``only`` argument to exclude the current context when rendering
    the included template::

        {% include "foo/some_include" only %}
        {% include "foo/some_include" with bar="1" only %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "%r tag takes at least one argument: the name of the template to "
            "be included." % bits[0]
        )
    site = Site.objects.get_current()
    bits[1] = '"{0}/{1}"'.format(site.domain, bits[1].strip("'").strip('"'))
    options = {}
    remaining_bits = bits[2:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'only':
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value
    isolated_context = options.get('only', False)
    namemap = options.get('with', {})
    bits[1] = construct_relative_path(parser.origin.template_name, bits[1])
    return IncludeNode(parser.compile_filter(bits[1]), extra_context=namemap,
                       isolated_context=isolated_context)


# by resgef
@register.simple_tag(takes_context=True)
def lp_tomorrow(context):
    EFFECTIVE_DATE_OFFSET_BY_MINUTES = 15
    effective_date = (timezone.now() + datetime.timedelta(
        days=1, minutes=EFFECTIVE_DATE_OFFSET_BY_MINUTES)).date()
    if effective_date.day > 28:
        effective_date = datetime.date(
            year=(effective_date.year if effective_date.month < 12 else effective_date.year + 1),
            month=((effective_date.month + 1) if effective_date.month < 12 else 1),
            day=1
        )
    return effective_date.strftime('%m/%d/%Y')
