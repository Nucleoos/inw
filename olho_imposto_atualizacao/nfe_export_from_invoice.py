# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion                                  #
# Copyright (C) 2011  Vinicius Dittgen - PROGE, Leonardo Santagada - PROGE    #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

import time
import base64
import re, string
from openerp.osv import orm, fields
from openerp.tools.translate import _


class l10n_br_account_nfe_export_invoice(orm.TransientModel):
    _inherit = 'l10n_br_account_product.nfe_export_invoice'

    def nfe_export(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        inv_obj = self.pool.get('account.invoice')
        active_ids = self._get_invoice_ids(cr, uid, data, context)
        export_inv_ids = []
        export_inv_numbers = []
        company_ids = []
        err_msg = ''

        if not active_ids:
            err_msg = u'Não existe nenhum documento fiscal para ser exportado!'

        for inv in inv_obj.browse(cr, uid, active_ids, context=context):
            if inv.state not in ('sefaz_export'):
                err_msg += u"O Documento Fiscal %s não esta definida para ser \
                exportação para a SEFAZ.\n" % inv.internal_number
            elif not inv.issuer == '0':
                err_msg += u"O Documento Fiscal %s é do tipo externa e não \
                pode ser exportada para a receita.\n" % inv.internal_number
            else:
                inv_obj.write(cr, uid, [inv.id], {'nfe_export_date': False,
                                                  'nfe_access_key': False,
                                                  'nfe_status': False,
                                                  'nfe_date': False})

                message = "O Documento Fiscal %s foi \
                    exportado." % inv.internal_number
                inv_obj.log(cr, uid, inv.id, message)
                export_inv_ids.append(inv.id)
                company_ids.append(inv.company_id.id)

            export_inv_numbers.append(inv.internal_number)

        if len(set(company_ids)) > 1:
            err_msg += u'Não é permitido exportar Documentos \
            Fiscais de mais de uma empresa, por favor selecione Documentos \
            Fiscais da mesma empresa.\n'

        if export_inv_ids:
            if len(export_inv_numbers) > 1:
                name = 'nfes%s-%s.%s' % (
                    time.strftime('%d-%m-%Y'),
                    self.pool.get('ir.sequence').get(cr, uid, 'nfe.export'),
                    data['file_type'])
            else:
                name = '{numero}_{cnpj}_{serie:0>3}_{dia}_{mes}_{ano}-nfe.{file_type}'.format(numero=export_inv_numbers[0],
                    cnpj=(re.sub('[%s]' % re.escape(string.punctuation), '', inv.company_id.partner_id.cnpj_cpf or '')),
                    serie=int(inv.document_serie_id.code),dia=time.strftime('%d'),
                    mes=time.strftime('%m'),ano=time.strftime('%Y'),
                    file_type=data['file_type'])

            mod_serializer = __import__(
                'nfe.sped.nfe.serializer.' + data['file_type'],
                 globals(), locals(), data['file_type'])

            func = getattr(mod_serializer, 'nfe_export')
            nfes = func(
                cr, uid, export_inv_ids, data['nfe_environment'],
                '3.10', context)

            for nfe in nfes:
                #if nfe['message']:
                    #status = 'error'
                #else:
                    #status = 'success'

                #self.pool.get(self._name + '_result').create(
                    #cr, uid, {'document': nfe['key'],
                        #'message': nfe['message'],
                        #'status': status,
                        #'wizard_id': data['id']})

                nfe_file = nfe['nfe'].encode('utf8')
            total_lic = float(inv.amount_total) - float(inv.total_federal_valor) - float(inv.total_estadual_valor)
            #nfe_file = inv_obj.nfe_export_txt(cr, uid, export_inv_ids, data['nfe_environment'])
            imp = ("Voce pagou aproximadamente:R$ %.2f de Tributos Federais, R$ %.2f de Tributos Estaduais, R$ %.2f Pelos Produtos Comercializados. Fonte: IBPT/FECOMERCIO " % (inv.total_federal_valor, inv.total_estadual_valor, total_lic)).replace('.',',').replace('*','.')

	    #tmp_obj = self.pool.get('account.invoice')
            #r = tmp_obj.write(cr, uid, inv.id, {'comment' : imp}, context)

            if '<infCpl>' in nfe_file:
                note = nfe_file.split('<infCpl>')
            elif '<infAdFisco>' in nfe_file:
                note = nfe_file.split('</infAdFisco>')
            else:
                note = nfe_file.split('</transp>')
            info = note[1]
            print imp.decode('utf-8')
            if inv.comment:
                imp = imp + ' - ' + inv.comment
            if '<infCpl>' in nfe_file:
                note[1] = '<infCpl>' + imp.decode('utf-8') +  info
            elif '<infAdFisco>' in nfe_file:
                note[1] = '</infAdFisco><infCpl>' + imp.decode('utf-8') + '</infCpl>' +  info
            else:
                note[1] = '</transp><infAdic><infCpl>' + imp.decode('utf-8') + '</infCpl></infAdic>' +  info
            txt = note[0] + note[1]
            nfe_file = unicode(txt.encode('utf-8'), errors='replace')
            save_dir = inv.company_id.nfe_export_folder
            if (data['export_folder']) & (save_dir != ''):
                try:
                    f = open(save_dir + name, 'w')
                except IOError:
                    err_msg += u'Não é foi possivel salvar o arquivo em disco, verifique as permissões de escrita e \
                    o caminho da pasta nas configurações da empresa\n'
                else:
                    f.write(nfe_file)
                    f.close()

            self.write(
                cr, uid, ids, {'file': base64.b64encode(nfe_file),
                'state': 'done', 'name': name}, context=context)

        if err_msg:
            raise orm.except_orm(_('Error!'), _("'%s'") % _(err_msg, ))

        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(
            cr, uid, [('model', '=', 'ir.ui.view'),
            ('name', '=', 'l10n_br_account_nfe_export_invoice_form')],
            context=context)
        resource_id = mod_obj.read(
            cr, uid, model_data_ids,
            fields=['res_id'], context=context)[0]['res_id']

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': data['id'],
            'views': [(resource_id, 'form')],
            'target': 'new',
        }

l10n_br_account_nfe_export_invoice()
