# -*- encoding: utf-8 -*-
from openerp.osv import  fields, osv

class declaracao_importacao(osv.osv):
    _name = 'declaracao.importacao'
    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line', u'Linha de Documento Fiscal', ondelete='cascade', select=True),
        'name': fields.char(u'Número da DI', size=10, required=True),
        'date_registration': fields.date(u'Data de Registro', required=True),
        'exporting_code': fields.char(u'Código do Exportador', size=60),
        'state_id': fields.many2one('res.country.state', u'Estado', domain="[('country_id.code', '=', 'BR')]"),
        'location': fields.char(u'Local', size=60),
        'date_release': fields.date(u'Data de Liberação'),
        'line_ids': fields.one2many('declaracao.importacao.linha', 'declaracao_importacao_id', 'Linhas da DI'),
        'via_trans_internacional': fields.selection([('1', 'Maritima'), ('2', 'Fluvial'),
                                                     ('3', 'Lacustre'), ('4', 'Aérea'),
                                                     ('5', 'Postal'), ('6', 'Ferroviária'),
                                                     ('7', 'Rodoviária'), ('8', 'Conduto / Rede Transmissão'),
                                                     ('9', 'Meios Próprios'), ('10', 'Entrada/Saída Ficta'),
                                                     ('11', 'Courier'), ('12', 'Handcarry')
                                                     ], 'Via de Transporte Internacional'),
        'tipo_importacao': fields.selection([('1', 'Por conta própria'),
                                             ('2', 'Por conta e ordens'),
                                             ('3', 'Encomenda')], 'Tipo de Importação'),
        #adquirinte
        
        'adquirinte_state_id': fields.many2one('res.country.state', u'UF', domain="[('country_id.code', '=', 'BR')]"),
        'cnpj': fields.char(u'CNPJ', size=14),
        

        
        
        
    }
declaracao_importacao()