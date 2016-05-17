# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from tools.translate import _


class product_product(osv.osv): 
    
    _inherit =  "product.product"

    _columns = {
                'billet_name' : fields.char('Descrição Boleto', size=32),    
                'produto_multa': fields.boolean('Produto Usado para Cobrança de Multa?'),            
                }
    
    def create(self, cr, uid, result, context=None):
        if 'produto_multa' in result:
            if result['produto_multa']:
                prod = self.search(cr, uid, [('produto_multa','=',True)])
                if prod:
                    raise osv.except_osv(_('Atenção!'),_("Já existe um produto cadastrado para cobrança de multa de cancelamento,não é permitido cadastrar dois produtos!"))
        return super(product_product, self).create(cr, uid, result, context=context)
    
    def write(self, cr, uid, ids, result, context=None):
        if 'produto_multa' in result:
            if result['produto_multa']:
                prod = self.search(cr, uid, [('produto_multa','=',True)])
                if prod:
                    raise osv.except_osv(_('Atenção!'),_("Já existe um produto cadastrado para cobrança de multa de cancelamento,não é permitido cadastrar dois produtos!"))
        return super(product_product, self).write(cr, uid, ids, result, context=context)
    
product_product()