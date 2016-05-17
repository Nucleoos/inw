# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
                
                
                'desconto_avista': fields.char("Desconto à vista"),
                'custo_em_real': fields.char("Custo R$"),
                'dolar_hoje': fields.char("Dolar na Ultima integração"),
                'tdcartao': fields.char("Td Cartão"),
                'juroscartao': fields.char("Juros Cartão"),
                'tipojuroscartao': fields.char("Tipo do Juros Cartão"),
                'valorminimoparcela': fields.char("Valor minimo da parcela"),
                'placatipo': fields.char("Tipo da Placa"),
                'fabricante': fields.char("Fabricante"),
                'numerodeportas': fields.char("Numero de Portas"),
                'color': fields.char("Cor"),
                'tiposlot': fields.char("Tipo de Slot"),
                'modelo': fields.char("Modelo"),
                'telefone_tipo': fields.char("Tipo do Telefone"),
                
                'ncm_char': fields.char("NCM CHAR"),
                }
    
    
    def create(self, cr, uid, result, context={}):
        id = super(product_product, self).create(cr, uid, result, context)
        
        if 'ncm_char' in result:
            if result['ncm_char']:
                resultA = {}
                resultA['ncm'] = self.resolve_ncm(cr, uid, id, result['ncm_char'])
                self.write(cr, uid, id, resultA, {})
                
        return id 
    
    def write(self, cr, uid, ids, vals, context):
        
        if 'ncm_char' in vals:
            if vals['ncm_char']:
                vals['ncm'] = self.resolve_ncm(cr, uid, ids, vals['ncm_char'])
        
        return super(product_product, self).write(cr, uid, ids, vals, context)
    
    def resolve_ncm(self, cr, uid, produto_id, ncm):
        ncm_id = False
        
        ncm_instancia = self.pool.get("account.product.fiscal.classification")
        ncm_ids = ncm_instancia.search(cr, uid, ([('name', '=', ncm)]))
            
        if ncm_ids:
            ncm_id = ncm_ids[0]
        
        propert = self.pool.get("ir.property")
        
        if produto_id:
            
            if type(produto_id) == list:
                produto_id = produto_id[0]
            
            propert_ids = propert.search(cr, uid, [('res_id', '=', 'product.template,%s' %produto_id), ('name', '=', 'property_fiscal_classification')])
            
            if propert_ids:
                propert.write(cr, uid, propert_ids, {'value_reference': 'account.product.fiscal.classification,%s' %ncm_id}, {})
            else:
                dicionario = {
                              'name': 'property_fiscal_classification',
                              'res_id': 'product.template,%s' %produto_id,
                              'value_reference': 'account.product.fiscal.classification,%s' %ncm_id,
                              'type': 'many2one',
                              'fields_id': 2117,
                              }
                propert.create(cr, uid, dicionario, {})
                
            ncm_instancia.button_update_products(cr, uid, [ncm_id], {})
            
        return ncm_id
        
product_product()
    
    
    