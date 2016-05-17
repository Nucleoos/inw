# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class nfee_export(osv.osv):
    _name = "nfee.export"
    
    _columns = {
                                
                'de': fields.date("De"),
                'ate': fields.date("Até"),
                'empresa_id': fields.many2one("res.company", "Empresa"),
                'state': fields.selection([('xml_autorizado', 'XML - Autorizados'),
                                            ('xml_cancelados', 'XML - Cancelados'),
                                            ('xml_cartacorrecao', 'XML - Carta de correção'),
                                            ('xml_estornodenegado', 'XML - Estorno ou denegado'),
                                            ('pdf_autorizado', 'PDF - Autorizadas'),
                                            ('pdf_estornodenegado', 'PDF - Estornos')], "Status"),
                
                }
    
    
    
    def gerar(self, cr, uid, ids, context={}):
        
        account_invoice = self.pool.get("account.invoice")
        
        for brw in self.browse(cr, uid, ids):
            
            status = brw.state.split("_")
            
            lista_ids = self.obtem_ids(cr, uid, account_invoice, brw, status[1])
            
            if lista_ids:
                
                if status[0] == 'pdf':
                    return account_invoice.invoice_print(cr, uid, [lista_ids[0]], {'active_ids': lista_ids})
                
                elif status[0] == 'xml':
                    nfe_export_invoice = self.pool.get('l10n_br_account.nfe_export_invoice')
                    nfe_export_invoice_id = nfe_export_invoice.create(cr, uid, {'export_folder': False, 'file_type': 'xml', 'nfe_environment': '1'}, {})
                    return nfe_export_invoice.nfe_export(cr, uid, [nfe_export_invoice_id], {'active_ids': lista_ids, 'exportador': True, 'state': status[1]})
                    
                
        return True
    
    
    def obtem_ids(self, cr, uid, account_invoice, brw, status):
        lista = []
        if status in ['autorizado', 'cancelados', 'estornodenegado']:
            tupla = self.obtem_lista_status(brw, status)
            lista = account_invoice.search(cr, uid, tupla, {})
        elif status in ['cartacorrecao']:
            lista = self.executa_query(cr, brw, status)
            
        return lista
        
    def obtem_lista_status(self, brw, status):
        lista = []
        
        if status == 'autorizado':
            lista = [('company_id', '=', brw.empresa_id.id), ('fiscal_type', '=', 'product'), ('type', '=', 'out_invoice'), ('date_hour_invoice', '>=', brw.de), ('date_hour_invoice', '<=', brw.ate), '|', ('state', '=', 'open'), ('state', '=', 'paid')]
        
        elif status == 'cancelados':
            lista = [('company_id', '=', brw.empresa_id.id), ('fiscal_type', '=', 'product'), ('type', '=', 'out_invoice'), ('date_hour_invoice', '>=', brw.de), ('date_hour_invoice', '<=', brw.ate), ('state', '=', 'sefaz_cancelled')]
        
        elif status == 'estornodenegado':
            lista = [('company_id', '=', brw.empresa_id.id), ('fiscal_type', '=', 'product'), ('type', '=', 'out_refund'), ('date_hour_invoice', '>=', brw.de), ('date_hour_invoice', '<=', brw.ate), '|', ('state', '=', 'open'), ('state', '=', 'paid')]

        return lista
        
    def executa_query(self, cr, brw, status):
        if status == 'cartacorrecao':
            query = """select distinct(ai.id) from l10n_br_account_invoice_cce aic
                       inner join account_invoice ai on aic.invoice_id = ai.id
                       where ai.date_invoice >= '%s' and ai.date_invoice <= '%s' and ai.company_id = %s""" %(brw.de, brw.ate, brw.empresa_id.id)
        cr.execute(query)
        
        aux = cr.fetchall()
        lista = []
        for tuple in aux:
            lista.append(tuple[0]) 
            
        return lista
nfee_export()
