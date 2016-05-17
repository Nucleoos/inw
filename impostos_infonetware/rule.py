# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_fiscal_position_rule(osv.osv):
    _inherit = 'account.fiscal.position.rule'
   
    _columns = {
                
                }
    
    def onchange_country(self, cr, uid, ids, context=None):
        res = {'value':{}}
        res['value']['from_state'] = False
        res['value']['to_invoice_state'] = False
        return res
    
account_fiscal_position_rule()
