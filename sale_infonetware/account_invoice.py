# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
from datetime import datetime, date
import base64

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
   
    _columns = {     
                'enviar_email': fields.boolean('Enviar Email?'),
                'boleto':fields.boolean('Enviar boleto?'),
                'banco': fields.selection([('caixa', 'Banco BRB'), ('itau', 'Banco Itau'), ('bb', 'Banco do Brasil') ], 'Banco'), 
                }


    def onchange_boleto(self, cr, uid, ids, b, context=None):
        res = {'value':{}}
        if b:
            res['value']['banco'] = 'caixa'
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        if not 't' in context:
            if 'state' in vals:
                if vals['state'] == 'open':
                    compose = self.pool.get('mail.compose.message')
                    if type(ids) is list:
                        obj = self.browse(cr, uid, ids[0])
                        c = compose.generate_email_for_composer(cr, uid, 9, ids[0], context=context)
                    else:
                        obj = self.browse(cr, uid, ids)
                        c = compose.generate_email_for_composer(cr, uid, 9, ids, context=context)
                    if obj.enviar_email:
                        context = {
                                   'banco': obj.banco,
                                   'body': c['body'],
                                   #'anexo': c['attachments'][0][1],
                                   }
                        self.create_mail_compose(cr, uid, ids, context=context)
                        context = {
                                   't':True
                                   }
        return res
    
    def create_mail_compose(self, cr, uid, ids, context=None):
        ir_attachment            = self.pool.get('ir.attachment')
        mail_mail                = self.pool.get('mail.mail')
        mail_message             = self.pool.get('mail.message')
        boleto_boleto_create     = self.pool.get('boleto.boleto_create')
        if type(ids) is list:
            ids = ids
        else:
            ids = [ids]
        sale = self.browse(cr, uid, ids[0])
        if sale.user_id:
            if not sale.user_id.email:
                raise orm.except_orm(
                        ('Aviso'),("Usuario sem email cadastrado!"))
        if not sale.partner_id.email:
            raise orm.except_orm(
                        ('Aviso'),("Cliente sem email cadastrado!"))
        temp =  self.pool.get('email.template').browse(cr, uid, 9)
        if temp.email_cc:
            cc = temp.email_cc
        else:
            cc = ''
        vals = {                         
                    'email_from': sale.user_id.email,
                    'email_to': sale.partner_id.email,
                    'email_cc' : cc,
                    'subject': '%s NFE (Ref %s)' % (sale.company_id.name, sale.number),
                    'body_html': context['body'],                        
                }
        xml = ''              
        mail_id = mail_mail.create(cr, uid, vals , context=context)
        aa = ir_attachment.search(cr, uid, [('res_id','=',ids[0])])
        if aa:
            aab = ir_attachment.browse(cr, uid, aa[0])
            xml = aab.index_content
        result2 = {
                    'db_datas':base64.b64encode(xml),#context['anexo'],
                    'type':'binary',
                    'res_name':sale.partner_id.name,
                    'company_id':sale.company_id.id,
                    'description':'Email de venda',
                    'datas_fname':u'%s.xml'%(sale.nfe_access_key),
                    'res_model':'account.invoice',
                    'name':'Venda',                        
                    }
        anexo_id = ir_attachment.create(cr, uid, result2)
        #pdf = self.str_pdf_Danfes(cr, uid, ids, context=context)
        #result6 = {
         #           'db_datas':pdf,#base64.b64encode(pdf),#context['anexo'],
          #          'type':'binary',
           #         'res_name':sale.partner_id.name,
            #        'company_id':sale.company_id.id,
            #        'description':'Email de venda',
            #        'datas_fname':u'%s.xml'%(sale.number),
            #        'res_model':'account.invoice',
            #        'name':'Venda',                        
            #        }
        #anexo_id6 = ir_attachment.create(cr, uid, result6)
        ret = 0
        salee    = self.pool.get('account.invoice').browse(cr, uid, ids[0], context=context)
        company    = self.pool.get('res.company').browse(cr, uid, [salee.company_id.id])[0]
        if salee.boleto:
            for bol_conf_id in company.boleto_company_config_ids:
                if bol_conf_id.banco == context['banco']:
                    ret = bol_conf_id.id
            if ret == 0:
                raise orm.except_orm(
                            ('Aviso'),("Empresa sem configuracao de boleto"))
            context['boleto_company_config_ids'] = ret
            boleto = boleto_boleto_create.create_boleto(cr, uid, ids, context)
            result3 = {
                        'db_datas':boleto,
                        'type':'binary',
                        'res_name':sale.partner_id.name,
                        'company_id':sale.company_id.id,
                        'description':'Email de venda',
                        'datas_fname':u'Boleto_%s.pdf'%(sale.name),
                        'res_model':'account.invoice',
                        'name':'Boleto Venda',                        
                        }
            anexo_id2 = ir_attachment.create(cr, uid, result3)
        message = {
                    'subject': '%s NFe (Ref %s)' % (sale.company_id.name, sale.number),
                     'author_id': uid,
                    'date': date.today(),
                    'type': 'email',
                    }
        message_id = mail_message.create(cr, 1, message)
        if salee.boleto:
            mail_mail.write(cr, 1, int(mail_id), {'attachment_ids': [(6, 0, [anexo_id,anexo_id2])], 
                                                    'mail_message_id': int(message_id)}, context=context)
        else:
            mail_mail.write(cr, 1, int(mail_id), {'attachment_ids': [(6, 0, [anexo_id])], 
                                                    'mail_message_id': int(message_id)}, context=context)
        send_mail = mail_mail.send(cr, 1, [int(mail_id)], context=context)
   
account_invoice()

