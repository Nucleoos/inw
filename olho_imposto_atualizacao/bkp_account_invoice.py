
from openerp.osv import osv, fields
import decimal_precision as dp
from openerp.osv import orm
import logging

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns ={
                'total_federal_valor':fields.float('Valor Aprox. Tributos Imp. Federais(R$)', readonly=True),
                'total_federal_perc':fields.float('Valor Aprox. Tributos Imp. Federais(%)', readonly=True),
                'total_estadual_valor': fields.float('Valor Aprox. Tributos Estaduais(R$)', readonly=True),
                'total_estadual_perc': fields.float('Valor Aprox. Tribualiq_nac_federaltos Estaduais(%)',readonly=True),
                'total_municipal_valor': fields.float('Valor Aprox. Tributos Municipais(R$)',readonly=True),
                'total_municipal_perc': fields.float('Valor Aprox. Tributos Municipais(%)', readonly=True),
               }    
    
    def create(self, cr, uid, result, context=None):
        if 'invoice_line' in result or 'abstract_line_ids' in result:
            if 'invoice_line' in result:
                if result['invoice_line']:
                    invoice_line = result['invoice_line']
                else:
                    invoice_line = result['abstract_line_ids']
            else:
                invoice_line = result['abstract_line_ids']
            tot_trib_fed=0
            tot_trib_estadual = 0
            tot_trib_municipal=0
            total = 0
            
            for line in invoice_line:
                if type(line[2]) == dict:
                    tot_trib_fed += line[2]['vl_tot_federal']
                    tot_trib_estadual += line[2]['vl_tot_estadual']
                    tot_trib_municipal += line[2]['vl_tot_municipal']
                    total += line[2]['quantity'] * line[2]['price_unit']
                else:     
                    obj = self.pool.get('account.invoice.line').browse(cr, uid, line[2][0])
                    tot_trib_fed += obj.vl_tot_federal
                    tot_trib_estadual += obj.vl_tot_estadual
                    tot_trib_municipal += obj.vl_tot_municipal
                    total += obj.quantity * obj.price_unit
                
                total=1	 
                result['total_federal_valor'] = tot_trib_fed
                result['total_federal_perc']= (tot_trib_fed / total) * 100
                result['total_estadual_valor'] = tot_trib_estadual
                result['total_estadual_perc'] = (tot_trib_estadual / total) * 100
                result['total_municipal_valor'] = tot_trib_municipal
                result['total_municipal_perc'] = (tot_trib_municipal /total) * 100
                valor_total = tot_trib_fed + tot_trib_estadual + tot_trib_municipal
                percentual_total = result['total_federal_perc'] + result['total_estadual_perc']+result['total_municipal_perc']
                tmp_string = 'Valor aproximado dos tributos R$ %f (%f) Fonte:IBPT'
                result['commment'] = tmp_string % ( valor_total, percentual_total)

        return super(account_invoice, self).create(cr, uid, result, context=context)
    
    def write(self, cr, uid, ids, result, context=None):
        linhas = self.pool.get('account.invoice.line')
        t = 0
        if 'invoice_line' in result or 'abstract_line_ids' in result:
            obj = self.browse(cr, uid, ids)
            if 'invoice_line' in result:
                if result['invoice_line']:
                    invoice_line = result['invoice_line']
                else:
                    invoice_line = obj[0].invoice_line
                    t = 1
            else:
                if result['abstract_line_ids']:
                    invoice_line = result['abstract_line_ids']
                else:
                    invoice_line = obj[0].abstract_line_ids
                    t = 1
            tot_trib_fed=0
            tot_trib_estadual = 0
            tot_trib_municipal=0
            total = 0
            if t == 1:
                for line in invoice_line:
                    if line:
                        l = linhas.browse(cr, uid, line.id, context=context)
                        tot_trib_fed=l.vl_tot_federal
                        tot_trib_estadual = l.vl_tot_estadual
                        tot_trib_municipal=l.vl_tot_municipal
                        total += l.price_total
                    
            else:
                for line in invoice_line:
                    if line[1]:
                        l = linhas.browse(cr, uid, line[1], context=context)
                        tot_trib_fed=l.vl_tot_federal
                        tot_trib_estadual = l.vl_tot_estadual
                        tot_trib_municipal=l.vl_tot_municipal
                        total += l.price_total
                    else:
                        tot_trib_fed=line[2]['vl_tot_federal']
                        tot_trib_estadual = line[2]['vl_tot_estadual']
                        tot_trib_municipal=line[2]['vl_tot_municipal']
