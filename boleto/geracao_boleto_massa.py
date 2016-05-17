# -*- uncoding: utf-8 -*-
from openerp.osv import osv, fields
from datetime import date, datetime, timedelta
from unicodedata import normalize
import locale    
import calendar

class geracao_boleto_massa(osv.osv):
    _name="geracao.boleto.massa"
    
    def gerar_boleto_mass2(self, cr, uid, *args): 
        
        account_invoice          = self.pool.get('account.invoice')
        boleto_boleto_create     = self.pool.get('boleto.boleto_create')
        boleto_company_config    = self.pool.get('boleto.company_config')
        ir_attachment            = self.pool.get('ir.attachment')
        mail_mail                = self.pool.get('mail.mail')
        mail_message             = self.pool.get('mail.message')
        account_analytic_due_day = self.pool.get("account.analytic.due.day")
        account_analytic_account = self.pool.get("account.analytic.account")
        
        itau          = 0
        cef           = 0
        context       = {}
        msg_retorno   = []
        lista_produto = ''
        hoje          = date.today()         
        hoje = datetime.strptime('2014-05-10', '%Y-%m-%d').date()
        mail_servicos = []
        
        #filtro de dias de vencimento  
        if hoje.day < 10:   
            dia_pesq = '0' + str(hoje.day)
        else:
            dia_pesq = str(hoje.day) 
                 
        venc_id = account_analytic_due_day.search(cr, uid, [('name','>=', dia_pesq)])
        if venc_id:
            venc_id = '(' + str(venc_id)[1:-1] + ')'
            query = "select id from account_analytic_account where type = 'contract' and \
                     state in ('ATV', 'PBL', 'BLQ', 'TSU', 'ACL') and due_day in %s" %venc_id
            cr.execute(query)
            contrato_ids = cr.fetchall()
            if contrato_ids:
                for contrato_id in contrato_ids:
                    contrato       = account_analytic_account.browse(cr, uid, contrato_id[0])
                    try:
                        date_due       = datetime.strptime(hoje.strftime("%Y-%m") + '-' + str(contrato.due_day.name), '%Y-%m-%d').date()                        
                    except:
                        ultimo_dia_mes = calendar.monthrange(int(hoje.strftime("%Y")),int(hoje.strftime("%m")))[1]
                        date_due       = datetime.strptime(hoje.strftime("%Y-%m") + '-' + str(ultimo_dia_mes), '%Y-%m-%d').date()   
                    data_boleto    = date_due - timedelta(days = contrato.billet_days)
                    if data_boleto < hoje:
                        continue
                    if contrato.company_id.id == contrato.partner_id.boleto_partner_config.preferencia.sequence.company_id.id:
                        id_config_boleto = contrato.partner_id.boleto_partner_config.preferencia.id
                    else:
                        continue                   
                
                lista_faturas = account_invoice.search(cr, uid,[('origin','=', contrato.code), 
                                                                ('date_due','=', date_due)])
                
                if lista_faturas:
                    if  cef != 0:
                        context['boleto_company_config_ids'] = cef
                    elif itau != 0:
                        context['boleto_company_config_ids'] = itau
                    context['company_id'] = contrato.company_id.id
                    
                    boleto = boleto_boleto_create.create_boleto(cr, uid, lista_faturas, context)
                    
                    lista_produtos = context['lista']
                    for i in lista_produtos:
                        i = normalize('NFKD',unicode(i)).encode('ASCII','ignore'),
                        mail_servicos.append(str(unicode(i[0])))
                    
                    # Configurações do usuário
                    locale.setlocale(locale.LC_ALL, '')     
                    data_servico = date_due - timedelta(days = 30)
                    
                    body   = normalize('NFKD',unicode("""
             Para sua maior comodidade e para aprimorar nosso atendimento, estamos alterando nosso modelo de cobrança. A partir de agora enviaremos nossos boletos de cobrança anexados em nossos e-mails, dessa forma não será mais necessário baixa-lo de um link. Alem disso, listaremos os serviços associados a cobrança no e-mail enviado. Com isso acreditaremos que será mais facil associar o boleto aos serviços prestados.<br/>
             <p/>
             </p>
             
             Segue em anexo o boleto de cobrança com vencimento no dia %s, referente aos serviços de:<br>
             <br/>
             %s 
             
             
             <br/>
             O boleto diz respeito ao servico prestado no mes de %s de %s.
             
             Qualquer duvida sinta-se a vontade para nos contactar no telefone (99) 9999-9999.<br/>
             Atenciosamente,<br/>
             Departamento Financeiro <br/>
             financeiro@iconecta.com.br </br> 
             <b> www.iconecta.com.br <b/><br/>
             +55 (99) 9999-9999 <br/>
             
             
             """ %(datetime.strftime(date_due, "%d-%m-%Y"),
                   mail_servicos,
                   data_servico.strftime("%B"), 
                   data_servico.year))).encode('UTF-8','ignore'),
                   
                    vals = {                         
                                'email_from': u'carlosfink@gmail.com',
                                'email_to': contrato.partner_id.email,
                                'email_cc' : u'carlos.fink@infonetware.com.br',
                                'subject': u'Boleto de cobrança de serviços',
                                'body_html': body[0],                        
                            }
                      
                    mail_id = mail_mail.create(cr, uid, vals , context=context)
                      
                    result2 = {
                                'db_datas':boleto,
                                'type':'binary',
                                'res_name':contrato.partner_id.name,
                                'company_id':contrato.company_id.id,
                                'description':'Boleto gerado automaticamente.',
                                'datas_fname':u'%s_%s.pdf'%(contrato.partner_id.name,date.today()),
                                'res_model':'account.analytic.account',
                                'name':'Boleto',                        
                                }
                    anexo_id = ir_attachment.create(cr, uid, result2)
                    message = {
                                'subject': u'Boleto de cobrança de serviços',
                                 'author_id': 1,
                                'date': date.today(),
                                'type': 'email',
                                }
                    message_id = mail_message.create(cr, uid, message)
                    mail_mail.write(cr, uid, int(mail_id), {'attachment_ids': [(6, 0, [anexo_id])], 
                                                            'mail_message_id': int(message_id)}, context=context)
                    send_mail = mail_mail.send(cr, uid, [int(mail_id)], context=context)
#                 account_analytic_account.write(cr, uid, [fatura.id], {'number': fatura.internal_number})
#              else:
#                   
#                 msg_retorno.append('Nao foi encontrado a configuracao do boleto na fatura %s') %contrato.name
                
#             mail_b = mail_mail.browse(cr, uid, int(mail_id))
#           if mail_b.state == 'sent':
#               result = {
#                        'enviado':'t'
#                        }
#               account_invoice.write(cr, uid, fatura.id,result)
#           else:
#               local_name="/var/log/openerp_boletos/log_%s_.txt"  % date.today()
#               var_file=open(local_name,'w')
#               var_file.write('Erro ao enviar o boleto referente a fatura %s do cliente %s em %s' % (fatura.internal_number,fatura.partner_id.name,str(date.today())))
#               var_file.close()
#     if msg_retorno:
#         local_name="/var/log/openerp_boletos/log_%s_.txt"  % date.today()
#         var_file=open(local_name,'w')
#         for linha in msg_retorno:
#             var_file.write(linha)
#         var_file.close()
        return True
    
geracao_boleto_massa()
