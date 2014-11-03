# -*- coding: utf-8 -*-
"""
    tests/test_employee.py

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
from trytond.transaction import Transaction
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.error import UserError


class TestEmployee(unittest.TestCase):
    '''
    Test Employee model
    '''
    def setUp(self):
        """
        Obtain models from POOL for use.
        This method is called before each test function
        is executed.
        """
        self.Party = POOL.get('party.party')
        self.Company = POOL.get('company.company')
        self.Department = POOL.get('company.department')
        self.Designation = POOL.get('employee.designation')
        self.Employee = POOL.get('company.employee')
        self.Currency = POOL.get('currency.currency')

    def setup_basics(self):
        """
        Set up some basic models.
        """
        self.currency, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])
        self.party, = self.Party.create([{'name': 'Openlabs'}])
        self.party_emp, = self.Party.create([{'name': 'Pritish C'}])
        self.company, = self.Company.create([{
            'party': self.party.id,
            'currency': self.currency.id,
        }])

    def _populate_department(self):
        """
        Create department and designations.
        """
        self.department, = self.Department.create([{
            'name': 'IT',
            'company': self.company.id
        }])
        self.desig1, = self.Designation.create([{
            'name': 'Sr Software Developer',
            'department': self.department.id
        }])
        self.desig2, = self.Designation.create([{
            'name': 'Software Dev Trainee',
            'department': self.department.id
        }])

    def test0001employee_creation(self):
        """
        Test dummy employee.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as transaction:
            self.setup_basics()
            self._populate_department()
            transaction.set_context(company=self.company.id)

            self.employee, = self.Employee.create([{
                'party': self.party_emp.id,
                'company': self.company.id,
                'gender': 'male',
                'designation': self.desig2.id,
                'department': self.department.id,
                'dob': '1992-08-08',
                'pan': '1234567891',
                'passport': '123456789',
                'driver_id': 'ABCD1234',
            }])

            self.assert_(self.employee)

            self.employee, = self.Employee.create([{
                'party': self.party_emp.id,
                'company': self.company.id,
                'designation': self.desig2.id,
                'department': self.department.id,
                'dob': '1992-08-08',
                'pan': '1234567890',
                'passport': '123456780',
                'driver_id': 'ABCD123',
            }])

            self.assertEquals(self.employee.gender, 'male')

            self.department2, = self.Department.create([{
                'name': 'IT',
            }])

            self.assertEquals(self.department.company, self.company)

    def test0005employee_uniqueness(self):
        """
        Cannot create employees where unique fields are the same.
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_basics()
            self._populate_department()

            self.employee, = self.Employee.create([{
                'party': self.party_emp.id,
                'company': self.company.id,
                'gender': 'male',
                'designation': self.desig2.id,
                'department': self.department.id,
                'dob': '1992-08-08',
                'pan': '1234567891',
                'passport': '123456789',
                'driver_id': 'ABCD1234',
            }])

            # PAN can't be the same.
            self.assertRaises(UserError, self.Employee.create, [{
                'party': self.party_emp.id,
                'company': self.company.id,
                'gender': 'male',
                'designation': self.desig2.id,
                'department': self.department.id,
                'dob': '1992-08-08',
                'pan': '1234567891',
                'passport': '987654321',
                'driver_id': 'DCB4321',
            }])
            # Passport can't be the same.
            self.assertRaises(UserError, self.Employee.create, [{
                'party': self.party_emp.id,
                'company': self.company.id,
                'gender': 'male',
                'designation': self.desig2.id,
                'department': self.department.id,
                'dob': '1992-08-08',
                'pan': '9876543219',
                'passport': '123456789',
                'driver_id': 'ADCB4321',
            }])

            # Driver's license ID can't be the same.
            self.assertRaises(UserError, self.Employee.create, [{
                'party': self.party_emp.id,
                'company': self.company.id,
                'gender': 'male',
                'designation': self.desig2.id,
                'department': self.department.id,
                'dob': '1992-08-08',
                'pan': '1234567811',
                'passport': '987654321',
                'driver_id': 'ABCD1234',
            }])


