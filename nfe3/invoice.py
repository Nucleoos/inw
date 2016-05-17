# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
import datetime
import re
import string
from openerp.addons import decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
                'date_hour_invoice': fields.datetime(
                                                u'Data e hora de emissão', readonly=True,
                                                select=True, help="Deixe em branco para usar a data atual"),
                'ind_final': fields.selection([
                                               ('0', u'Não'),
                                               ('1', u'Consumidor final')], u'Operação com Consumidor final', readonly=True,
                                                states={'draft': [('readonly', False)]}, required=False,
                                                help=u'Indica operação com Consumidor final.'),   
               'ind_pres': fields.selection([
                                            ('0', u'Não se aplica'),
                                            ('1', u'Operação presencial'),
                                            ('2', u'Operação não presencial, pela Internet'),
                                            ('3', u'Operação não presencial, Teleatendimento'),
                                            ('4', u'NFC-e em operação com entrega em domicílio'),
                                            ('9', u'Operação não presencial, outros'),
                                        ], u'Tipo de operação', readonly=True,
                                            states={'draft': [('readonly', False)]}, required=False,
                                            help=u'Indicador de presença do comprador no \
                                                \nestabelecimento comercial no momento \
                                                \nda operação.'),
                'date_in_out': fields.datetime(
                                            u'Data de Entrada/Saida', readonly=True,
                                            select=True, help="Deixe em branco para usar a data atual"),
                'nfe_version': fields.selection(
                                                [('1.10', '1.10'), ('2.00', '2.00'), ('3.10', '3.10')],
                                                u'Versão NFe', readonly=True,
                                                required=True),
                'dest_id': fields.selection([('1','Contribuinte ICMS'),
                                            ('2','Contribuinte ISENTO'),
                                            ('9','Não Contribuinte'),]
                                            ,'Tipo de Contribuinte', required=True, states={'draft': [('readonly', False)]}),

                }
    
    _defaults = {
                    'nfe_version': '3.10',
                    'ind_final': '1',
                    'ind_pres': '0',
                }
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            if vals['state'] == 'sefaz_export':
                vals['date_hour_invoice'] = datetime.date.today()
                vals['date_in_out'] = datetime.date.today()
        
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

    def punctuation_rm(self, cr, uid, ids, string_value):
        tmp_value = (re.sub('[%s]' % re.escape(string.punctuation), '',
                string_value or ''))
        return tmp_value
   
account_invoice()

class account_fiscal_position(osv.osv):
    _inherit = 'account.fiscal.position'
    
    _columns = {
                'id_dest': fields.selection([('1', u'Operação interna'),
                                            ('2', u'Operação interestadual'),
                                            ('3', u'Operação com exterior')],
                                            u'Local de destino da operação',
                                            help=u'Identificador de local de destino da operação.'),
                }
    
account_fiscal_position()


class res_company(osv.osv):
    _inherit = 'res.company'
    
    _columns = {
                'nfe_version': fields.selection([('1.10', '1.10'),
                                                 ('2.00', '2.00'),
                                                 ('3.10', '3.10'),
                                                 ], 'Versão NFe',
                                                required=True),
                }
    
    _defaults = {
        'nfe_version': '3.10',
            }
    
    
res_company()

