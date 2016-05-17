# -*- encoding: UTF-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2011  Vinicius Dittgen - PROGE, Leonardo Santagada - PROGE      #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from pyboleto.bank.real import BoletoReal
from pyboleto.bank.itau import BoletoItau
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixa
from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.pdf import BoletoPDF
from datetime import datetime, date
import sys
import base64
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
from unicodedata import normalize

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class boleto_create(osv.osv):

    _name = "boleto.boleto_create"

    def _get_company_config_ids(self, cr, uid, context=None):
        ret = []
        if context is None:
            context = {}
        if 'active_ids' in context:
            active_ids = context.get('active_ids', [])[0]
            invoice    = self.pool.get('account.invoice').browse(cr, uid, active_ids, context=context)
            company    = self.pool.get('res.company').browse(cr, uid, [invoice.company_id.id])[0]
            currency   = self.pool.get('res.currency').browse(cr, uid, company.currency_id.id)
            for bol_conf_id in company.boleto_company_config_ids:
                bc = bol_conf_id.id, bol_conf_id.name
                ret.append(bc)

        return ret

    _columns = {
        'boleto_company_config_ids': fields.selection(_get_company_config_ids, u'Configuração dos Boletos', required=True),
        'file': fields.binary('Arquivo', readonly=True),
        'state': fields.selection([('init', 'init'),
                               ('done', 'done')], 'state', readonly=True),
        }

    _defaults = {
        'state': 'init',
        }

    def create_boleto(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        account_invoice       = self.pool.get('account.invoice')
        account_invoice_line  = self.pool.get('account.invoice.line')
        boleto_company_config = self.pool.get('boleto.company_config').browse(cr, uid, [context['boleto_company_config_ids']])[0]
        #[context['company_id']])[0]
        #res_currency          = self.pool.get('res.currency').browse(cr, uid, res_company.namecurrency_id.id)
        boleto_boleto         = self.pool.get('boleto.boleto')
        rel_boleto_fatura     = self.pool.get('rel.boleto.fatura')
        valor_documento       = 0

        invoice_dados = False
        lista_produtos = []
        for invoice in account_invoice.browse(cr, uid, ids, context=context):
            res_company           = self.pool.get('res.company').browse(cr, uid, invoice.company_id.id)
            if not lista_produtos == []:
                lista_produtos.append("")
            lista_produtos.append(invoice.company_id.name)
            if not invoice_dados:
                partner  = self.pool.get('res.partner').browse(cr, uid, invoice.partner_id.id)
                endereco = ''
                if invoice.state in ['proforma2', 'open', 'sefaz_export','draft']:
#                     if invoice.contact_id:
#                         endereco = '%s, %s  (%s), %s - %s / %s - %s ' %(invoice.contact_id.endereco_cobranca.street,
#                                                                         invoice.contact_id.endereco_cobranca.number,
#                                                                         invoice.contact_id.endereco_cobranca.street2,
#                                                                         invoice.contact_id.endereco_cobranca.district,
#                                                                         invoice.contact_id.endereco_cobranca.l10n_br_city_id.name,
#                                                                         invoice.contact_id.endereco_cobranca.state_id.name,
#                                                                         invoice.contact_id.endereco_cobranca.zip)
#                     else:
                    endereco = '%s, %s  (%s), %s - %s / %s - %s ' %(invoice.partner_id.street,
                                                                    invoice.partner_id.number,
                                                                    invoice.partner_id.street2,
                                                                    invoice.partner_id.district,
                                                                    invoice.partner_id.l10n_br_city_id.name,
                                                                    invoice.partner_id.state_id.name,
                                                                    invoice.partner_id.zip)
                    endereco = normalize('NFKD',unicode(endereco or '')).encode('ASCII','ignore')
                venc = ''
		if invoice.date_due:
                    venc = invoice.date_due
		if invoice.vencimento:
                    venc = invoice.vencimento
                if venc == '':
                    venc = date.today()
                data_vencimento = venc
                data_documento  = invoice.date_invoice
                nosso_numero    = invoice.id
                nome            = 'Referente' + ' ' + invoice.origin or False
                context.update({'contrato':invoice.origin})
                invoice_dados   = True

            for invoice_line in invoice.invoice_line:
                preco_total  = str("%.2f" % (float(invoice_line.quantity) *
                                             float(invoice_line.price_unit))).replace('.',',')
                preco_total  = "R$" + ' ' + preco_total
#                 if invoice_line.product_id.billet_name:
#                     linha = "  " + invoice_line.product_id.billet_name[:33].ljust(33)
#                 else:
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

        for invoice in account_invoice.browse(cr, uid, ids, context=context):
            dict_rel = {
                'boleto_id' : boleto_id,
                'fatura_id' : invoice.id,
                        }
            rel_boleto_fatura.create(cr, uid, dict_rel, context=None)

        context.update({'lista':lista_produtos})

        boleto_file     = self.gen_boleto(cr, uid, ids, boleto_id, context=context)
        sequence_boleto = self.pool.get('sequence.boleto')
        proximo         = boleto_company_config.sequence.proximo_numero + 1
        sequence_boleto.write(cr, uid, [boleto_company_config.sequence.id],{'proximo_numero': proximo})

        return boleto_file

    def gen_boleto(self, cr, uid, ids, boleto_id, context=None):
        uid = 1
        boleto_boleto                 = self.pool.get('boleto.boleto')
        account_analytic_account      = self.pool.get('account.analytic.account')
        account_analytic_charges_line = self.pool.get('account.analytic.charges.line')
        res_company                   = self.pool.get('res.company').browse(cr, uid, 1)
      #  res_currency                  = self.pool.get('res.currency').browse(cr, uid, res_company.currency_id.id)

        partner_obj = self.pool.get('')
        fbuffer     = StringIO()
        boleto_pdf  = BoletoPDF(fbuffer)
        lista_produtos = context['lista']
        multa = 0
        mora = 0
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

        contrato_id    = account_analytic_account.search(cr, uid, [('code', '=', str(context['contrato']))])

#         lista_encargos = account_analytic_charges_line.search(cr, uid, [('analytic_account_id', '=', contrato_id)])
#
#         for charge in account_analytic_charges_line.browse(cr, uid, lista_encargos):
#             if charge.type_charge == 'mora':
#                 mora = charge.perc_charge
#             elif charge.type_charge == 'multa':
#                 multa = charge.perc_charge
#
        boleto.valor_documento  = bol.valor
        multa_ok = 0
        mora_ok = 0
#         for k in bol.instrucoes.split('\n'):
        h = normalize('NFKD',unicode(instrucoes)).encode('ASCII','ignore')
#         if multa and multa_ok == 0:
#             #multa = "%s%s" % (multa, '%')
#             multa = multa / 100
#             multa = str("%.2f" % (float(multa) * float(boleto.valor_documento))).replace('.',',')
#             multa = "%s%s" % ("R$", multa)
#             h = h.replace('@multa', multa)
#             multa_ok = 1
#         if mora and mora_ok == 0:
#             #mora = "%s%s" % (mora, '%')
#             mora = mora / 100
#             mora = str("%.2f" % (float(mora) * float(boleto.valor_documento))).replace('.',',')
#             mora = "%s%s" % ("R$", mora)
#             h = h.replace('@mora', mora)
#             mora_ok = 1
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
