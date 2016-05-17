# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm

class sale_order_line(osv.osv):
    
    _inherit = 'sale.order.line'
    
    
    def create(self, cr, uid, result, context={}):
        res = super(sale_order_line, self).create(cr, uid, result, context)
        
        fiscal_position = False
        if 'fiscal_position' in result:
            fiscal_position = result['fiscal_position']
        
            
        if not fiscal_position:
            
            sale_order_brw = self.pool.get("sale.order").browse(cr, uid, result['order_id'])
            
            
            tt = {"value": {}}
            
            kwargs = {
                        'shop_id': sale_order_brw.shop_id.id,
                        'partner_id': sale_order_brw.partner_id.id,
                        'partner_invoice_id': sale_order_brw.partner_invoice_id.id,
                        'fiscal_category_id': sale_order_brw.fiscal_category_id.id,
                        'context': {},
            }
            tt = self._fiscal_position_map(cr, uid, tt, **kwargs)
            
            if not tt['value']['fiscal_position']:
                raise orm.except_orm(
                ('Posição Fiscal !'),
                ("Posição Fiscal para este cliente não foi encontrada"))
                
            
            tax_id = self.onchange_fiscal_position(cr, uid, [], sale_order_brw.partner_id.id, sale_order_brw.partner_invoice_id.id, sale_order_brw.shop_id.id, result['product_id'], tt['value']['fiscal_position'], sale_order_brw.fiscal_category_id.id)
            taxas_tupla = [(6, 0, tax_id['value']['tax_id'])]
            
            self.write(cr, uid, res, {'fiscal_category_id' : sale_order_brw.fiscal_category_id.id, 'fiscal_position' : tt['value']['fiscal_position'], 'tax_id': taxas_tupla}, {})
        return res
    
sale_order_line()