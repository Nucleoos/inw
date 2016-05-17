# -*- coding: utf-8 -*-

{
    'name' :'Declaração de Importação - Odoo v7',
    'version' :' 1.0',
    'author' : 'Jefferson Tito/Roberto Santos',
    'website' : 'http://www.inwgroup.com.br',
    'description': """
        Modulo que adiciona a opção de DI
    
    """,
    'depends':['base','l10n_br_account'],
    'data':  [
             'account_invoice_line_view.xml',
             'res_partner_view.xml',
             'compras_view.xml',
	     'di_view.xml',
             
             
             #data file
             'dados/estado_dados.xml',
             'dados/cidade_dados.xml',
             
             ],
    'installable': True,
    'auto_install': False,
}
