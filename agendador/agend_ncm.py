from openerp.osv import fields, osv

class account_product_fiscal_classification(osv.osv):
    _inherit = 'account.product.fiscal.classification'
   
    def agend_ncm(self, cr, uid, context=None):
#         model = self.browse(cr, uid, 273)
#        excluir imposto do ncm
#        obj_b = self.search(cr, uid, [('id','>=',269),('id','<=',270)])
        for i in self.browse(cr, uid, [69,249,227,79,230,80,232,91,128,131,137,139,141,142,150,93,231]):
#            list1 = []
#            list2 = []
#            for j in i.sale_tax_definition_line:
#                if not j.tax_id.id in list1:
#                    list1.append(j.tax_id.id)
#                else:
#                    list2.append(j.id)
#            if list2:
#                for a in list2:
#                    self.pool.get("l10n_br_tax.definition.sale").unlink(cr, uid, [a], context=context)
                  
#              incluir imposto no ncm       
#             if not i.id == 68:
            list = [[1238,73],[1233,78],[1230,83],[1221,68],[1218,93],[1224,88],[1227,108]] 
            for l in list:
                dict = {
                    'tax_id': l[0],#l.tax_id.id,
                    'tax_code_id': l[1],#l.tax_code_id.id,
                    'fiscal_classification_id': i.id,
                    }
                self.pool.get('l10n_br_tax.definition.purchase').create(cr, uid, dict)
                       
        return True
   #[1057,73],[1056,78],[1055,83],[1052,68],[1053,93],[1054,88],[1121,108]
   #[1082,71],[1271,74],[1264,75],[1080,76],[1270,79],[1263,80],[1078,81],[1269,106],[1265,85],[1067,66],[1267,69],[1256,70],[1073,91],[1266,107],[1255,95],[1076,86],[1268,89],[1259,90],[1124,62],[1122,57],[1129,61]
   #[1126,60],[1129,61],[1124,62],[1123,59],[1121,56],[1122,7],[1102,43],[1108,44],[1062,19],[1051,9],[1114,50],[1120,26],[1096,36],[1103,49],[1058,4],[1,2],[1109,20],[1116,55],[1101,42],[1107,45],[1061,18],[1050,8],[1113,24],[1119,51],[1100,41],[1106,46],[1060,17],[1049,7],[1112,23],[1118,52],[1099,40],[1105,47],[1059,16],[1048,6],[1111,22],[1117,54],[1098,39],[1104,48],[1070,3],[1047,5],[1110,21],[1115,53]
account_product_fiscal_classification()
