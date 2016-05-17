# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
                'order_policy': fields.selection([('manual', 'On Demand'),
                                                  ('picking', 'On Delivery Order'),
                                                  ('prepaid', 'Before Delivery'),
                                                  ('nota_futura', 'Nota Fatura'),], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                                 help="""On demand: A draft invoice can be created from the sales order when needed. \nOn delivery order: A draft invoice can be created from the delivery order when the products have been delivered. \nBefore delivery: A draft invoice is created from the sales order and must be paid before the products can be delivered."""),
                'nota_futura_emitida': fields.boolean("Nota futura emitida"),
                }
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        sale_order_brw = self.browse(cr, uid, ids[0])
        marcador = False
        
        if sale_order_brw.order_policy == 'nota_futura':
            self.write(cr, uid, ids, {'order_policy': 'picking'}, context)
            marcador = True
            
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        
        if marcador:
            self.write(cr, uid, ids, {'order_policy': 'nota_futura'}, context)
        return res

    def cria_fatura_futura(self, cr, uid, ids, context={}):
        res = self.action_invoice_create(cr, uid, ids)
        if res:
            self.write(cr, uid, ids, {'nota_futura_emitida': True}, context)
        return res
sale_order()




# 
#    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
#         """ open a view on one of the given invoice_ids """
#         ir_model_data = self.pool.get('ir.model.data')
#         form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
#         form_id = form_res and form_res[1] or False
#         tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
#         tree_id = tree_res and tree_res[1] or False
# 
#         return {
#             'name': _('Advance Invoice'),
#             'view_type': 'form',
#             'view_mode': 'form,tree',
#             'res_model': 'account.invoice',
#             'res_id': invoice_ids[0],
#             'view_id': False,
#             'views': [(form_id, 'form'), (tree_id, 'tree')],
#             'context': "{'type': 'out_invoice'}",
#             'type': 'ir.actions.act_window',
#         }
