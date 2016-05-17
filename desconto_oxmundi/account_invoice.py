from openerp.osv import osv, fields, orm
from openerp.addons import decimal_precision as dp
import time

class account_invoice(osv.osv):
    _inherit = "account.invoice"


    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_tax_discount': 0.0,
                'amount_total': 0.0,
                'icms_base': 0.0,
                'icms_value': 0.0,
                'icms_st_base': 0.0,
                'icms_st_value': 0.0,
                'ipi_base': 0.0,
                'ipi_value': 0.0,
                'pis_base': 0.0,
                'pis_value': 0.0,
                'cofins_base': 0.0,
                'cofins_value': 0.0,
                'ii_value': 0.0,
                'amount_insurance': 0.0,
                'amount_freight': 0.0,
                'amount_costs': 0.0,
                'amount_gross': 0.0,
                'amount_discount': 0.0,
            }
            for line in invoice.invoice_line:
                res[invoice.id]['icms_base'] += line.icms_base
                res[invoice.id]['icms_value'] += line.icms_value
                res[invoice.id]['icms_st_base'] += line.icms_st_base
                res[invoice.id]['icms_st_value'] += line.icms_st_value
                res[invoice.id]['ipi_base'] += line.ipi_base
                res[invoice.id]['ipi_value'] += line.ipi_value
                res[invoice.id]['pis_base'] += line.pis_base
                res[invoice.id]['pis_value'] += line.pis_value
                res[invoice.id]['cofins_base'] += line.cofins_base
                res[invoice.id]['cofins_value'] += line.cofins_value
                res[invoice.id]['ii_value'] += line.ii_value
                res[invoice.id]['amount_insurance'] += line.insurance_value
                res[invoice.id]['amount_freight'] += line.freight_value
                res[invoice.id]['amount_costs'] += line.other_costs_value
                res[invoice.id]['amount_gross'] += line.price_gross
                res[invoice.id]['amount_untaxed'] += line.price_gross - line.desconto - line.discount_value
                
                if line.discount:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                else:
                    price = line.price_unit - line.desconto
 
		if not line.ipi_cst_id.tax_discount:
                    res[invoice.id]['amount_tax'] += line.ipi_value               
                res[invoice.id]['amount_discount'] += line.price_gross - (price * line.quantity)

