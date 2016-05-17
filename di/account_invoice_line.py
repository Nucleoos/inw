# -*- encoding: utf-8 -*-
from openerp.osv import  fields, osv, orm
from openerp.addons import decimal_precision as dp
import time
from openerp.osv import osv, fields, orm

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
                'import_declaration_ids': fields.one2many('declaracao.importacao','invoice_line_id', u'Declaração de Importação'), 
                 }
    
    def create(self, cr, uid, vals, context=None):
        if 'invoice_line_tax_id' in vals:
            for imp in self.pool.get('account.tax').browse(cr, uid, vals['invoice_line_tax_id'][0][2]):
                if imp.ii_imposto:
                    vals['ii_base'] = vals['quantity'] * vals['price_unit']
                    vals['ii_value'] = vals['ii_base'] * imp.amount
        return super(account_invoice_line, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        iid = False
        if not context:
            context = {}
        if 't' in context:
            return super(account_invoice_line, self).write(cr, uid, ids, vals, context=context)
        vals['ii_base'] = 0 
        vals['ii_value'] = 0
        res = super(account_invoice_line, self).write(cr, uid, ids, vals, context=context)
        if type(ids) == list:
            if ids:
                iid = ids[0]
        else:
            iid = ids
        if iid:
            obj = self.browse(cr, uid, iid)
            if obj.invoice_id.company_id.country_id.id == obj.invoice_id.partner_id.country_id.id:
                if not 't' in context:
                    if obj.invoice_line_tax_id:
                        for imp in obj.invoice_line_tax_id:
                            if imp.ii_imposto:
                                dict = {
                                        'ii_base': obj.quantity * obj.price_unit,
                                        'ii_value': (obj.quantity * obj.price_unit) * imp.amount
                                        }
                                context = {'t':True}
                                self.write(cr, uid, ids, dict, context=context)
            else:
                if obj.invoice_id.origin and obj.invoice_id.type == 'in_invoice':
                    compra_s = self.pool.get('purchase.order').search(cr, uid, [('name','=', obj.invoice_id.origin)])
                    if compra_s:
                        compra_b = self.pool.get('purchase.order').browse(cr, uid, compra_s[0])
                        for c in compra_b.order_line:
                            if c.product_id.id == obj.product_id.id and c.product_qty == obj.quantity:
                                context = {'t':True}
                                dict = {
                                        'icms_base': c.icms_s,
                                        'icms_value': c.icms,
                                        'ipi_base': c.base_ipi,
                                        'ipi_value': c.ipi,
                                        'pis_base': c.base_pis,
                                        'pis_value': c.pis,
                                        'cofins_base': c.base_cofins,
                                        'cofins_value': c.cofins,
                                        'ii_base': c.base_ii,
                                        'ii_value': c.ii
                                        }
                                self.write(cr, uid, ids, dict, context=context)
        return res
                    
        
    
account_invoice_line()

class account_tax(osv.osv):
    _inherit = 'account.tax'
    
    _columns = {
                'ii_imposto': fields.boolean('Imposto para II')
                }
    
account_tax()

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
                elif inv.type == 'in_invoice' and inv.partner_id.country_id.id != inv.company_id.country_id.id:
                    if inv.origin:
                        compra_s = self.pool.get('purchase.order').search(cr, uid, [('name','=', inv.origin)])
                        if compra_s:
                            compra_b = self.pool.get('purchase.order').browse(cr, uid, compra_s[0])
                            for c in compra_b.order_line:
                                if c.product_id.id == line.product_id.id and c.product_qty == line.quantity:
                                    if tax['domain'] == 'pis':
                                        val['invoice_id'] = inv.id
                                        val['name'] = tax['name']
                                        val['amount'] = c.pis#tax['amount']
                                        val['manual'] = False
                                        val['sequence'] = tax['sequence']
                                        val['base'] = c.base_pis
                                    
                                    elif tax['domain'] == 'cofins':
                                        val['invoice_id'] = inv.id
                                        val['name'] = tax['name']
                                        val['amount'] = c.cofins#tax['amount']
                                        val['manual'] = False
                                        val['sequence'] = tax['sequence']
                                        val['base'] = c.base_cofins
                                    
                                    elif tax['domain'] == 'ipi':
                                        val['invoice_id'] = inv.id
                                        val['name'] = tax['name']
                                        val['amount'] = c.ipi#tax['amount']
                                        val['manual'] = False
                                        val['sequence'] = tax['sequence']
                                        val['base'] = c.base_ipi
                                    
                                    elif tax['domain'] == 'ii' or tax['domain'] == False:
                                        val['invoice_id'] = inv.id
                                        val['name'] = tax['name']
                                        val['amount'] = c.ii#tax['amount']
                                        val['manual'] = False
                                        val['sequence'] = tax['sequence']
                                        val['base'] = c.base_ii
                                        
                                    elif tax['domain'] == 'icms':
                                        val['invoice_id'] = inv.id
                                        val['name'] = tax['name']
                                        val['amount'] = c.icms#tax['amount']
                                        val['manual'] = False
                                        val['sequence'] = tax['sequence']
                                        val['base'] = c.icms_s
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