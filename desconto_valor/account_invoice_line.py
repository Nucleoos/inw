# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
   
    _columns = {     
                'desconto': fields.float("Desconto R$"),          
                }
    
    def create(self, cr, uid, result, context):
        
        if 'discount' in result:
            if result['discount']:
                result['desconto'] = ((result['price_unit'] * result['quantity']) * result['discount']) / 100
        
        return super(account_invoice_line, self).create(cr, uid, result, context)
    
   
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
                    aux = ((valor_unitario * quantidade) * discount) / 100
                    if "%.2f" %desconto != "%.2f" %aux:
                        res['value']['desconto'] = aux  
        return res
   
   
account_invoice_line()
