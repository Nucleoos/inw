# -*- encoding: utf-8 -*-
# 
# Copyright (C) 2009  Infonetware Hardware & Software Solutions                        
#                                                                                                                          
# This program is free software: you can redistribute it and/or modify                  
# it under the terms of the GNU Affero General Public License as published by   
# the Free Software Foundation, either version 3 of the License, or                         
# (at your option) any later version.                                                                       
#                                                                                                                          
# This program is distributed in the hope that it will be useful,                           
# but WITHOUT ANY WARRANTY; without even the implied warranty of               
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              
# GNU General Public License for more details.                                                      
#                                                                                                                          
# You should have received a copy of the GNU General Public License            
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 
'''
Created on 12/08/2014

@author: Bruno
'''
from openerp.osv import fields, osv
import time
import datetime
from datetime import datetime, date
import calendar

class taxas(osv.osv):
    _name = "taxas.taxas"
    _columns = {
                'banco': fields.many2one('res.bank', 
                                         'Banco',
                                         required=True, 
                                         help="Escolha o banco"),
                'ativar_taxas': fields.boolean('Ativar Taxas'),
                'tipo_pagamento': fields.selection([('0', 'Boleto'),
                                                    ('1', 'Cartão de Débito'),
                                                    ('2', 'Cartão de Crédito'),
                                                    ], 
                                                   'Forma de Pagamento',
                                                   required=True,
                                                   help="Selecione a forma de pagamento"
                                                   ),
                'bandeira_cartao': fields.many2one('cartao.bandeira', 'Bandeira do Cartão', required=False),
                'valor_fixo': fields.float('Valor Fixo', 
                                           digits=(12,2),
                                           required=True,
                                           help="Digite o valor fixo da taxa, caso o mesmo não exista, manter em 0.00"),
                'percentual_valor': fields.float('Percentual da taxa (%)',
                                                 required=True,
                                                 help="Digite o valor percentual da taxa, caso a mesma não exista, manter em 0.00"),
                'write_date_taxa': fields.datetime('Data da Modificação', readonly=True),
                'write_uid_taxa' : fields.many2one('res.users', 'Modificado por', required=False, select=1, readonly=True),
                'campo_invisivel': fields.boolean('Readonly', readonly=True),
                }
    _defaults={
               'tipo_pagamento': '0',
               'bandeira_cartao': "",
               'campo_invisivel': False,
               'write_uid_taxa' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
               'write_date_taxa': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
               }
    
    def on_change_boleto(self, cr, uid, ids, forma_pagamento, context=None ):
        res = {'value':{}}
        if forma_pagamento == '0':
            res['bandeira_cartao'] = ''
        return { 'value': res }
    
    def write(self, cr, uid, ids, vals, context=None):
        return super(taxas, self).write(cr, uid, ids, vals, context)
    
    def create(self, cr, uid, vals, context=None):
        obj_brw = self.pool.get('taxas.taxas')
        if obj_brw.search(cr, uid, [
                                    ('banco', '=', vals['banco']), 
                                    ('tipo_pagamento', '=', vals['tipo_pagamento']),
                                    ('bandeira_cartao', '=', vals['bandeira_cartao'])
                                    ]):
            raise osv.except_osv(("Atenção"), ("Esta taxa já está cadastrada neste banco, favor verificar"))
        vals['campo_invisivel'] = True
        return super(taxas, self).create(cr, uid, vals, context=context)
    
taxas()