#                        imp_valor += line[2]['valor_total_imp']
                        total += line[2]['price_total']
            if tot_trib_fed>0 or tot_trib_estadual>0 or tot_trib_municipal>0:
                result['total_federal_valor'] = tot_trib_fed
                result['total_federal_perc']= (tot_trib_fed / total) * 100
                result['total_estadual_valor'] = tot_trib_estadual
                result['total_estadual_perc'] = (tot_trib_estadual / total) * 100
                result['total_municipal_valor'] = tot_trib_municipal
                result['total_municipal_perc'] = (tot_trib_municipal /total) * 100
                valor_total = tot_trib_fed + tot_trib_estadual + tot_trib_municipal
                percentual_total = result['total_federal_perc'] + result['total_estadual_perc']+result['total_municipal_perc']
                tmp_string = 'Valor aproximado dos tributos R$ %f (%f) Fonte:IBPT'
                result['commment'] = tmp_string % ( valor_total, percentual_total)




        return super(account_invoice, self).write(cr, uid, ids, result, context=context)
    
account_invoice()
    
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
                'vl_tot_federal': fields.float('Valor Aprox. Trib. Nac. Federais'),
                'vl_tot_estadual': fields.float('Valor Aprox. Tributos Estaduais'),
                'vl_tot_municipal': fields.float('Valor Aprox Tributos Municipais'),
                'vl_tot_federal_readonly': fields.float('Valor Aprox. Trib. Nac. Federais',readonly=True),
                'vl_tot_estadual_readonly': fields.float('Valor Aprox. Tributos Estaduais',readonly=True),
                'vl_tot_municipal_readonly': fields.float('Valor Aprox Tributos Municipais',readonly=True),
                }
    
    def write(self, cr, uid, ids, result, context=None):
        q = 0
        p = 0
        inv_line = self.browse(cr, uid, ids, context=context)
        if 'quantity' in result:
            q = result['quantity']
            p = inv_line.price_unit
        elif 'price_unit' in result:
            q = inv_line.quantity
            p = result['price_unit']
        if 'quantity' in result or 'price_unit' in result:
            inv_line = self.browse(cr, uid, ids, context=context)[0]
            aliq_estadual = inv_line.product_id.property_fiscal_classification.aliq_estadual
            aliq_municipal = inv_line.product_id.property_fiscal_classification.aliq_municipal
            vl_trib_est = ((q * p) * aliq_estadual) / 100
            vl_trib_mun = ((q * p) * aliq_municipal) / 100
            
            if inv_line.product_id.origin == '0':
                aliq_fed  = inv_line.product_id.property_fiscal_classification.aliq_nac_federal
            else:
                aliq_fed = inv_line.product_id.property_fiscal_classification.aliq_imp_federal
                
            vl_trib_fed = ((q * p) * aliq_fed) / 100                    

            result['vl_tot_federal'] = vl_trib_fed
            result['vl_tot_estadual'] = vl_trib_est
            result['vl_tot_municipal'] = vl_trib_mun
            
            
            result['vl_tot_federal_readonly'] = vl_trib_fed
            result['vl_tot_estadual_readonly'] = vl_trib_est
            result['vl_tot_municipal_readonly'] = vl_trib_mun
        return super(account_invoice_line, self).write(cr, uid, ids, result, context=context)
#    
#    
    def create(self, cr, uid, result, context=None):

        if 'quantity' in result or 'price_unit' in result:
            produto = self.pool.get('product.product').browse(cr, uid, result['product_id'])
            aliq_estadual = produto.property_fiscal_classification.aliq_estadual
            aliq_municipal = produto.property_fiscal_classification.aliq_municipal
            
            if produto.origin == '0':
                aliq_fed  = produto.property_fiscal_classification.aliq_nac_federal
            else:
                aliq_fed = produto.property_fiscal_classification.aliq_imp_federal
            
            
            vl_trib_fed = ((result['quantity'] * result['price_unit']) * aliq_fed) / 100
            vl_trib_est = ((result['quantity'] * result['price_unit']) * aliq_estadual) / 100
            vl_trib_mun = ((result['quantity'] * result['price_unit']) * aliq_municipal) / 100
            
            result['vl_tot_federal'] = vl_trib_fed
            result['vl_tot_estadual'] = vl_trib_est
            result['vl_tot_municipal'] = vl_trib_mun
            
            
            result['vl_tot_federal_readonly'] = vl_trib_fed
            result['vl_tot_estadual_readonly'] = vl_trib_est
            result['vl_tot_municipal_readonly'] = vl_trib_mun
        return super(account_invoice_line, self).create(cr, uid, result, context=context)
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    
    
    
