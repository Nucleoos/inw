# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from ..cliente_infonetware.tools import fiscal


class res_partner(osv.osv):
    _inherit = "res.partner"
    
    
    def _check_cnpj_cpf(self, cr, uid, ids):
        usuario = self.pool.get("res.users").browse(cr, uid, uid)
        
        for partner in self.browse(cr, uid, ids):
            if partner.country_id.id != usuario.company_id.country_id.id:
                estrangeiro = True
            else:
                estrangeiro = False
            
            if not partner.cnpj_cpf or estrangeiro:
                continue

            if partner.is_company:
                if not fiscal.validate_cnpj(partner.cnpj_cpf):
                    return False
            elif not fiscal.validate_cpf(partner.cnpj_cpf):
                    return False

        return True
    
    _columns = {
                'only': fields.boolean('Deixar campo Estado e Municipio READONLY outros paises'),
                }
    
    def onchange_country(self, cr, uid, ids, pais, context=None):
        user = self.pool.get('res.users')
        estado = self.pool.get('res.country.state')
        municipio =  self.pool.get('l10n_br_base.city')
        res = {'value':{}}
        company = user.browse(cr, uid, uid).company_id
        if company.country_id.id != pais and pais != False:
            est = estado.search(cr, uid, [('code','=','EX')])[0]
            if est:
                mun = municipio.search(cr, uid, [('name','=','Exterior'),('state_id','=',est)])[0]
                if mun:
                    res['value']['state_id'] = est
                    res['value']['l10n_br_city_id'] = mun
                    res['value']['only'] = True
                    if ids:
                        self.write(cr, uid, ids, {'state_id': est, 'l10n_br_city_id':mun, 'only':True})
        else:
            res['value']['state_id'] = False
            res['value']['l10n_br_city_id'] = False
            res['value']['only'] = False
            if ids:
                self.write(cr, uid, ids, {'state_id': False, 'l10n_br_city_id':False, 'only':False})
        return res   
    
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            est = self.pool.get('res.country.state').browse(cr, uid, state_id).code
            if est != 'EX':
                country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
                return {'value':{'country_id':country_id}}
        return {}
    
    
    def onchange_mask_cnpj_cpf(self, cr, uid, ids, is_company, cnpj_cpf, context={}):
        res = True
        
        only = False
        if 'only' in context:
            only = context['only']
        
        if not only:
            res = super(res_partner, self).onchange_mask_cnpj_cpf(cr, uid, ids, is_company, cnpj_cpf)
        return res
    
    def create(self, cr, uid, vals, context=None):
        user = self.pool.get('res.users')
        estado = self.pool.get('res.country.state')
        municipio =  self.pool.get('l10n_br_base.city')
        if 'country_id' in vals:
            company = user.browse(cr, uid, uid).company_id
            if vals['country_id'] != company.country_id.id:
                est = estado.search(cr, uid, [('code','=','EX')])[0]
                if est:
                    mun = municipio.search(cr, uid, [('name','=','Exterior'),('state_id','=',est)])[0]
                    if mun:
                        vals['state_id'] = est
                        vals['l10n_br_city_id'] = mun
        return super(res_partner, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users')
        estado = self.pool.get('res.country.state')
        municipio =  self.pool.get('l10n_br_base.city')
        if 'country_id' in vals:
            company = user.browse(cr, uid, uid).company_id
            if vals['country_id'] != company.country_id.id:
                est = estado.search(cr, uid, [('code','=','EX')])[0]
                if est:
                    mun = municipio.search(cr, uid, [('name','=','Exterior'),('state_id','=',est)])[0]
                    if mun:
                        vals['state_id'] = est
                        vals['l10n_br_city_id'] = mun
                        vals['only'] = True
            else:
                vals['only'] = False
        else:
            vals['only'] = False
        return super(res_partner, self).write(cr, uid, ids, vals, context=context)
    
    _constraints = [
        (_check_cnpj_cpf, u'CNPJ/CPF invalido!', ['cnpj_cpf']),
    ]
res_partner()
