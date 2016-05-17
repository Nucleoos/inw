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


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'boleto_partner_config': fields.many2one('boleto.partner_config', u'Configurações de Boleto do Parceiro'),
        'only': fields.boolean('Deixar campo Estado e Municipio READONLY outros paises'),
        }

    _defaults = {
                  'boleto_partner_config': lambda self, cr, uid, c: self.pool.get('boleto.partner_config').search(cr, uid, [('default_boleto', '=', True)])[0]
                  }



res_partner()


class mail_mail(osv.osv):
    _inherit = 'mail.mail'
    _columns = {
		'name': fields.char('Nome',64)
		}
mail_mail()
