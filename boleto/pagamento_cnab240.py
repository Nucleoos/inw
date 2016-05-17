# -*- encoding:utf-8 -*-

from openerp.osv import osv, fields
from datetime import date,datetime
import time
import shutil
import glob


class pagamento_cnab240(osv.osv):
    _name = 'pagamento.cnab240'

    # Pega os arquivos RET em um diretorio
    def get_ret(self, cr, uid, *args):
        lista_logs = []
        types_document = ('/home/robertosantos/Documentos/RET/*.RET',
                          '/home/robertosantos/Documentos/RET/*.ret',
                          '/home/robertosantos/Documentos/RET/*.txt')
        for type in types_document:
            for file in glob.glob(type):
                lista_logs += (self.checa_linha(cr, uid, file))
        #lista de logs
        if lista_logs:
            local_name = "/home/robertosantos/Documentos/log/log_%s_.txt" % datetime.now()
            var_file = open(local_name, 'w')
            for linha in lista_logs:
                var_file.write(linha)
            var_file.close()
            shutil.move(file, '/home/robertosantos/Documentos/RET Usado')
        else:
            msg_txt = "Baixa de pagamentos executado com sucesso as %s" % datetime.now()
            local_name = "/home/robertosantos/Documentos/log/log_%s_.txt" % datetime.now()
            var_file = open(local_name, 'w')
            for linha in msg_txt:
                var_file.write(linha)
            var_file.close()
            shutil.move(file, '/home/robertosantos/Documentos/RET Usado')
        return lista_logs

    # Para cada arquivo, checa-se se existe uma linha T e U, se existir ele chama o metodo checa pagamento
    # T = Informacoes de criacao do boleto
    # U = Informacaoes do pagamento
    def checa_linha(self, cr, uid, file):
        contador_itau = contador_cef = contador_bb = contador_linha = 0
        lista_log = []
        for line in open(file):
            contador_linha += 1
            if line[:3] == '104':
                if line[7:8] == '3':
                    if  line[13:14] == 'T':
                        valor_nominal_titulo = line[81:96]
                        data_vencimento = line[73:81]
                        nosso_numero = line[46:57]
                        contador_cef += 1
                    elif line[13:14] == 'U':
                        data_processamento = line[137:145]
                        valor_pago = line[77:92]
                        contador_cef += 1
            elif line[:3] == '341':
                if line[7:8] == '3':
                    if  line[13:14] == 'T':
                        contador_itau = contador_itau + 1
                        valor_nominal_titulo = line[81:96]
                        data_vencimento = line[73:81]
                        nosso_numero = line[40:48]
                    elif line[13:14] == 'U':
                        data_processamento = line[137:145]
                        valor_pago = line[77:92]
                        contador_itau = contador_itau + 1
            elif line[:3] == '001':
                if line[7:8] == '3':
                    if  line[13:14] == 'T':
                        valor_nominal_titulo = line[81:96]
                        nosso_numero = line[37:57]
                        data_vencimento = line[73:81]
                        contador_bb += 1
                    elif line[13:14] == 'U':
                        data_processamento = line[137:145]
                        valor_pago = line[77:92]
                        contador_bb += 1
            if contador_cef == 2 or contador_itau == 2 or contador_bb == 2:
                valor_nominal_titulo = valor_nominal_titulo.lstrip('0')
                valor_pago = valor_pago.lstrip('0')
                nosso_numero = nosso_numero.lstrip('0')


                if data_vencimento == '00000000':
                    boleto_id = self.pool.get('boleto.boleto')
                    boleto_src = boleto_id.search(cr, uid, [('nosso_numero', '=', nosso_numero)])
                    if boleto_src:
                        boleto_brw = boleto_id.browse(cr, uid, max(boleto_src))
                        if boleto_brw:
                            data_vencimento = boleto_brw.data_vencimento
                if  valor_nominal_titulo != "" and valor_pago != "" and data_processamento[:2] != "" and data_processamento[:2] != '00' and data_vencimento[:2] != '00' and data_vencimento[:2] != '':
                    lista_log += (self.checa_pagamento(cr, uid, valor_nominal_titulo, data_vencimento, nosso_numero, data_processamento, valor_pago))
                else:
                    lista_log.append("Os dados da linha %s no arquivo %s apresentaram inconsistencias, favor verificar.  \n" %(str(contador_linha),file))
                if contador_cef == 2:
                    contador_cef = 0
                elif contador_itau:
                    contador_itau = 0
                else:
                    contador_bb = 0
                valor_nominal_titulo = ''
                data_vencimento = ''
                data_processamento = ''
                valor_pago = ''
                nosso_numero = ''
        return lista_log
    
    # valida se a creditos cadastrado no sistema para o cliente que fez o pagamento
    def cria_voucher(self, cr, uid, fatura, valor_pago, faturas_ids, pagamento, empresa, tipo, context=None):
        if not context:
            conta_id = self.pool.get('account.account').search(cr, uid, [('company_id', '=', empresa[0]), ('code', '=', "1.01.01.02.002")])
        else:
            conta_id = self.pool.get('account.account').search(cr, uid, [('company_id', '=', empresa[0]), ('code', '=', "1.01.05.02.00")])
        period_id = self.pool.get("account.period").search(cr, uid, [('company_id', '=', empresa[0]), ('code', '=', time.strftime("%m/%Y"))])
        if not conta_id or not period_id:
            dict = {'sem_conta': True, 'msg_log': ''}
            if not conta_id:
                dict['msg_log'] = 'A empresa %s não tem conta banco \n' %self.pool.get("res.company").browse(cr, uid, empresa[0].name)
            if not period_id:
                dict['msg_log'] = dict['msg_log'] + 'A empresa %s não tem periodo definido para %s' %(self.pool.get("res.company").browse(cr, uid, empresa[0].name), time.strftime("%m/%Y"))
            return dict
        account_invoice = fatura.browse(cr, uid, faturas_ids[0])
        journal_pool = self.pool.get('account.journal')
        if not context:
            account_jornal_id = journal_pool.search(cr, uid, [('code', '=', 'BCO2'),
                                                            ('company_id', '=', empresa[0])])
        else:
            account_jornal_id = journal_pool.search(cr, uid, [('code', '=', 'DV'),
                                                            ('company_id', '=', empresa[0])])
        account_voucher = {
                            'partner_id': account_invoice.partner_id.id,
                            'date': date.today(),
                            'journal_id': account_jornal_id[0],
                            'amount': float(valor_pago),
                            'company_id': empresa[0],
                            'type': tipo,
                            'account_id': conta_id[0],
                            'period_id': period_id[0],
                         }
        if context:
            account_voucher['name'] = "Recibo automatico referente ao mes %s (multa: %s, mora: %s)" %(time.strftime("%m/%Y"),context[0], context[1]),
        else:
            account_voucher['name'] = "Pagamento automatico referente ao mes %s" %time.strftime("%m/%Y"),

        pagamento_id = pagamento.create(cr, uid, account_voucher)
        return {'id_pagamento': pagamento_id, 'account_invoice': account_invoice.partner_id.id, 'pagamento': pagamento, 'account_journal_id': account_jornal_id}

    def cria_mov(self, cr, uid, journal, period, fatura_id, context):
        move = self.pool.get('account.move')
        fatura = self.pool.get('account_invoice')
        fatura_brw = fatura.browse(cr, uid, fatura_id, context)
        dict_line = {
                     }
        dict = {
                'journal_id': journal,
                }


    def checa_pagamento(self, cr, uid, valor_nominal_titulo, data_vencimento, nosso_numero, data_processamento, valor_pago):
        lista_log = []
        faturas_ids = []
        journal_pool = self.pool.get('account.journal')
        pagamento = self.pool.get('account.voucher')
        fatura = self.pool.get('account.invoice')
        rel_fatura_obj = self.pool.get('rel.boleto.fatura')
        cr.execute('select id from res_company')
        lista_empresa = cr.fetchall()
        boleto_id = self.pool.get("boleto.boleto").search(cr, uid, [("nosso_numero", "=", nosso_numero)])
        if boleto_id:
            rel_boleto_fatura_ids = rel_fatura_obj.search(cr, uid, [('boleto_id', '=', boleto_id[0])]) #int(nosso_numero)
            for each_line in rel_fatura_obj.browse(cr, uid, rel_boleto_fatura_ids):
                if each_line.fatura_id.state == 'open':
                    faturas_ids.append(each_line.fatura_id.id)
            if not faturas_ids:
                return lista_log
            voucher = self.cria_voucher(cr, uid, fatura, valor_pago, faturas_ids, pagamento, lista_empresa[0], 'receipt')
            if 'sem_conta' in voucher:
                return lista_log.append(voucher['msg_log'])
            journal = journal_pool.browse(cr, uid, voucher['account_journal_id'][0])
            currency_id = journal.company_id.currency_id.id
            linhas_credito = pagamento.onchange_partner_id(cr, uid, [int(voucher['id_pagamento'])], voucher['account_invoice'], voucher['account_journal_id'][0], float(valor_pago),currency_id, 'receipt', date.today(), None)
            if linhas_credito['value']['line_cr_ids'] == []:
                pagamento.unlink(cr, uid, [int(voucher['id_pagamento'])], context=None)
                lista_log.append('O(a) cliente %s nao possui debitos no sistema, porem no arquivo cnab %s consta que o cliente efetuou um pagamento no valor de  %s reais. \n' % (voucher['account_invoice'],"240",valor_pago))
            else:
                cria = self.checa_linhas(cr, uid, linhas_credito, faturas_ids, data_vencimento, data_processamento, valor_pago, voucher['id_pagamento'], currency_id, voucher['account_journal_id'], lista_empresa)
    #             if not cria:
    #                 pagamento.unlink(cr, uid, [int(pagamento_id)], context=None)
        else:
            lista_log.append('Boleto de nosso numero %s nao registrado no sistema' %nosso_numero)
        return lista_log

    # efetua os pagamentos linha a linha
    def checa_linhas(self, cr, uid, t, fatura_ids, data_vencimento, data_processamento, valor_pago, pagamento_id, currency_id, account_jornal_id, lista_empresa):
        lista_log = []
        fatura = self.pool.get('account.invoice')
        empresa_incial = lista_empresa[0][0]
        lista_multa_mora = []
        linhas_fatura = 0
        saldo = valor_pago
        pagamento = self.pool.get('account.voucher')
        qnt_linha_debito = len(t['value']['line_cr_ids']) -1
        data_vencimento.replace('-', '')
        ano = data_vencimento[4:]
        mes = data_vencimento[2:4]
        dia = data_vencimento[:2]
        data_vencimento = ano + '-' + mes + '-' + dia
        ano_p = data_processamento[4:]
        mes_p = data_processamento[2:4]
        dia_p = data_processamento[:2]
        data_processamento = ano_p + '-' + mes_p + '-' + dia_p
        multa = mora = multa_t = mora_t = 0
        calc_multa = False
        if fatura_ids:
            for empresa in lista_empresa:
                total_fatura = 0
                if not empresa_incial == empresa[0]:
                    voucher = self.cria_voucher(cr, uid, fatura, valor_pago, fatura_ids, pagamento, empresa, 'receipt')
                    pagamento_id = voucher['id_pagamento']
                for fatura_brw in self.pool.get('account.invoice').browse(cr, uid, fatura_ids):
                    if fatura_brw.company_id.id == empresa[0]:
                        linhas_fatura += len(fatura_brw.invoice_line)
                        total_fatura += fatura_brw.residual
                saldo -= total_fatura
                pagamento.write(cr, uid, pagamento_id, {"amount": total_fatura})
                for fatura_brw in self.pool.get('account.invoice').browse(cr, uid, fatura_ids):
                    linha_atual = 0
                    # pago total
                    if valor_pago >= total_fatura:
                        while(qnt_linha_debito >= linha_atual):
                            #pago em dia
                            if t['value']['line_cr_ids'][linha_atual]['date_due'] >= data_processamento and fatura_brw.move_id.name == t['value']['line_cr_ids'][linha_atual]['name']:
                                i = t['value']['line_cr_ids'][linha_atual]
                                if fatura_brw.company_id.id != empresa[0]:
                                    linha_atual += 1
                                    continue
                                i['reconcile'] = True
                                i['voucher_id'] = int(pagamento_id)
                                i['amount'] = i['amount_unreconciled']
                                self.pool.get('account.voucher.line').create(cr, uid, i, None)
                                #
                            # pago em atraso
                            elif t['value']['line_cr_ids'][linha_atual]['date_due'] <= data_processamento and fatura_brw.move_id.name == t['value']['line_cr_ids'][linha_atual]['name']:
                                i = t['value']['line_cr_ids'][linha_atual]
                                if fatura_brw.company_id.id != empresa[0]:
                                    linha_atual += 1
                                    continue
                                contrato_id = self.pool.get('account.analytic.account').search(cr, uid, [('name', '=', fatura_brw.origin)])[0]
                                contrato_brw = self.pool.get('account.analytic.account').browse(cr, uid, contrato_id)
                                mora_brw = self.pool.get('desconto.mora')
                                mora += mora_brw.calcula_mora(cr, uid, contrato_brw.id, fatura_brw.id, data_processamento)
                                if not calc_multa:
                                    for item in contrato_brw.charges_line_ids:
                                        if item.name == 'multa':
                                            multa += (item.perc_charge / 100) * t['value']['line_cr_ids'][linha_atual]['amount_unreconciled']
                                            break
                                    calc_multa = True
                                i['reconcile'] = True
                                i['voucher_id'] = int(pagamento_id)
                                i['amount'] = i['amount_unreconciled']
                                lista_multa_mora.append([multa, mora])
                                self.pool.get('account.voucher.line').create(cr, uid, i, None)
                            linha_atual += 1

                    else:
                        while(qnt_linha_debito >= linha_atual):
                            #pago em dia
                            if t['value']['line_cr_ids'][linha_atual]['date_due'] >= data_processamento and fatura_brw.move_id.name == t['value']['line_cr_ids'][linha_atual]['name']:
                                i = t['value']['line_cr_ids'][linha_atual]
                                if fatura_brw.company_id.id != empresa[0]:
                                    linha_atual += 1
                                    continue
                                i['voucher_id'] = int(pagamento_id)
                                i['amount'] = i['amount_unreconciled']
                                self.pool.get('account.voucher.line').create(cr, uid, i, None)
                            # pago em atraso
                            elif t['value']['line_cr_ids'][linha_atual]['date_due'] <= data_processamento and fatura_brw.move_id.name == t['value']['line_cr_ids'][linha_atual]['name']:
                                i = t['value']['line_cr_ids'][linha_atual]
                                if fatura_brw.company_id.id != empresa[0]:
                                    linha_atual += 1
                                    continue
                                contrato_id = self.pool.get('account.analytic.account').search(cr, uid, [('name', '=', fatura_brw.origin)])[0]
                                contrato_brw = self.pool.get('account.analytic.account').browse(cr, uid, contrato_id)
                                mora_brw = self.pool.get('desconto.mora')
                                mora += mora_brw.calcula_mora(cr, uid, contrato_brw.id, fatura_brw.id, data_processamento)
                                if not calc_multa:
                                    for item in contrato_brw.charges_line_ids:
                                        if item.name == 'multa':
                                            multa += (item.perc_charge/100) * t['value']['line_cr_ids'][linha_atual]['amount_unreconciled']
                                            break
                                    calc_multa = True
                                i['reconcile'] = True
                                i['voucher_id'] = int(pagamento_id)
                                i['amount'] = i['amount_unreconciled']
                                lista_multa_mora.append([multa, mora])
                                self.pool.get('account.voucher.line').create(cr, uid, i, None)
                            linha_atual += 1
                pagamento.proforma_voucher(cr, uid, [int(pagamento_id)], context=None)
                self.cria_movimento(cr, uid, empresa, fatura_brw, valor_pago)
                if lista_multa_mora:
                    linha_atual_div = 0
                    for elemento in lista_multa_mora:
                        multa_t += elemento[0]
                        mora_t += elemento[1]
                    context = [multa_t, mora_t]
                    divida_id = self.cria_voucher(cr, uid, fatura, multa_t + mora_t, fatura_ids, pagamento, empresa, 'sale', context)
                    self.cria_voucher_line(cr, uid, divida_id['id_pagamento'], multa_t, empresa, time.strftime("%d-%m-%Y"), {'name': 'Multa'})
                    self.cria_voucher_line(cr, uid, divida_id['id_pagamento'], mora_t, empresa, time.strftime("%d-%m-%Y"), {'name': 'Mora'})
                    pagamento.proforma_voucher(cr, uid, [divida_id['id_pagamento']], context=None)
                    m = True
                if saldo:
                    voucher_divida = self.cria_voucher(cr, uid, fatura, saldo, fatura_ids, pagamento, empresa, 'receipt')
                    voucher_dict = pagamento.onchange_partner_id(cr, uid, [int(voucher_divida['id_pagamento'])],voucher_divida['account_invoice'], voucher_divida['account_journal_id'][0],float(saldo),currency_id, 'receipt', date.today(), None)
                    if m:
                        if saldo >= multa_t + mora_t:
                            contador_linha = len(voucher_dict['value']['line_cr_ids'])
                            while linha_atual_div < contador_linha:
                                if voucher_dict['value']['line_cr_ids'][linha_atual_div]['date'] == time.strftime("%d-%m-%Y") and mora_t == t['value']['line_cr_ids'][linha_atual_div]['amount_original'] or multa_t == t['value']['line_cr_ids'][linha_atual_div]['amount_original']:
                                    i = voucher_dict['value']['line_cr_ids'][linha_atual_div]
                                    i['reconcile'] = True
                                    i['voucher_id'] = voucher_divida['id_pagamento']
                                    i['amount'] = i['amount_unreconciled']
                                    self.pool.get('account.voucher.line').create(cr, uid, i, None)
                        else:
                            contador_linha = len(voucher_dict['value']['line_cr_ids'])
                            while linha_atual_div < contador_linha:
                                if voucher_dict['value']['line_cr_ids'][linha_atual_div]['date_original'] == time.strftime("%Y-%d-%m") and mora_t + multa_t == voucher_dict['value']['line_cr_ids'][linha_atual_div]['amount_original']:
                                    i = voucher_dict['value']['line_cr_ids'][linha_atual_div]
                                    i['voucher_id'] = voucher_divida['id_pagamento']
                                    i['amount'] = saldo
                                    self.pool.get('account.voucher.line').create(cr, uid, i, None)
                                linha_atual_div += 1
                    pagamento.proforma_voucher(cr, uid,  [int(voucher_divida['id_pagamento'])], context=None)
                    self.cria_movimento(cr, uid, empresa, fatura_brw, saldo)
        return lista_log

    def cria_voucher_line(self, cr, uid, divida_id, valor, empresa, date, context):
        line = self.pool.get('account.voucher.line')
        #TODO EMPRESA QUE FICA COM A MULTA E MORA
        account_id = self.pool.get('account.account').search(cr, uid, [('code', '=', "3.01.01.01.01.02.00"), ('company_id', '=', empresa)])
        dicionario = {
                              'voucher_id': divida_id,
                              'amount': valor,
                              'account_id': account_id[0],
                              'company_id': empresa,
                              'type': 'cr',
                              'date': date,
                              'name': context['name'],
                    }
        return line.create(cr, uid, dicionario)

    def cria_movimento(self, cr, uid, empresa, fatura, valor_pago):
        account_move = self.pool.get("account.move")
        account_move_line = self.pool.get("account.move.line")
        account_account = self.pool.get("account.account")
        account_journal = self.pool.get("account.journal")
        account_period = self.pool.get("account.period")

        journal_id = account_journal.search(cr, uid, [('code', '=', 'DV'),('company_id', '=', empresa)])
        periodo_id = account_period.search(cr, uid, [('company_id', '=', empresa),
                                                     ('code', '=', time.strftime("%m/%Y"))])
        account_master = account_account.search(cr, uid, [("conta_max", '=', True)])
        account_empresa = account_account.searc(cr, uid, [("code", "=", "BCO2"), ("company_id", "=", empresa)])
        if journal_id and periodo_id and account_master and account_empresa:
            dicionario = {
                          'journal_id': journal_id[0],
                          'period_id': periodo_id[0],
                          'company_id': empresa,
                          'ref': fatura.internal_number,
                          'date': time.strftime("%m/%Y"),
                          'narration': "Movimentação automatica referente ao pagamento da fatura %s" %fatura.name,
                          }
            mov_id = account_move.create(cr, uid, dicionario)
            dicionario_linha = {
                                'name': "%s/1" %fatura.internal_number,
                                'account_id': account_master[0],
                                'debit': valor_pago,
                                'move_id': mov_id,
                                }
            account_move_line.create(cr, uid, dicionario_linha)
            dicionario_linha['credit'] = dicionario_linha ['debit']
            dicionario_linha['debit'] = 0.0
            dicionario_linha['account_id'] = account_empresa[0]
            account_move_line.create(cr, uid, dicionario_linha)

        return True
pagamento_cnab240()

# 
# class account_voucher_line(osv.osv):
#     _inherit = 'account.voucher.line'
#     _columns = {
#                 'date': fields.date('Data'),
#                 }
# account_voucher_line()
