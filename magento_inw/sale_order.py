# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm

class sale_order(osv.osv):
    
    _inherit = 'sale.order'
    
    
    def create(self, cr, uid, result, context={}):
        res = super(sale_order, self).create(cr, uid, result, context)
        
        fiscal_position = False
        if 'fiscal_position' in result:
            fiscal_position = result['fiscal_position']
        
            
        if not fiscal_position:
            

            context = {'uid': uid, 'default_type': 'invoice'}
            resultt = {'value': {}}
            
            kwargs = {
                    'shop_id': result['shop_id'],
                    'partner_id': result['partner_id'],
                    'partner_invoice_id': result['partner_invoice_id'],
                    'partner_shipping_id': result['partner_shipping_id'],
                    'context': context,
                    'fiscal_category_id': result['fiscal_category_id']
            }
            retorno = self._fiscal_position_map(cr, uid, resultt, **kwargs)
            
    
            if not retorno['value']['fiscal_position']:
                raise orm.except_orm(
                ('Posição Fiscal !'),
                ("Posição Fiscal para este cliente não foi encontrada"))

            self.write(cr, uid, res, {'fiscal_position':retorno['value']['fiscal_position']}, {})
    
        return res
    
sale_order()