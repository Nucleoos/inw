# -*- coding: utf-8 -*-

{
    'name' :'Desconto Real ou porcentagem',
    'version' :' 1.0',
    'author' : 'Roberto Santos',
    'website' : 'http://www.inwgroup.com.br',
    'description': 'Este modulo adiciona um campo de desconto tipo float na linha da venda',
    'depends':['sale', 'l10n_br_sale', 'account', 'l10n_br_account', 'l10n_br_delivery'],
    'update_xml': ['sale_order_view.xml',
                   'account_invoice_line_view.xml',],
    'installable': True,
    'auto_install': True,
}