# -*- coding: utf-8  -*-
    
from openerp.osv import osv, fields
from openerp.addons import decimal_precision as dp



def  calc_price_ratio(price_gross, amount_calc, amount_total):
    if not amount_total or amount_total == 0:
        amount_total = 1
    return price_gross * amount_calc / amount_total

class sale_order(osv.osv):
    
    _inherit = "sale.order"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_extra': 0.0,
                'amount_discount': 0.0,
                'amount_gross': 0.0,
            }
            val = val1 = val2 = val3 = val4 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                val2 += (line.insurance_value + line.freight_value + line.other_costs_value)
                val3 += line.discount_value or line.desconto
                val4 += line.price_gross
            res[order.id]['amount_tax'] = val
            res[order.id]['amount_untaxed'] = val1
            res[order.id]['amount_extra'] = val2
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + res[order.id]['amount_extra']
            res[order.id]['amount_discount'] = val3
            res[order.id]['amount_gross'] = val4
        return res
    
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()    
    
    _columns = {
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The total amount."),
        'amount_extra': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Extra',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The total amount."),
        'amount_discount': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Desconto (-)',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The discount amount."),
        'amount_gross': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Vlr. Bruto',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The discount amount."),
        'amount_freight': fields.float('Frete',
             digits_compute=dp.get_precision('Account'), readonly=True,
                               states={'draft': [('readonly', False)]}),
        'amount_costs': fields.float('Outros Custos',
            digits_compute=dp.get_precision('Account'), readonly=True,
                               states={'draft': [('readonly', False)]}),
        'amount_insurance': fields.float('Seguro',
            digits_compute=dp.get_precision('Account'), readonly=True,
                               states={'draft': [('readonly', False)]}),
        'discount_rate': fields.float('Desconto', readonly=True,
                               states={'draft': [('readonly', False)]}),
        }
    
    
    def onchange_amount_freight(self, cr, uid, ids, amount_freight=False):
        result = {}
        if (amount_freight is False) or not ids:
            return {'value': {'amount_freight': 0.00}}
        
        line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=None):
            valor = 0
            if order.order_line:
                if len(order.order_line) > 1:
                    linha_id = order.order_line[-1].id
                else:
                    linha_id = order.order_line[0]
                for line in order.order_line:
                    desc_linha = calc_price_ratio(line.price_gross, amount_freight, order.amount_gross)
                    desc_linha = float("%.2f" %desc_linha)
                    valor += desc_linha
                    if line.id == linha_id:
                        if valor != amount_freight:
                            diferenca = amount_freight - valor
                            desc_linha += diferenca
                    line_obj.write(cr, uid, [line.id], {'freight_value': desc_linha}, context=None)
            
        return result