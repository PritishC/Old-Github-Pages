# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
"""
from trytond.model import fields, ModelSQL, ModelView
from trytond.transaction import Transaction

__all__ = ['Department']


class Department(ModelSQL, ModelView):
    'Department'
    __name__ = 'company.department'

    name = fields.Char("Name", required=True)
    company = fields.Many2One('company.company', 'Company', required=True)

    @staticmethod
    def default_company():
        return Transaction().context.get('company')
