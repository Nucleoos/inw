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
class cartao_bandeira(osv.osv):
    _name="cartao.bandeira"
    _columns={
              'name': fields.char('Bandeira', size=128, help="Bandeira do cartão", required=True),
              'reference': fields.char('Refêrencia', size=3, required=True),
              'write_date_taxa': fields.datetime('Data da Modificação', readonly=True),
              'write_uid_taxa' : fields.many2one('res.users', 'Modificado por', required=False, select=1, readonly=True),
              }
    _defaults={
               'write_uid_taxa' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
               'write_date_taxa': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
               }
cartao_bandeira()

class account_voucher(osv.osv):
    _inherit="account.voucher"
    _columns={
                'cartoes_bandeiras': fields.many2one('cartao.bandeira', 'Bandeiras do Cartão'),
                'tipo_pagamento': fields.selection([('vista','À vista'),
                                                    ('0', 'Boleto'),
                                                    ('1', 'Cartão de Débito'),
                                                    ('2', 'Cartão de Crédito'),
                                                    ], 
                                                   'Forma de Pagamento',
                                                   required=True,
                                                   help="Selecione a forma de pagamento")
              }
    _defaults={
               'tipo_pagamento': '0'
               }
account_voucher()