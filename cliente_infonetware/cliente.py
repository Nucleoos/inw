# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
from .tools import fiscal

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
                'cadastro': fields.selection([
                                            ('dados','Faltam dados'),
                                            ('ok','Cadastro Ok'),
                                            ('cnpj_cpf_invalido', 'CNPJ/CPF Invalido'),
                                            ('cnpj_cpf_duplicado', 'CNPJ/CPF Duplicado'),
                                            ],'Status'),

                'cpf_cpf_invalido': fields.char("CNPJ/CPF Invalido"),
		        'legal_name': fields.char(u'Razão Social', size=60, help="nome utilizado em documentos fiscais"),
                }

    _defaults = {
                 'country_id': 32
                 }

    def write(self, cr, uid, ids, vals, context={}):
        if type(ids) is int:
            objeto_atual = self.browse(cr, uid, ids)
        else:
            if ids:
                objeto_atual = self.browse(cr, uid, ids[0])
            else:
                return super(res_partner, self).write(cr, uid, ids, vals, context)
        if 'legal_name' in vals and vals['legal_name']:
            if len(vals['legal_name']) > 60:
                raise orm.except_orm(
                    (u'Aviso'),
                    (u'Maximo 60 Characteris na Razao Social.'))
        if type(ids) == list:
            if ids:
	           iid = ids[0]
        else:
            iid = ids

        if 'city' in vals:
            cidade = self.pool.get("l10n_br_base.city")

            if not 'state_id' in vals:
                vals['state_id'] = self.browse(cr, uid, iid).state_id.id

            cidade_ids = cidade.search(cr, uid, [('name', 'ilike', vals['city']), ('state_id', '=', vals['state_id'])])

            if cidade_ids:
                vals['l10n_br_city_id'] = cidade_ids[0]
            else:
                vals['city'] = False

        estrangeiro = False
        if 'country_id' in vals:
            country_id = vals['country_id']
        else:
            country_id = objeto_atual.country_id.id

        usuario = self.pool.get("res.users").browse(cr, uid, uid)

        if usuario.company_id.country_id.id != country_id:
            estrangeiro = True

        if 'cnpj_cpf' in vals and not estrangeiro:
            cnpj_cpf = str(vals['cnpj_cpf']).replace(".", "").replace("/", "").replace("-", "")
            tamanho_cnpj_cpf = len(cnpj_cpf)
            marcador = False

            if tamanho_cnpj_cpf == 14:
                vals['is_company'] = True
                marcador = True
            elif tamanho_cnpj_cpf == 11:
                vals['is_company'] = False
                marcador = True

            if marcador:
                vals['cnpj_cpf'] = self.onchange_mask_cnpj_cpf(cr, uid, False, vals['is_company'], vals['cnpj_cpf'])['value']['cnpj_cpf']

                if vals['is_company']:
                    cnpj_cpf_valido = fiscal.validate_cnpj(vals['cnpj_cpf'])
                else:
                    cnpj_cpf_valido = fiscal.validate_cpf(vals['cnpj_cpf'])


                if not cnpj_cpf_valido:
                    vals['cpf_cpf_invalido'] = vals['cnpj_cpf']
                    vals['cadastro'] = 'cnpj_cpf_invalido'
                    del vals['cnpj_cpf']
                else:
                    partner_ids = self.search(cr, uid, [('cnpj_cpf', '=', vals['cnpj_cpf'])])

                    if not partner_ids:
                        vals['cpf_cpf_invalido'] = False
                        vals['cadastro'] = 'ok'
                        vals['cnpj_cpf'] = self.onchange_mask_cnpj_cpf(cr, uid, ids, vals['is_company'], vals['cnpj_cpf'])['value']['cnpj_cpf']

                    else:

                        atual = False
                        if len(partner_ids) == 1 and partner_ids[0] == iid:
                            atual = True

                        if not atual:
                            if uid == 1:
                                vals['cpf_cpf_invalido'] = vals['cnpj_cpf']
                                vals['cadastro'] = 'cnpj_cpf_duplicado'
                                del vals['cnpj_cpf']
                            else:
                                raise orm.except_orm((u'Aviso'), (u'Não é permitido duplicar o CNPJ. Já existe um cliente com  este CNPJ cadastrado.'))
            else:
                if not type(vals['cnpj_cpf']) is bool:
                    vals['cpf_cpf_invalido'] = vals['cnpj_cpf']
                    vals['cadastro'] = 'cnpj_cpf_invalido'
                    del vals['cnpj_cpf']


        if 'company_id' in vals:

            if not 'child_ids' in vals:
                child_ids = objeto_atual.child_ids
            else:
                child_ids = vals['parent_ids']

            if child_ids:
                context['cascata'] = True
                for child_id in child_ids:
                    self.write(cr, uid, [child_id.id], {'company_id': vals['company_id']}, context)

            else:
                if not 'parent_id' in vals:
                    parent_id = objeto_atual.parent_id.id
                else:
                    parent_id = vals['parent_id']


                if parent_id:
                    if not 'cascata' in context:
                        raise orm.except_orm((u'Aviso'), (u'Altere a empresa pelo contato pai.'))

        return super(res_partner, self).write(cr, uid, ids, vals, context)


    def create(self, cr, uid, vals, context=None):
        if 'legal_name' in vals and vals['legal_name']:
            if len(vals['legal_name']) > 60:
                raise orm.except_orm((u'Aviso'), (u'Maximo 60 Characteris na Razao Social.'))

        if 'city' in vals:
            if 'state_id' in vals:
                cidade = self.pool.get("l10n_br_base.city")

                cidade_ids = cidade.search(cr, uid, [('name', 'ilike', vals['city']), ('state_id', '=', vals['state_id'])])

                if cidade_ids:
                    vals['l10n_br_city_id'] = cidade_ids[0]
                else:
                    vals['city'] = False
            else:
                vals['city'] = False

        estrangeiro = False
        if 'country_id' in vals:
            usuario = self.pool.get("res.users").browse(cr, uid, uid)
            if usuario.company_id.country_id.id != vals['country_id']:
                estrangeiro = True

        if 'cnpj_cpf' in vals and not estrangeiro:

            cnpj_cpf = str(vals['cnpj_cpf']).replace(".", "").replace("/", "").replace("-", "")
            tamanho_cnpj_cpf = len(cnpj_cpf)
            marcador = False

            if tamanho_cnpj_cpf == 14:
                vals['is_company'] = True
                marcador = True
            elif tamanho_cnpj_cpf == 11:
                vals['is_company'] = False
                marcador = True

            if marcador:
                vals['cnpj_cpf'] = self.onchange_mask_cnpj_cpf(cr, uid, False, vals['is_company'], vals['cnpj_cpf'])['value']['cnpj_cpf']

                if vals['is_company']:
                    cnpj_cpf_valido = fiscal.validate_cnpj(vals['cnpj_cpf'])
                else:
                    cnpj_cpf_valido = fiscal.validate_cpf(vals['cnpj_cpf'])

                if not cnpj_cpf_valido:
                    vals['cpf_cpf_invalido'] = vals['cnpj_cpf']
                    vals['cadastro'] = 'cnpj_cpf_invalido'
                    del vals['cnpj_cpf']

                else:
                    partner_ids = self.search(cr, uid, [('cnpj_cpf', '=', vals['cnpj_cpf'])])

                    if not partner_ids:
                        vals['cpf_cpf_invalido'] = False
                        vals['cadastro'] = 'ok'
                        vals['cnpj_cpf'] = vals['cnpj_cpf']


                        tipo_fiscal = self.pool.get("l10n_br_account.partner.fiscal.type")

                        if vals['is_company']:
                            if vals['inscr_est']:
                                tipo_fiscal_id = tipo_fiscal.search(cr, uid, [('is_company', '=', True), ('code', '=', 'CT')])
                            else:
                                tipo_fiscal_id = tipo_fiscal.search(cr, uid, [('is_company', '=', True), ('code', '=', 'NC')])
                        else:
                            tipo_fiscal_id = tipo_fiscal.search(cr, uid, [('is_company', '=', False), ('code', '=', 'NC')])

                        if tipo_fiscal_id:
                            tipo_fiscal_id = tipo_fiscal_id[0]
                        else:
                            tipo_fiscal_id = False

                        vals['partner_fiscal_type_id'] = tipo_fiscal_id

                    else:
                        if uid == 1:
                            vals['cpf_cpf_invalido'] = vals['cnpj_cpf']
                            vals['cadastro'] = 'cnpj_cpf_duplicado'
                            del vals['cnpj_cpf']
                        else:
                            raise orm.except_orm((u'Aviso'), (u'Não é permitido duplicar o CNPJ. Já existe um cliente com  este CNPJ cadastrado.'))

            else:
                vals['cpf_cpf_invalido'] = vals['cnpj_cpf']
                vals['cadastro'] = 'cnpj_cpf_invalido'
                del vals['cnpj_cpf']

        vals['company_id'] = False
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        zip = False
        cpf_cnpj = False
        obj = self.browse(cr, uid, res)
