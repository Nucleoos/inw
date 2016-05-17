# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from unicodedata import normalize
from datetime import date, datetime, timedelta
import base64


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    _columns = {
                'valor_unit_dolar': fields.float('Valor Unitario($)',digits=(12,4)),
                'valor_proforma': fields.float('Valor Proforma($)',digits=(12,4)),
                'data_proforma': fields.date('Data Proforma'),
                'cotacao_proforma': fields.float('Cotação Proforma',digits=(12,4)),
                'cambio': fields.float('Cambio($)'),
                'data_cambio':fields.date('Data Cambio'),
                'cotacao_cambio': fields.float('Cotação Cambio',digits=(12,4)),
                
                'di_adicao': fields.integer('DI_Adições'),
                'taxa_siscomex': fields.float('Taxa Siscomex'),
                'cotacao_cambio_di': fields.float('Cotação Cambio DI',digits=(12,4)),
                'data_di': fields.date('Data DI'),
                
                'armazenagem': fields.float('Valor de Armazenagem'),
                'carregamento': fields.float('Valor Carregamento'),
                'documento': fields.float('Logistica Documento'),
                'despachante': fields.float('Despachante'),
                'outras_despesas': fields.float('Outras despesas(cambio)'),
                
                'valor_total': fields.float('Valor Total'),
                
                'base_pis': fields.float('base'),
                'pis': fields.float('Pis'),
                'base_cofins': fields.float('base'),
                'cofins': fields.float('Cofins'),
                'base_ipi': fields.float('base'),
                'ipi':fields.float("IPI"),
                'icms_p': fields.float('Icms Primario'),
                'icms_s': fields.float('Icms Secundario'),
                'icms': fields.float("ICMS"),     
                'base_ii': fields.float('base'),          
                'ii': fields.float('II'),
                }
    
    def onchange_taxa(self, cr, uid, ids, adicoes, context=None):
        uid = 1
        res = {'value':{}}
        tabela = self.pool.get('tabela.siscomex')
        if adicoes > 0:
            tabela_s = tabela.search(cr, uid, [('adicoes','=',adicoes)])
            if tabela_s:
                obj = tabela.browse(cr, uid, tabela_s[0])
                res['value']['taxa_siscomex'] = obj.valor
        return res
    
    def onchange_unit(self, cr, uid, ids, qty, unit, ts, ar, crr, doc, dp, od, vp, tdi, taxes, vud, context=None):
        res = {'value':{}}
        if taxes:
            ii_ok = False
            percent_icms=0
            for t in self.pool.get('account.tax').browse(cr, uid, taxes[0][2]):
                if t.ii_imposto:
                    percent_ii = t.amount     
                    ii_ok = True   
                elif t.domain == 'ipi':  
                    percent_ipi = t.amount
                elif t.domain == 'pis':
                    percent_pis = t.amount
                elif t.domain == 'cofins':
                    percent_cofins = t.amount
                elif t.domain == 'icms':
                    percent_icms = t.amount
            if ii_ok:
                
		vii = ((vud * qty) * tdi) * percent_ii
                res['value']['ii'] = vii
               	# vu = vii + (vud * tdi) + ts + ar + crr + doc + dp + od
                vu=(vud * tdi) + (vii / qty)
            
		if unit != vu:
                    res['value']['price_unit'] = vu
                res['value']['valor_total'] = qty * vu
                
		#calculo II
                imp_ii_base = vud * qty
                imp_ii = (imp_ii_base * percent_ii) * tdi
                res['value']['ii'] = imp_ii
                res['value']['base_ii'] = imp_ii_base
                # calculo ipi
                imp_ipi_base = (imp_ii_base * tdi) + imp_ii
                imp_ipi = imp_ipi_base * percent_ipi
                res['value']['ipi'] = imp_ipi
                res['value']['base_ipi'] = imp_ipi_base
                #calculo pis
                imp_pis_base = (vud * tdi) * qty
                imp_pis = imp_pis_base * percent_pis
                res['value']['pis'] = imp_pis
                res['value']['base_pis'] = imp_pis_base
                #calculo cofins
                imp_cofins_base = (vud * tdi) * qty
                imp_cofins = imp_cofins_base * percent_cofins
                res['value']['cofins'] = imp_cofins
                res['value']['base_cofins'] = imp_cofins_base
                #calculo ICMS
                imp_icms_base1 = (vud * tdi * qty) + imp_ii + imp_ipi + imp_pis + imp_cofins + ts
                imp_icms_base2 = imp_icms_base1 / 0.88
                imp_icms = imp_icms_base2 * percent_icms
                res['value']['icms'] = imp_icms
                res['value']['icms_p'] = imp_icms_base1
                res['value']['icms_s'] = imp_icms_base2
            else:
                raise orm.except_orm(_('Aviso'), _('Nao encontrado imposto de importacao!'))
        return res
        
purchase_order_line()

class tabela_siscomex(osv.osv):
    _name = 'tabela.siscomex'
    
    _columns = {
                'adicoes': fields.integer('Numero de adições'),
                'valor': fields.float('Valor da Taxa Siscomex')
                }
    
tabela_siscomex()

