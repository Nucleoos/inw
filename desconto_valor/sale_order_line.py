# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
   
    _columns = {     
                'desconto': fields.float("Desconto R$"),          
                }
    
   
    def on_change_desconto(self, cr, uid, ids, valor_unitario, quantidade, desconto, discount, context={}):
        res = {'value':{}}
        
        if type(desconto) is not float:
            desconto = float(desconto)
            
        if type(discount) is not float:
            discount = float(discount)

        if 'name' in context:
            if valor_unitario:
                if context['name'] == 'desconto':
                    aux = (desconto / (valor_unitario * quantidade)) * 100
                    if "%.2f" %discount != "%.2f" %aux:
                        res['value']['discount'] = aux
                elif context['name'] == 'discount' or context['name'] == 'price_unit':
                    aux = ((valor_unitario * quantidade) * float(str(discount)[:5])) / 100
                    if "%.2f" %desconto != "%.2f" %aux:
                        res['value']['desconto'] = aux    
        return res
   
   
sale_order_line()
