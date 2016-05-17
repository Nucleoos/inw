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

{
    "name": "Boletos",
    "version": "0.1",
    "author": "Jefferson Tito",
    "category": "Account",
    'depends': ['l10n_br_account','base', 'sale'],
    'init_xml': [],
    'update_xml': [
        # 'boleto_view.xml',
        'partner_view.xml',
        'res_company_view.xml',
        'wizard/boleto_create_view.xml',
#         'sale_view.xml',
#         'account_voucher.xml',
#         'sequence_boleto.xml',
#         'product_view.xml',
        'boleto_partner_config.xml',
        'account_invoice.xml',
#         'taxas_view.xml',
        'account_journal_view.xml',
#         'cartao_bandeira_view.xml'
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
