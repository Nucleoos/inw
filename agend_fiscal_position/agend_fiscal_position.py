from openerp.osv import fields, osv

class agend_fiscal_position(osv.osv):
    _name = "agend.fiscal.position"
   
    def agend_fiscal_position_inw(self, cr, uid, context=None):
        
        tipo = 'input'
        imposto = self.pool.get('account.tax')
        empresa=self.pool.get('res.company')
        account_fiscal_position = self.pool.get("account.fiscal.position")
        account_position_tax = self.pool.get('account.fiscal.position.tax')
        categoria_fiscal_id = '5'
        empresa_ids = [9,5,4,7,6,1,8]
        imposto_ids = [1082,1271,1264,1057,1238,1203,1239,1241,1080,1270,1263,1056,1233,1205,1236,1235,1078,1269,1265,1055,1230,1207,1232,1231,1067,1267,1256,1052,1221,1213,1223,1222,1073,1266,1255,1053,1218,1216,1220,1219,1076,1268,1259,1054,1224,1211,1226,1225,1124,1122,1129,1121,1227,1209,1229,1228]
        
        for empresa_id in empresa_ids:
            empresa_brw = empresa.browse(cr, uid, empresa_id)
            nome = "Compra %s" %empresa_brw.name
            lista_impostos = []
            
                    
            dict = {
                    'name': nome,
                    'type': tipo,
                    'company_id': empresa_brw.id,
                    'fiscal_category_id' : categoria_fiscal_id
                    
                    }        
            position_fiscal_id = account_fiscal_position.create(cr, uid, dict)
            
            for imposto_id in imposto_ids:
                imposto_brw = imposto.browse(cr, uid, imposto_id)
                if imposto_brw.company_id.id != empresa_brw.id:
                    account_position_tax.create(cr, uid, {'tax_src_id':imposto_brw.id, 'position_id':position_fiscal_id}) 
        
        return True
    
agend_fiscal_position()
