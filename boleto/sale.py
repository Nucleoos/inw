# -*- encoding:utf-8 -*-
from openerp.osv import osv, fields


class sale_order_line (osv.osv):
    _inherit = 'sale.order.line'

#     def _check_qtd(self, cr, uid, ids):
#         res = True
#         product_line = self.browse(cr, uid, ids[0])
#         if product_line.product_id.product_tmpl_id.type == "product":
#             res = False
#             location = self.pool.get('stock.location')
#             report = location._product_get_report(cr, uid, [product_line.order_id.shop_id.warehouse_id.lot_stock_id.id], recursive=True)
#             for product_stock in report['product']:
#                 if product_line.product_id.name == product_stock['prod_name']:
#                     if product_line.product_uom_qty > product_stock['prod_qty']:
#                         break
#                     else:
#                         res = True
#                         break
#         return res
#     _constraints = [(_check_qtd, 'A quantidade informada é maior do que a quantidade em estoque', ['Quantidade'])]

sale_order_line()
