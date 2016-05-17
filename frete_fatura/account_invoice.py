# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
   
    _columns = {     
                'frete_fatura': fields.boolean("Colocar Frete Direto na Fatura"),
                'valor_frete': fields.float('Valor do Frete'),          
                'vendedor': fields.many2one('res.users','Vendedor Responsavel'),      
		}

    def onchange_frete(self, cr, uid, ids, valor, ff, context=None):
        t = 0
        if ff:
            if valor > 0:
                obj = self.browse(cr, uid, ids[0])
                if obj:
                    linhas = len(obj.invoice_line)
                    valor_linha = float(valor) / float(linhas)
                    for i in obj.invoice_line:
                        dict = {
                                'freight_value': float(valor_linha)
                                }
                        self.pool.get('account.invoice.line').write(cr, uid, i.id, dict, context=context)
                    d = {
                         'amount_freight': float(valor)
                         }
                    self.write(cr, uid, ids, d)
                    conta_frete = obj.company_id.account_freight_id.id
                    cr.execute('delete from account_invoice_tax where account_id = %s' % (conta_frete))
                    tax = {
                           'tax_amount': valor,
                           'account_id':conta_frete,
                           'sequence':1,
                           'invoice_id': obj.id,
                           'manual': False,
                           'company_id': obj.company_id.id,
                           'base_amount': obj.amount_total,
                           'amount': float(valor),
                           'base': obj.amount_total,
                           'name': 'Frete'
                           }
                    self.pool.get('account.invoice.tax').create(cr, uid, tax)
            else:
                t = 1 
        else:
            t = 1
        if t == 1:
            obj = self.browse(cr, uid, ids[0])
            cr.execute('delete from account_invoice_tax where account_id = %s' % (conta_frete))
            for i in obj.invoice_line:
                dict = {
                        'freight_value': 0
                        }
                self.pool.get('account.invoice.line').write(cr, uid, i.id, dict, context=context)
            d = {
                 'amount_freight': float(valor)
                 }
            self.write(cr, uid, ids, d)
	obj2 = self.browse(cr, uid, ids[0])
        if obj2.type == 'in_invoice':
            dd = {
                  'check_total':obj2.amount_total
                  }
            self.write(cr, uid, ids, dd)
        return True
    
    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('account.invoice.tax')
        obj = self.browse(cr, uid, ids[0])
        conta_frete = obj.company_id.account_freight_id.id
        for id in ids:
            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False AND account_id != %s", (id,conta_frete))
            partner = self.browse(cr, uid, id, context=ctx).partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                ait_obj.create(cr, uid, taxe)
        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
        return True
   
account_invoice()
