# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.addons import decimal_precision as dp

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
   
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'discount_value': 0.0,
                'price_gross': 0.0,
                'price_subtotal': 0.0,
                'price_total': 0.0,
            }
            
            if line.discount:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit - line.desconto
            
            taxes = tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id, price, line.quantity,
                line.product_id, line.invoice_id.partner_id,
                fiscal_position=line.fiscal_position,
                insurance_value=line.insurance_value,
                freight_value=line.freight_value,
                other_costs_value=line.other_costs_value)

            if line.invoice_id:
                currency = line.invoice_id.currency_id
                price_gross = cur_obj.round(cr, uid, currency,
                        line.price_unit * line.quantity)
                res[line.id].update({
                    'price_subtotal': taxes['total'] - taxes['total_tax_discount'],#cur_obj.round(
                        #cr, uid, currency,
                        #taxes['total'] - taxes['total_tax_discount']),
                    'price_total': taxes['total'],#cur_obj.round(
                       # cr, uid, currency, taxes['total']),
                    'price_gross': price_gross,
                    'discount_value': (price_gross - taxes['total']),
                })

        return res

    _columns = {
        'discount_value': fields.function(
            _amount_line, method=True, string='Vlr. desconto', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_total': fields.function(
            _amount_line, method=True, string='Total', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_gross': fields.function(
            _amount_line, method=True, string='Vlr. Bruto', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_subtotal': fields.function(
            _amount_line, method=True, string='Subtotal', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'price_total': fields.function(
            _amount_line, method=True, string='Total', type="float",
            digits_compute=dp.get_precision('Account'),
            store=True, multi='all'),
        'desconto': fields.float("Desconto R$"),          
        }
    
    def create(self, cr, uid, result, context):
        
        if 'origin' in result:
            if result['origin']:
                if result['origin'][:1] == 'S':
                    sale_order = self.pool.get("sale.order")
                    sale_order_id = sale_order.search(cr, uid, [('name', '=', result['origin'])])
                    if sale_order_id:
                        sale_order_brw = sale_order.browse(cr, uid, sale_order_id)[0]
                                  
                        for linha in sale_order_brw.order_line:
                            if linha.product_id.id == result['product_id']:
                                result['desconto'] = linha.desconto
                                break
        
        return super(account_invoice_line, self).create(cr, uid, result, context)
    
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
   
account_invoice_line()
