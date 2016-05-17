# -*- coding: utf-8 -*-
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

from openerp.osv import fields, osv


class boleto_partner_config(osv.osv):
    """Boleto Partner Configuration"""
    _name = 'boleto.partner_config'
    _columns = {
        'name'       : fields.char('Name', size=20, required=True),
        'carteira'   : fields.char('Carteira', size=20, required=True),
        'instrucoes' : fields.text(u'Instruções' ,help="Alterar valores de Multa, Mora por variaveis %multa e %mora!"),
        'preferencia': fields.many2one('boleto.company_config', 'Preferência', required=True),
        'default_boleto': fields.boolean('Default')
        }
    _sql_constraints = [('unique_default','UNIQUE(default_boleto)',"Não se pode duplicar um produto.")]

boleto_partner_config()


class boleto_company_config(osv.osv):
    """Boleto Company Configuration"""
    _name = 'boleto.company_config'
    _columns = {
        'name': fields.char('Name', size=20, required=True),
        'banco': fields.selection([('bb', 'Banco do Brasil'), ('real', 'Banco Real'), ('bradesco', 'Banco Bradesco'), ('caixa', 'Banco Caixa Federal'), ('itau', 'Banco Itau')], 'Banco', required=True),
        'agencia_cedente': fields.char('Agencia', size=6, required=True),
        'conta_cedente': fields.char('Conta', size=8, required=True),
        'convenio': fields.char(u'Convenio', size=8, required=True),
        'nosso_numero': fields.integer(u'Nosso Número'),
        'sequence': fields.many2one('sequence.boleto','Sequência Numerica para Boleto',required=True)
         }

boleto_company_config()

class sequence_boleto(osv.osv):
    _name = "sequence.boleto"

    _columns = {
                'name': fields.char('Nome', 256,required=True),
                'qtd': fields.integer('Quantidade de Inserção',required=True),
                'proximo_numero': fields.integer('Proximo Numero',required=True),
                #'company_id': fields.many2one('res.company','Empresa',required=True)
                }

    _defaults = {
                 'qtd': 1,
                 'proximo_numero': 1,
                 }

sequence_boleto()

class boleto_boleto(osv.osv):

    """Boleto"""

    _name = 'boleto.boleto'
    _columns = {
        'name'      : fields.char('Name', size=128, required=True),
        'carteira'  : fields.char('Carteira', size=10),
        'instrucoes': fields.text(u'Instruções'),
        'sacado'    : fields.many2one('res.partner', 'Sacado'),
        'banco'     : fields.selection([('bb', 'Banco do Brasil'),
                                        ('real', 'Banco Real'),
                                        ('bradesco', 'Banco Bradesco'),
                                        ('caixa', 'Banco Caixa Federal'),
                                        ('itau', 'Banco Itau')], 'Banco'),
        'agencia_cedente'   : fields.char ('Agencia', size=6),
        'conta_cedente'     : fields.char ('Conta', size=8),
        'convenio'          : fields.char ('Convenio', size=8),
        'cedente'           : fields.many2one('res.company', 'Empresa'),
        'invoice_id'        : fields.many2one('account.invoice', 'Fatura'),
        'data_vencimento'   : fields.date ('Data do Vencimento'),
        'data_documento'    : fields.date ('Data do Documento'),
        'data_processamento': fields.date ('Data do Processamento'),
        'valor'             : fields.float('Valor', digits=(12, 2)),
        'numero_documento'  : fields.char (u'Número do Documento', size=20),
        'nosso_numero'      : fields.char (u'Nosso Numero', size=10),
        'endereco'          : fields.char (u'Endereço', size=128),
        'invoice_line'      : fields.one2many('rel.boleto.fatura', 'boleto_id', 'Invoice Lines'),
    }

boleto_boleto()

class rel_boleto_fatura(osv.osv):

    """Relação Boleto Fatura"""

    _name = 'rel.boleto.fatura'
    _columns = {
        'boleto_id' : fields.many2one('boleto.boleto', 'Boleto'),
        'fatura_id' : fields.many2one('account.invoice', 'Fatura'),
                }

rel_boleto_fatura()
