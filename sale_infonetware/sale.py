# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from unicodedata import normalize
from datetime import date, datetime, timedelta
import base64

from pyboleto.bank.real import BoletoReal
from pyboleto.bank.itau import BoletoItau
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixa
from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.pdf import BoletoPDF
from datetime import datetime, date
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
   
    _columns = {
                'fiscal_position': fields.many2one(
                            'account.fiscal.position', 'Posição Fiscal',
                            domain="[('fiscal_category_id','=',fiscal_category_id)]",
                            readonly=True, states={'draft': [('readonly', False)],
                                'sent': [('readonly', False)]}),
                }
    
sale_order_line()
    
class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
                'fiscal_position': fields.many2one(
                                        'account.fiscal.position', 'Posição Fiscal',
                                        domain="[('fiscal_category_id', '=', fiscal_category_id)]",
                                        readonly=True, states={'draft': [('readonly', False)],
                                            'sent': [('readonly', False)]}),
                'incoterm': fields.many2one('stock.incoterms', 'Modo de Entrega', help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
                'vencimento': fields.date('Data de Vencimento de Boleto'),
                'boleto':fields.boolean('Enviar boleto?'),
                'banco': fields.selection([('caixa', 'Banco BRB'), ('itau', 'Banco Itau'), ('bb', 'Banco do Brasil') ], 'Banco'),
                }

    def onchange_boleto(self, cr, uid, ids, b, context=None):
        res = {'value':{}}
        if b:
            res['value']['banco'] = 'caixa'
        return res
    
    def create(self, cr, uid, result, context={}):
        if 'carrier_id' in result:
            if result['carrier_id']:
                delivery_carrier_brw = self.pool.get('delivery.carrier').browse(cr, uid, result['carrier_id'])
                
                if delivery_carrier_brw.magento_code == 'correios':
                    nova_linhas = []
                    for linha in result['order_line']:
                        if linha[2]['product_id'] == delivery_carrier_brw.product_id.id:
                            result['amount_freight'] = linha[2]['price_unit']
                        else:
                            nova_linhas.append(linha)
        
                    result['order_line'] = nova_linhas
    
        return super(sale_order, self).create(cr, uid, result, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        obj = self.browse(cr, uid, ids[0])
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if obj.company_id.id != user.company_id.id:
            raise orm.except_orm(
                        ('Aviso'),("Pedido de venda feito na empresa %s por favor mudar sua Preferencia!" % (obj.company_id.name)))
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        sale = self.browse(cr, uid, ids[0])
        if 'state' in vals:
            if vals['state'] == 'manual':
                if sale.boleto:
                    if not context:
                        context = {}
                    compose = self.pool.get('mail.compose.message')
                    c = compose.generate_email_for_composer(cr, 1, 6, ids[0], context=context)
                    context.update({
                                'body': c['body'],
                                'anexo': c['attachments'][0][1],
                                'banco': sale.banco,
                            })
                    cc = self.create_mail_compose(cr, uid, ids, context=context)
        return res

    def create_mail_compose(self, cr, uid, ids, context=None):
        ir_attachment            = self.pool.get('ir.attachment')
        mail_mail                = self.pool.get('mail.mail')
        mail_message             = self.pool.get('mail.message')
        boleto_boleto_create     = self.pool.get('boleto.boleto_create')
        sale = self.browse(cr, uid, ids[0])
        if not sale.user_id.email:
            raise orm.except_orm(
                        ('Aviso'),("Usuario sem email cadastrado!"))
        if not sale.partner_id.email:
            raise orm.except_orm(
                        ('Aviso'),("Cliente sem email cadastrado!"))
        temp =  self.pool.get('email.template').browse(cr, uid, 6)
        if temp.email_cc:
            cc = temp.email_cc
        else:
            cc = ''
        vals = {                         
                    'email_from': sale.user_id.email,
                    'email_to': sale.partner_id.email,
                    'email_cc' : cc,
                    'subject': '%s Pedido de Venda (Ref %s)' % (sale.company_id.name, sale.name),
                    'body_html': context['body'],                        
                }
                      
        mail_id = mail_mail.create(cr, uid, vals , context=context)
        result2 = {
                    'db_datas':context['anexo'],
                    'type':'binary',
                    'res_name':sale.partner_id.name,
                    'company_id':sale.company_id.id,
                    'description':'Email de venda',
                    'datas_fname':u'%s.pdf'%(sale.name),
                    'res_model':'sale.order',
                    'name':'Venda',                        
                    }
        anexo_id = ir_attachment.create(cr, uid, result2)
        ret = 0
        salee    = self.pool.get('sale.order').browse(cr, uid, ids[0], context=context)
        company    = self.pool.get('res.company').browse(cr, uid, [salee.company_id.id])[0]
        for bol_conf_id in company.boleto_company_config_ids:
            if bol_conf_id.banco == context['banco']:
                ret = bol_conf_id.id
        if ret == 0:
            raise orm.except_orm(
                        ('Aviso'),("Empresa sem configuracao de boleto"))
        context['boleto_company_config_ids'] = ret
        boleto = boleto_boleto_create.create_boleto_venda(cr, uid, ids, context)
        result3 = {
                    'db_datas':boleto,
                    'type':'binary',
                    'res_name':sale.partner_id.name,
                    'company_id':sale.company_id.id,
                    'description':'Email de venda',
                    'datas_fname':u'Boleto_%s.pdf'%(sale.name),
                    'res_model':'sale.order',
                    'name':'Boleto Venda',                        
                    }
        anexo_id2 = ir_attachment.create(cr, uid, result3)
        message = {
                    'subject': '%s Pedido de Venda (Ref %s)' % (sale.company_id.name, sale.name),
                     'author_id': uid,
                    'date': date.today(),
                    'type': 'email',
                    }
        message_id = mail_message.create(cr, 1, message)
        mail_mail.write(cr, 1, int(mail_id), {'attachment_ids': [(6, 0, [anexo_id,anexo_id2])], 
                                                'mail_message_id': int(message_id)}, context=context)
        send_mail = mail_mail.send(cr, 1, [int(mail_id)], context=context)


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(purchase_order, self).write(cr, uid, ids, vals, context=context)
        if 'state' in vals:
            if vals['state'] == 'aapproved':
                if not context:
                    context = {}
                compose = self.pool.get('mail.compose.message')
                c = compose.generate_email_for_composer(cr, uid, 8, ids[0], context=context)
                context.update({
                            'body': c['body'],
                            'anexo': c['attachments'][0][1]
                        })
                cc = self.create_mail_compose_compra(cr, uid, ids, context=context)
        return res 
    
    
    def create_mail_compose_compra(self, cr, uid, ids, context=None):
        ir_attachment            = self.pool.get('ir.attachment')
        mail_mail                = self.pool.get('mail.mail')
        mail_message             = self.pool.get('mail.message')
        compra = self.browse(cr, uid, ids[0])
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if not user.email:
            raise orm.except_orm(
                        ('Aviso'),("Usuario sem email cadastrado!"))
        if not compra.partner_id.email:
            raise orm.except_orm(
                        ('Aviso'),("Fornecedor sem email cadastrado!"))
        temp =  self.pool.get('email.template').browse(cr, uid, 8)
        if temp.email_cc:
            cc = temp.email_cc
        else:
            cc = ''
        vals = {                         
                    'email_from': user.email,
                    'email_to': compra.partner_id.email,
                    'email_cc' : cc,
                    'subject': '%s Pedido de Compra (Ref %s)' % (compra.company_id.name, compra.name),
                    'body_html': context['body'],                        
                }
                      
        mail_id = mail_mail.create(cr, uid, vals , context=context)
        result2 = {
                    'db_datas':context['anexo'],
                    'type':'binary',
                    'res_name':compra.partner_id.name,
                    'company_id':compra.company_id.id,
                    'description':'Email de compra',
                    'datas_fname':u'%s.pdf'%(compra.name),
                    'res_model':'sale.order',
                    'name':'Compra',                        
                    }
        anexo_id = ir_attachment.create(cr, uid, result2)
        message = {
                    'subject': '%s Pedido de Compra (Ref %s)' % (compra.company_id.name, compra.name),
                     'author_id': uid,
                    'date': date.today(),
                    'type': 'email',
                    }
        message_id = mail_message.create(cr, uid, message)
        mail_mail.write(cr, uid, int(mail_id), {'attachment_ids': [(6, 0, [anexo_id])], 
                                                'mail_message_id': int(message_id)}, context=context)
        send_mail = mail_mail.send(cr, uid, [int(mail_id)], context=context)
        
purchase_order()

class boleto_create(osv.osv):

    _inherit = "boleto.boleto_create"
    
    _columns = {
                'sale': fields.many2one('sale.order', 'Venda')
                }
    
    def create_boleto_venda(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        sale_order       = self.pool.get('sale.order')
        boleto_company_config = self.pool.get('boleto.company_config').browse(cr, uid, [context['boleto_company_config_ids']])[0]
        boleto_boleto         = self.pool.get('boleto.boleto')
        valor_documento       = 0               
                
        invoice_dados = False
        lista_produtos = []
        for invoice in sale_order.browse(cr, uid, ids, context=context):
            res_company           = self.pool.get('res.company').browse(cr, uid, invoice.company_id.id)
            if not lista_produtos == []:
                lista_produtos.append("")
            lista_produtos.append(invoice.company_id.name)
            if not invoice_dados:
                partner  = self.pool.get('res.partner').browse(cr, uid, invoice.partner_id.id)
                endereco = ''
                if invoice.state in ['proforma2', 'open', 'sefaz_export','draft']:
                    endereco = '%s, %s  (%s), %s - %s / %s - %s ' %(invoice.partner_id.street,
                                                                    invoice.partner_id.number,
                                                                    invoice.partner_id.street2,
                                                                    invoice.partner_id.district,
                                                                    invoice.partner_id.l10n_br_city_id.name,
                                                                    invoice.partner_id.state_id.name,
                                                                    invoice.partner_id.zip)
                    endereco = normalize('NFKD',unicode(endereco or '')).encode('ASCII','ignore')
                data_vencimento = invoice.vencimento
                data_documento  = invoice.date_order
                nosso_numero    = invoice.id
                if invoice.origin:
                    nome            = 'Referente' + ' ' + invoice.origin or False
                    context.update({'contrato':invoice.origin})
                else:
                    nome = 'Sem Origem'
                invoice_dados   = True 

            for invoice_line in invoice.order_line:
                preco_total  = str("%.2f" % (float(invoice_line.product_uom_qty) * 
                                             float(invoice_line.price_unit))).replace('.',',')
                preco_total  = "R$" + ' ' + preco_total
                linha = "  " + invoice_line.product_id.name[:33].ljust(33)
                     
                linha = linha  + preco_total[:15].rjust(15)
                lista_produtos.append(linha)                    
            if invoice.amount_freight:
                l = "  " + "Frete".ljust(33) +     ("R$ %.2f" % (invoice.amount_freight)).replace('.',',').rjust(15)
                lista_produtos.append(l)
            valor_documento += invoice.amount_total                           
            
        pp = self.pool.get('boleto.partner_config').search(cr, uid, [('default_boleto','=',True)])
        if partner.boleto_partner_config:
            carteira = partner.boleto_partner_config.carteira
        elif pp:
            ppb = self.pool.get('boleto.partner_config').browse(cr, uid, pp[0])
            carteira = ppb.carteira
        else:
            raise osv.except_osv((u'Atencao !'),("Por favor criar uma configuracao de boleto para clientes padrão com as instrucooes do boleto"))
        boleto = {
            'name'              : nome,
            'carteira'          : carteira,
            'cedente'           : res_company.id,
            'sacado'            : partner.id,
            'instrucoes'        : normalize('NFKD',unicode(partner.boleto_partner_config.instrucoes or '')).encode('ASCII','ignore'),
            'banco'             : boleto_company_config.banco,
            'agencia_cedente'   : boleto_company_config.agencia_cedente,
            'conta_cedente'     : boleto_company_config.conta_cedente,
            'convenio'          : boleto_company_config.convenio,
            'nosso_numero'      : nosso_numero,
            'data_vencimento'   : data_vencimento,
            'data_documento'    : data_documento,
            'valor'             : valor_documento,
            'numero_documento'  : str(boleto_company_config.sequence.proximo_numero),
            'endereco'          : str(endereco),
          }

        boleto_id = boleto_boleto.create(cr, uid, boleto, context=context)
        
#         for invoice in sale_order.browse(cr, uid, ids, context=context):
#             dict_rel = {
#                 'boleto_id' : boleto_id,
#                 'fatura_id' : invoice.id,
#                         } 
#             rel_boleto_fatura.create(cr, uid, dict_rel, context=None)
            
        context.update({'lista':lista_produtos})    

        boleto_file     = self.gen_boleto(cr, uid, ids, boleto_id, context=context)
        sequence_boleto = self.pool.get('sequence.boleto')
        proximo         = boleto_company_config.sequence.proximo_numero + 1
        sequence_boleto.write(cr, uid, [boleto_company_config.sequence.id],{'proximo_numero': proximo})
        
        return boleto_file           
    
    def gen_boleto(self, cr, uid, ids, boleto_id, context=None):
        uid = 1
        boleto_boleto                 = self.pool.get('boleto.boleto')
        fbuffer     = StringIO()
        boleto_pdf  = BoletoPDF(fbuffer)
        lista_produtos = context['lista']
        bol = boleto_boleto.browse(cr, uid, boleto_id, context=context)

        if bol.banco == 'bb':
            boleto = BoletoBB(7, 2)
        elif bol.banco == 'bradesco':
            boleto = BoletoBradesco()
        elif bol.banco == 'caixa':
            boleto = BoletoCaixa()
        elif bol.banco == 'real':
            boleto = BoletoReal()
        elif bol.banco == 'itau':
            boleto = BoletoItau()
            
        boleto.demonstrativo = []
        
        end_company = "%s, %s  %s  %s" % (bol.cedente.partner_id.street or '', 
                                          bol.cedente.partner_id.number or '', 
                                          bol.cedente.partner_id.district or '', 
                                          bol.cedente.partner_id.city or '')
        boleto.cedente_documento = bol.cedente.partner_id.cnpj_cpf
        boleto.cedente  = "%s   CNPJ: %s" % (bol.cedente.name,bol.cedente.partner_id.cnpj_cpf)
        boleto.carteira = bol.carteira
        if bol.banco == 'caixa':
            boleto.carteira = 'SR'
        else:
            boleto.carteira = bol.carteira
        boleto.agencia_cedente  = bol.agencia_cedente
        boleto.conta_cedente    = bol.conta_cedente    
        boleto.data_vencimento  = datetime.date(datetime.strptime(bol.data_vencimento, '%Y-%m-%d'))
        boleto.data_documento   = date.today()#datetime.date(datetime.strptime(bol.data_documento, '%Y-%m-%d'))
        boleto.data_processamento = date.today()
        boleto.nosso_numero     = bol.nosso_numero
        if bol.banco == 'caixa':
            n = list(boleto.nosso_numero)
            n[0] = '2'
            n[1] = '4'
            n[2] = '2'
            boleto.nosso_numero = "".join(n)
            boleto.especie_documento = 'DS'
        boleto.numero_documento = bol.numero_documento
        boleto.convenio         = bol.convenio
        pp = self.pool.get('boleto.partner_config').search(cr, uid, [('default_boleto','=',True)])
        if bol.instrucoes:
            instrucoes = bol.instrucoes
        elif pp:
            ppb = self.pool.get('boleto.partner_config').browse(cr, uid, pp[0])
            instrucoes = ppb.instrucoes
        else:
            raise osv.except_osv((u'Atencao !'),("Para gerar boletos primeiro cadastre a configuracao de boleto deste cliente."))
        boleto.instrucoes = []
        
        boleto.valor_documento  = bol.valor
        h = normalize('NFKD',unicode(instrucoes)).encode('ASCII','ignore')
        for k in h.split('\n'):
            boleto.instrucoes.append(k)
            
        boleto.cedente_endereco = normalize('NFKD',unicode(end_company or '')).encode('ASCII','ignore')
        sac = normalize('NFKD',unicode("%s           CNPJ/CPF:%s" 
            % (bol.sacado.legal_name or bol.sacado.name,bol.sacado.cnpj_cpf))).encode('ASCII','ignore')
        end = normalize('NFKD',unicode("%s, %s  %s  %s" 
            % (bol.sacado.street or '', bol.sacado.number or '', bol.sacado.street2 or '', bol.sacado.district or ''))).encode('ASCII','ignore')
        boleto.sacado = [(normalize('NFKD',unicode('%s  CNPJ/CPF: %s' 
                        % (bol.sacado.name or bol.sacado.legal_name or '',
                           str(bol.sacado.cnpj_cpf)))).encode('ASCII','ignore')), end,
                         ("%s            CEP: %s" % (bol.sacado.city,bol.sacado.zip))]
        boleto.demonstrativo =[
            str(sac[:90]),
            "%s" % (bol.name),
            str(end[:90]),
            "%s            CEP: %s" % (bol.sacado.city,bol.sacado.zip),
            "__________________________________________________________________________________________",              
            "REFERENTE A SERVIÇOS",
            "Produto".ljust(35)  + "Valor".rjust(15),
            "",
            ]
        for i in lista_produtos:
            i = normalize('NFKD',unicode(i[:90])).encode('ASCII','ignore'),
            boleto.demonstrativo.append(str(unicode(i[0]))) 
            
        print boleto
        boleto_pdf.drawBoleto(boleto)
        print boleto.linha_digitavel
        boleto_pdf.save()
            
        boleto_file = fbuffer.getvalue().encode("base64")
        fbuffer.close()
        return boleto_file

boleto_create()
