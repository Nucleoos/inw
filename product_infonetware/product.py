# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'ncm': fields.many2one('account.product.fiscal.classification','NCM'),

        'cadastro': fields.selection([
                                            ('dados','Faltam dados'),
                                            ('ok','Cadastro Ok'),
                                            ],'Status'),
        }

    _sql_constraints = [('product_product_name_uniq', 'unique(default_code)', u'Já existe um produto com esse Codigo!') ]

    def create(self, cr, uid, vals, context=None):
        vals['company_id'] = False
	if 'default_code' in vals:
            if vals['default_code']:
                code = self.search(cr, uid, [('default_code','=',vals['default_code'])])
                if code:
                    raise orm.except_orm(
                        ('Aviso'),("Esse SKU ja esta cadastrado"))
        return super(product_product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        obj = self.browse(cr, uid, ids[0])
        if 'default_code' in vals:
            if vals['default_code']:
                code = self.search(cr, uid, [('default_code','=',vals['default_code']),('id','!=',ids[0])])
                if code:
                    raise orm.except_orm(
                        ('Aviso'),("Esse SKU ja esta cadastrado"))
        vals['ncm'] = obj.property_fiscal_classification.id
        if obj.cadastro == 'dados':
            if 'property_fiscal_classification' in vals:
                if vals['property_fiscal_classification']:
                    vals['cadastro'] = 'ok'
                    vals['ncm'] = vals['property_fiscal_classification']
                else:
                    vals['cadastro'] = 'dados'
        return super(product_product, self).write(cr, uid, ids, vals, context=context)


product_product()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def create(self, cr, uid, vals, context=None):
        if 'name' in vals:
            if vals['name']:
                code = self.search(cr, uid, [('name','=',vals['name'])])
                if code:
                    raise orm.except_orm(
                        ('Aviso'),("Numero de serie %s ja cadastrado" % (vals['name'])))
        return super(stock_production_lot, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'name' in vals:
            if vals['name']:
                code = self.search(cr, uid, [('name','=',vals['name'])])
                if code:
                    raise orm.except_orm(
                        ('Aviso'),("Numero de serie %s ja cadastrado" % (vals['name'])))
        return super(stock_production_lot, self).write(cr, uid, ids, vals, context=context)


stock_production_lot()
