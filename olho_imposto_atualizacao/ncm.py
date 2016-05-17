##############################################################################
#
# Copyright (c) 2008-2009 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields,osv


class account_product_fiscal_classification(osv.osv):
    _inherit = "account.product.fiscal.classification"
    
    _columns = {
                
                'aliq_nac_federal': fields.float('Aliquota Nacional Federal(%)', required=True),
                'aliq_imp_federal': fields.float('Aliquota Importada Federal(%)', required=True),
        		'aliq_estadual': fields.float('Aliquota Estadual(%)', required=True),
        		'aliq_municipal': fields.float('Aliquota Municipal(%)',required=True),                
                }
    
account_product_fiscal_classification()