#         if not obj.is_company:
#             d = {
#                  'legal_name':obj.name
#                  }
#             self.write(cr, uid, [res], d)
#         if obj.zip:
#             z = self.pool.get('l10n_nr.zip').search(cr, uid, [('zip','=',obj.zip)])
#             if z:
#                 zip = True
#         if obj.cnpj_cpf:
#             c = self.onchange_mask_cnpj_cpf(cr, uid, res, obj.is_company, obj.cnpj_cpf)
#             if c:
#                 cpf_cnpj = True
#
#         if zip and cpf_cnpj:
#             dict = {
#                     'cadastro':'ok'
#                     }
#         else:
#             dict = {
#                     'cadastro':'dados'
#                     }
#         self.write(cr, uid, res, dict)
        return res



    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []

        if uid != 1:
            usuario = self.pool.get("res.users").browse(cr, uid, uid)
            args.append(['company_id', 'in', [usuario.company_id.id, False]])

        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):

            self.check_access_rights(cr, uid, 'read')
            where_query = self._where_calc(cr, uid, args, context=context)
            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            # TODO: simplify this in trunk with `display_name`, once it is stored
            # Perf note: a CTE expression (WITH ...) seems to have an even higher cost
            #            than this query with duplicated CASE expressions. The bulk of
            #            the cost is the ORDER BY, and it is inevitable if we want
            #            relevant results for the next step, otherwise we'd return
            #            a random selection of `limit` results.
            query = ('''SELECT res_partner.id FROM res_partner
                                          LEFT JOIN res_partner company
                                               ON res_partner.parent_id = company.id'''
                        + where_str + ''' (res_partner.email ''' + operator + ''' %s OR
                              CASE
                                   WHEN company.id IS NULL OR res_partner.is_company
                                       THEN res_partner.name
                                   ELSE company.name || ', ' || res_partner.name
                              END ''' + operator + ''' %s)
                        ORDER BY
                              CASE
                                   WHEN company.id IS NULL OR res_partner.is_company
                                       THEN res_partner.name
                                   ELSE company.name || ', ' || res_partner.name
                              END''')

            where_clause_params += [search_name, search_name]
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            cr.execute(query, where_clause_params)
            ids = map(lambda x: x[0], cr.fetchall())

            if ids:
                return self.name_get(cr, uid, ids, context)
            else:
                return []
        return super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)

res_partner()
