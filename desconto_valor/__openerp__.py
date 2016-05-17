# -*- coding: utf-8 -*-

{
    'name' :'Desconto por Valor',
    'version' :' 1.0',
    'author' : 'Roberto Santos',
    'website' : 'http://www.inwgroup.com.br',
    'description': 'Este modulo adiciona um campo de desconto tipo float na linha da venda',
    'depends':['sale'],
    'update_xml': ['sale_order_view.xml', 'account_invoice_view.xml'],
    'installable': True,
    'auto_install': True,
}