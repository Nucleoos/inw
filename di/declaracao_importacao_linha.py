# -*- encoding: utf-8 -*-
from openerp.osv import  fields, osv
from openerp.addons import decimal_precision as dp

class declaracao_importacao_linha(osv.osv):
    _name = 'declaracao.importacao.linha'
    _columns = {
        'declaracao_importacao_id': fields.many2one('declaracao.importacao', u'DI', ondelete='cascade', select=True),
        'sequence': fields.integer(u'Sequência'),
        'name': fields.char(u'Adição', size=3, required=True),
        'manufacturer_code': fields.char(u'Código do Fabricante', size=3, required=True),
        'amount_discount': fields.float(u'Valor de Desconto', digits_compute=dp.get_precision('Account')),
    }
    _defaults = {
        'amount_discount': 0.00,
    }
declaracao_importacao_linha()