from openerp.osv import fields, osv

class account_voucher_line(osv.osv):
    _inherit =  "account.voucher.line"
    
    def write(self, cr, uid, ids, vals, context=None):
#         account = self.pool.get('account.account')
#         obj_b = self.browse(cr, uid, ids)
#         if obj_b:
#             if obj_b[0].account_id.company_id.id != obj_b[0].company_id.id:
#                 account_s = account.search(cr, uid, [('name','=',obj_b[0].account_id.name),('company_id','=',obj_b[0].company_id.id)])
#                 vals['account_id'] = account_s[0]            
        return super(account_voucher_line, self).write(cr, uid, ids, vals, context=context)
    
account_voucher_line()