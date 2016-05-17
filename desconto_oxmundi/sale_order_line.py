# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.addons import decimal_precision as dp

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'price_subtotal': 0.0,
                'price_gross': 0.0,
                'discount_value': 0.0,
            }
            
            if line.discount:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit - line.desconto
                
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price,
                line.product_uom_qty, line.order_id.partner_invoice_id.id,
                line.product_id, line.order_id.partner_id,
                fiscal_position=line.fiscal_position,
                insurance_value=line.insurance_value,
                freight_value=line.freight_value,
                other_costs_value=line.other_costs_value)
            cur = line.order_id.pricelist_id.currency_id

            res[line.id]['price_subtotal'] = taxes['total']
            res[line.id]['price_gross'] = line.price_unit * line.product_uom_qty
            res[line.id]['discount_value'] = res[line.id]['price_gross']-(price * line.product_uom_qty) 

        return res

    _columns = {
         'discount_value': fields.function(_amount_line, string='Vlr. Desc. (-)', digits_compute=dp.get_precision('Sale Price'), multi='sums'),
         'price_gross': fields.function(_amount_line, string='Vlr. Bruto', digits_compute=dp.get_precision('Sale Price'), multi='sums'),
         'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price'), multi='sums'),
         'desconto': fields.float("Desconto R$"),          

    
    }
    
   
    def on_change_desconto(self, cr, uid, ids, desconto, discount):
        res = {'value':{}}
        if desconto:
            res['value']['discount'] =  False
        return res
   
    def on_change_discount(self, cr, uid, ids, desconto, discount):
        res = {'value': {}}
        if discount:
            res['value']['desconto'] = False
        return res
   
   
sale_order_line()
