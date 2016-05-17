# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2011  Vinicius Dittgen - PROGE, Leonardo Santagada - PROGE      #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from openerp.osv import fields, osv
from datetime import datetime, date


class boleto_create(osv.osv):

    _inherit = 'boleto.boleto_create'

    def criar_boletos(self, cr, uid, context=None):
        fatura = self.pool.get('account.invoice')
        fatura_s = fatura.search(cr, uid, [('name','=','CTT')])
        contrato = self.pool.get('sale.recurring_orders.agreement')
        today = str(date.today())
        t = 01#today[8:]
#        contrato_s = contrato.search(cr ,uid , [('start_date','<=',date.today())])
        for f in fatura.browse(cr, uid, fatura_s):
            ids = f.id
            v = str(f.date_due)
            d = 01 #v[8:]
            if t == d:
                self.create_boleto(cr,uid,ids)

#        return boleto

boleto_create()
