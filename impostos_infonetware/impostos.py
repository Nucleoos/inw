# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_tax(osv.osv):
    _inherit = 'account.tax'

    _columns = {
                'domain_select': fields.selection([
                                            ('icms','ICMS'),
                                            ('pis','PIS'),
                                            ('cofins','COFINS'),
                                            ('ipi','IPI'),
                                            ('iss','ISS'),
                                            ],'Domínio'),
                }


account_tax()

class account_tax_code(osv.osv):
    _inherit = 'account.tax.code'

    _columns = {
                'domain_select': fields.selection([
                                            ('icms','ICMS'),
                                            ('pis','PIS'),
                                            ('cofins','COFINS'),
                                            ('ipi','IPI'),
                                            ('iss','ISS'),
                                            ],'Domínio'),
                }


account_tax_code()