#            for invoice_tax in invoice.tax_line:
#                if not invoice_tax.tax_code_id.tax_discount:
#                    res[invoice.id]['amount_tax'] += invoice_tax.amount

            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res
    
    
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(
            cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
    
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(
            cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()        
    
    _columns = {
        'amount_gross': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Vlr. Bruto',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (
                    _get_invoice_line, ['price_unit',
                                        'invoice_line_tax_id',
                                        'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_discount': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Desconto',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (
                    _get_invoice_line, ['price_unit',
                                        'invoice_line_tax_id',
                                        'quantity', 'discount'], 20),
            }, multi='all'),                
        'amount_untaxed': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (
                    _get_invoice_line, ['price_unit',
                                        'invoice_line_tax_id',
                                        'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_tax': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_total': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['price_unit',
                                          'invoice_line_tax_id',
                                          'quantity', 'discount'], 20),
            }, multi='all'),
        'amount_insurance': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Valor do Seguro',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line,
                                         ['insurance_value'], 20),
            }, multi='all'),
        'amount_freight': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Valor do Seguro',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                    ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line,
                                        ['freight_value'], 20),
            }, multi='all'),
            'amount_costs': fields.function(
        _amount_all, method=True,
        digits_compute=dp.get_precision('Account'), string='Outros Custos',
        store={
            'account.invoice': (lambda self, cr, uid, ids, c={}: ids,
                                ['invoice_line'], 20),
            'account.invoice.line': (_get_invoice_line,
                                     ['other_costs_value'], 20)}, multi='all')
    }
    

    def create(self, cr, uid, vals, context={}):
        res = super(account_invoice, self).create(cr, uid, vals, context)

        if 'invoice_line' in vals:
            #if type(ids) is not list:
             #   ids = [ids]

            account_invoice_line = self.pool.get("account.invoice.line")
            for invoice in self.browse(cr, uid, [res]):

                for linha in invoice.invoice_line:
                    valor_total = linha.price_unit * linha.quantity
                    if linha.discount:
                        valor_total -= (valor_total * linha.discount)/100
                    else:
                        valor_total -= (linha.quantity * linha.desconto)

                    valor_total += linha.freight_value
                    vc = valor_total
                    vp = valor_total
                    vco = valor_total
                    vi = valor_total
                    if linha.icms_percent == 0:
                        vc = 0.00
                    if linha.pis_percent == 0:
                        vp = 0.00
                    if linha.cofins_percent == 0:
                        vco = 0.00
                    if linha.ipi_percent == 0:
                        vi = 0.00
                    dicionario = {
                                  'icms_base': vc,
                                  'icms_value': (valor_total * linha.icms_percent)/100,

                                  'pis_base': vp,
                                  'pis_value': (valor_total * linha.pis_percent)/100,

                                  'cofins_base': vco,
                                  'cofins_value': (valor_total * linha.cofins_percent)/100,

                                  'ipi_base': vi,
                                  'ipi_value': (valor_total * linha.ipi_percent)/100,
                                  }
                    account_invoice_line.write(cr, uid, linha.id, dicionario, {})

        return res

    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(account_invoice, self).write(cr, uid, ids, vals, context)       
        if type(ids) is not list:
            iid=ids
	else:
	    iid=ids[0]

        obj = self.browse(cr, uid, iid)
        if obj.type != 'in_invoice' and 'invoice_line' in vals:
            if type(ids) is not list:
                ids = [ids]
	    	
            account_invoice_line = self.pool.get("account.invoice.line")
            for invoice in self.browse(cr, uid, ids):

                for linha in invoice.invoice_line:
                    valor_total = linha.price_unit * linha.quantity
                    if linha.discount:
                        valor_total -= (valor_total * linha.discount)/100
                    else:
                        valor_total -= (linha.quantity * linha.desconto)

                    valor_total += linha.freight_value
                    vc = valor_total
                    vp = valor_total
                    vco = valor_total
                    vi = valor_total
                    if linha.icms_percent == 0:
                        vc = 0.00
                    if linha.pis_percent == 0:
                        vp = 0.00
                    if linha.cofins_percent == 0:
                        vco = 0.00
                    if linha.ipi_percent == 0:
                        vi = 0.00
                    dicionario = {
                                  'icms_base': vc,
                                  'icms_value': (valor_total * linha.icms_percent)/100,

                                  'pis_base': vp,
                                  'pis_value': (valor_total * linha.pis_percent)/100,

                                  'cofins_base': vco,
                                  'cofins_value': (valor_total * linha.cofins_percent)/100,

                                  'ipi_base': vi,
                                  'ipi_value': (valor_total * linha.ipi_percent)/100,
                                  }
                    account_invoice_line.write(cr, uid, linha.id, dicionario, {})
          
        return res
    
account_invoice() 
    
    
    
class account_invoice_tax(orm.Model):
    _inherit = "account.invoice.tax"

    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(
            cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        currenty_date = time.strftime('%Y-%m-%d')
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            
            if line.discount:
                vallor = (line.price_unit * (1 - (line.discount or 0.0) / 100.0))
            else:
                vallor = line.price_unit - (line.desconto / line.quantity)
                
            
            for tax in tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id,
                #(line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                # alterado linha de cima
                vallor,
                line.quantity, line.product_id, inv.partner_id,
                fiscal_position=line.fiscal_position,
               insurance_value=line.insurance_value,
                freight_value=line.freight_value,
                other_costs_value=line.other_costs_value)['taxes']:
                val = {}
                if inv.type == 'in_invoice' and inv.partner_id.country_id.id == inv.company_id.country_id.id and not tax['domain'] == 'icms':
                    val['invoice_id'] = inv.id
                    val['name'] = tax['name']
                    val['amount'] = ((tax.get('total_base', 0.0) + line.freight_value) * tax['percent'])#tax['amount']
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = tax.get('total_base', 0.0) + line.freight_value + line.other_costs_value
                else:
                    val['invoice_id'] = inv.id
                    val['name'] = tax['name']
                    val['amount'] = tax['amount']
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = tax.get('total_base', 0.0)

                if inv.type in ('out_invoice', 'in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid,
                        inv.currency_id.id, company_currency,
                        val['base'] * tax['base_sign'],
                        context={'date': inv.date_invoice or currenty_date},
                        round=False)
                    val['tax_amount'] = cur_obj.compute(
                        cr, uid, inv.currency_id.id, company_currency,
                        val['amount'] * tax['tax_sign'],
                        context={'date': inv.date_invoice or currenty_date},
                        round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(
                        cr, uid, inv.currency_id.id, company_currency,
                        val['base'] * tax['ref_base_sign'],
                        context={'date': inv.date_invoice or currenty_date},
                        round=False)
                    val['tax_amount'] = cur_obj.compute(
                        cr, uid, inv.currency_id.id,
                        company_currency, val['amount'] * tax['ref_tax_sign'],
                        context={'date': inv.date_invoice or currenty_date},
                        round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

account_invoice_tax()
