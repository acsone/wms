# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
from datetime import date

STR_BOOL = {
    'Y': True
}

LANG = {
    'FR': 'fr_BE',
    'NL': 'nl_BE',
    'D': 'de_DE',
}


UOM = {
    0: 'product.product_uom_unit',
    2: 'product.product_uom_meter',
    7: '__setup__.product_uom_sac',
    8: '__setup__.product_uom_boite',
    16: '__setup__.product_uom_blister',
    17: '__setup__.product_uom_plateau',
    55: '__setup__.product_uom_liasse',
    56: '__setup__.product_uom_flacon',
}


DEFAULT_PROD_CAT = 'specific_data.product_categ_undefined'
PRODUCT_CATEGORY = {i: DEFAULT_PROD_CAT for i in range(100)}
PRODUCT_CATEGORY.update({
    1: 'specific_data.product_categ_ali_dietetique',
    2: 'specific_data.product_categ_ali_physio',
    3: 'specific_data.product_categ_antimicrobiens',
    4: 'specific_data.product_categ_pis',
    6: 'specific_data.product_categ_oeil_oreille',
    7: 'specific_data.product_categ_antiparasite',
    9: 'specific_data.product_categ_sys_nerveux',
    10: 'specific_data.product_categ_vasculo',
    11: 'specific_data.product_categ_vitamines',
    12: 'specific_data.product_categ_vaccins',
    13: 'specific_data.product_categ_mat_sutures',
    14: 'specific_data.product_categ_divers_veto',
    15: 'specific_data.product_categ_humain',
    # All product from this go to stupefiant
    # 16: 'specific_data.product_categ_ketamine',
    16: 'specific_data.product_categ_stupefiant',
    18: 'specific_data.product_categ_phytosanitaires',
    20: 'specific_data.product_categ_homeo',
    23: 'specific_data.product_categ_hormones',
    24: 'specific_data.product_categ_mat_cardio',
    26: 'specific_data.product_categ_divers_para',
    29: 'specific_data.product_categ_chimiques',
    30: 'specific_data.product_categ_psychotropes_25',
    31: 'specific_data.product_categ_stupefiant',
    32: 'specific_data.product_categ_mat_dentisterie',
    34: 'specific_data.product_categ_ali_comp',
    35: 'specific_data.product_categ_mat_equins',
    36: 'specific_data.product_categ_mat_rurale',
    44: 'specific_data.product_categ_topiques',
    52: 'specific_data.product_categ_mat_sav',
    55: 'specific_data.product_categ_mat_ortho',
    56: 'specific_data.product_categ_mat_sut_bobine',
    58: 'specific_data.product_categ_mat_equipement',
    59: 'specific_data.product_categ_mat_instrumentation',
    60: 'specific_data.product_categ_mat_img_echo',
    61: 'specific_data.product_categ_mat_img_radio',
#    62: 'specific_data.product_categ_psychotropes_38', # empty category
    63: 'specific_data.product_categ_mat_img_endo',
    66: 'specific_data.product_categ_mat_occasion',
    68: 'specific_data.product_categ_mat_conso',
    71: 'specific_data.product_categ_mat_petshop',
    75: 'specific_data.product_categ_importation',
    91: 'specific_data.product_categ_finance_frais',
    92: 'specific_data.product_categ_finance_remises_fournisseurs',
    93: 'specific_data.product_categ_mat_marge',
    94: 'specific_data.product_categ_finance_bonus_actionnaires',
    95: 'specific_data.product_categ_finance_cheques_clients',
    96: 'specific_data.product_categ_ali_divers',
    97: 'specific_data.product_categ_finance_remises_partenariat',
    98: 'specific_data.product_categ_finance_remises_geste_commercial',
    99: 'specific_data.product_categ_finance_divers_divers',
})

PRODUCT_TYPE = {
    15: 'service',  # specific_data.product_categ_humain
}

PRODUCT_WITH_APB_TAX_CATEG = [
    # Products Belgian VET, specific_data.product_categ_vet_belges
    3,  # specific_data.product_categ_antimicrobiens
    4,  # specific_data.product_categ_pis
    6,  # specific_data.product_categ_oeil_oreille
    7,  # specific_data.product_categ_antiparasite
    9,  # specific_data.product_categ_sys_nerveux
    10,  # specific_data.product_categ_vasculo
    11,  # specific_data.product_categ_vitamines
    12,  # specific_data.product_categ_vaccins
    14,  # specific_data.product_categ_divers_veto
    23,  # specific_data.product_categ_hormones
    30,  # specific_data.product_categ_psychotropes_25
    31,  # specific_data.product_categ_stupefiant
    44,  # specific_data.product_categ_topiques
    62,  # specific_data.product_categ_psychotropes_38
    # Products importation
    75,  # specific_data.product_categ_importation
]

PRODUCT_ANTIBIO_TAX = {
    '8888001': '001',
    '8888002': '002',
    '8888003': '003',
    '8888004': '004',
    '8888005': '005',
    '8888006': '006',
    '8888007': '007',
    '8888008': '007',
    '8888009': '008',
    '8888010': '009',
    '8888011': '010',
    '8888012': '011',
    '8888013': '013',
    '8888014': '013',
    '8888015': '013',
    '8888016': '014',
    '8888017': '016',
    '8888018': '017',
    '8888019': '018',
    '8888020': '020',
    '8888021': '026',
    '8888022': '031',
    '8888023': '032',
    '8888024': '035',
    '8888025': '037',
    '8888026': '039',
    '8888027': '041',
    '8888028': '042',
    '8888029': '050',
    '8888030': '053',
    '8888031': '053',
    '8888032': '061',
    '8888033': '063',
    '8888034': '079',
    '8888035': '088',
    '8888036': '090',
    '8888037': '092',
    '8888038': '105',
    '8888039': '113',
    '8888040': '123',
    '8888041': '126',
    '8888042': '131',
    '8888043': '140',
    '8888044': '158',
    '8888045': '175',
    '8888046': '204',
    '8888047': '263',
    '8888048': '033',
    '8888049': '066',
    '8888050': '012',
    '8888051': '024',
    '8888214': '214',
    '8888888': '005',
}


PRODUCT_STATES = {
    'A': 'specific_purchase.product_state_a',
    'D': 'specific_purchase.product_state_d',
    'H': 'specific_purchase.product_state_h',
    'I': 'specific_purchase.product_state_i',
    'L': 'specific_purchase.product_state_l',
    'M': 'specific_purchase.product_state_m',
    'N': 'specific_purchase.product_state_n',
}

PRODUCT_STORAGE_TEMPERATURES = {
    0: 'specific_product.product_storage_temperature_ambient',
    2: 'specific_product.product_storage_temperature_minus_12',
    5: 'specific_product.product_storage_temperature_15',
    6: 'specific_product.product_storage_temperature_6',
}

PRODUCT_WEB_PUBLISHED = {
    '0': False,
    '1': True,
}

# We could just prefix by __setup__.res_user_
# but it will fail the import if user does not exist in Odoo.
USERS = {
    1: '__setup__.res_user_1',
    2: '__setup__.res_user_2',
    21: '__setup__.res_user_21',
    5: '__setup__.res_user_5',
    6: '__setup__.res_user_6',
    7: '__setup__.res_user_7',
    11: '__setup__.res_user_11',
    12: '__setup__.res_user_12',
    22: '__setup__.res_user_22',
    13: '__setup__.res_user_13',
    23: '__setup__.res_user_23',
    14: '__setup__.res_user_14',
    15: '__setup__.res_user_15',
    16: '__setup__.res_user_16',
    17: '__setup__.res_user_17',
    18: '__setup__.res_user_18',
    19: '__setup__.res_user_19',
    20: '__setup__.res_user_20',
}

PARTNER_ALCYON_CATEGORY = {
    1: 'specific_partner.partner_category_veterinary',
    2: 'specific_partner.partner_category_pharmacy',
    4: 'specific_partner.partner_category_callcenter',
    5: 'specific_partner.partner_category_pharmacy',
    6: 'specific_partner.partner_category_pharmacy',
    7: 'specific_partner.partner_category_pharmacy',
    9: 'specific_partner.partner_category_pharmacy',
    10: 'specific_partner.partner_category_pharmacy',
    11: 'specific_partner.partner_category_customerexport',
    15: 'specific_partner.partner_category_pharmacy',
    16: 'specific_partner.partner_category_pharmacy',
    17: 'specific_partner.partner_category_pharmacy',
    18: 'specific_partner.partner_category_pharmacy',
    19: 'specific_partner.partner_category_pharmacy',
    20: 'specific_partner.partner_category_student',
    # Have been added in odoo
    # 21: 'specific_partner.partner_category_alcyonaire'
    # 22: 'specific_partner.partner_category_med_export',
    # 23: 'specific_partner.partner_category_only_material',
    #
    # 97: specific_partner.partner_category_user'
    # 98: 'specific_partner.partner_category_supplier'
    # Those became Customer Tags see below
    # 3: 'specific_partner.partner_category_veto',
    # 8: 'specific_partner.partner_category_university',
    # 12: 'specific_partner.partner_category_fund_alcyon',
    # 13: 'specific_partner.partner_category_fund_pasteur',
    # 14: 'specific_partner.partner_category_other',
    # 99: 'specific_partner.partner_category_various',
    # And others are transform to pharmacy so adding them in tags as well
}

CUSTOMER_CATEGORY = {
    'cpcl17': '__setup__.customer_category_petits_animaux',
    'cpcl18': '__setup__.customer_category_grands_animaux',
    'cpcl19': '__setup__.customer_category_equins',
    'cpcl20': '__setup__.customer_category_clinique',
    'cpcl21': '__setup__.customer_category_nac',
    'cpcl22': '__setup__.customer_category_fonctionnaire',
    'cpcl23': '__setup__.customer_category_inseminateur',
    'cpcl24': '__setup__.customer_category_comportementaliste',
    'cpcl25': '__setup__.customer_category_enseignant',
}

# Some Alcyon Category are not imported but set as Tags on the customer in Odoo
ALCYON_CATEGORY_TO_CUSTOMER_CATEGORY = {
    3: '__setup__.customer_category_sous_veto',
    # Those are the Alcyon Category that are transform to another Alcyon Category
    5: '__setup__.customer_category_petit_grossiste',
    6: '__setup__.customer_category_epece',
    7: '__setup__.customer_category_pharma_sante',
    9: '__setup__.customer_category_pharma_belge',
    10: '__setup__.customer_category_pasteur_humain',
    15: '__setup__.customer_category_life',
    16: '__setup__.customer_category_multipharma',
    17: '__setup__.customer_category_backup',
    18: '__setup__.customer_category_alpharepartition',
    19: '__setup__.customer_category_vpharma',

    8: '__setup__.customer_category_universite',
    12: '__setup__.customer_category_caisse_alcyon',
    13: '__setup__.customer_category_caisse_pasteur',
    14: '__setup__.customer_category_autres',
    99: '__setup__.customer_category_divers',
}

ACCOUNT_PAYABLE = {
    1: '__setup__.account_440000',
    2: '__setup__.account_440100',
}

CUSTOMER_ACTIVE = {
    # In AS400, 1 means customer blocked => so inactive.
    1: False,
    0: True,
}

PARTNER_TITLE = {
     11: 'base.res_partner_title_madam',
     10: 'base.res_partner_title_mister',
     7: 'base.res_partner_title_assveter',
     1: 'base.res_partner_title_dctveter',
     12: 'base.res_partner_title_doctor',
}

PARTNER_LEGAL_ENTITY = {
    2: 'Org.Resp.V10',
    3: 'Clinique Vétérinaire',
    4: 'SPRLU',
    5: 'SPRL',
    6: 'S.A.',
    8: 'S.C.',
    9: 'Pharmacie',
    13: 'ASBL',
    14: 'A.D.F.',
    15: 'S.A.R.L.',
    16: 'S.C.R.L.',
}

PARTNER_IS_COMPANY = {
    k: True for k in [2, 3, 4, 5, 6, 8, 9, 13, 14, 15, 16]
}

CLIENT_DISCOUNT_PRICELIST = {
    5: '__setup__.pricelist_5',
    6: '__setup__.pricelist_6',
    7: '__setup__.pricelist_7',
    8: '__setup__.pricelist_8',
    9: '__setup__.pricelist_9',
    10: '__setup__.pricelist_10',
    11: '__setup__.pricelist_11',
    12: '__setup__.pricelist_12',
    13: '__setup__.pricelist_13',
    14: '__setup__.pricelist_14',
    15: '__setup__.pricelist_15',
    100: '__setup__.pricelist_100',
    103: '__setup__.pricelist_103',
    104: '__setup__.pricelist_104',
    105: '__setup__.pricelist_105',
    106: '__setup__.pricelist_106',
    107: '__setup__.pricelist_107',
    108: '__setup__.pricelist_108',
    109: '__setup__.pricelist_109',
    110: '__setup__.pricelist_110',
    111: '__setup__.pricelist_111',
    112: '__setup__.pricelist_112',
    210: '__setup__.pricelist_210',
    211: '__setup__.pricelist_211',
    212: '__setup__.pricelist_212',
    213: '__setup__.pricelist_213',
    214: '__setup__.pricelist_214',
    301: '__setup__.pricelist_301',
    302: '__setup__.pricelist_302',
    303: '__setup__.pricelist_303',
    304: '__setup__.pricelist_304',
    308: '__setup__.pricelist_308',
    310: '__setup__.pricelist_310',
    311: '__setup__.pricelist_311',
    312: '__setup__.pricelist_312',
    314: '__setup__.pricelist_314',
    315: '__setup__.pricelist_315',
    316: '__setup__.pricelist_316',
    317: '__setup__.pricelist_317',
    318: '__setup__.pricelist_318',
    319: '__setup__.pricelist_319',
    320: '__setup__.pricelist_320',
    321: '__setup__.pricelist_321',
    322: '__setup__.pricelist_322',
    323: '__setup__.pricelist_323',
    401: '__setup__.pricelist_401',
    402: '__setup__.pricelist_402',
    403: '__setup__.pricelist_403',
    404: '__setup__.pricelist_404',
    405: '__setup__.pricelist_405',
    406: '__setup__.pricelist_406',
    407: '__setup__.pricelist_407',
    410: '__setup__.pricelist_410',
    411: '__setup__.pricelist_411',
    412: '__setup__.pricelist_412',
    600: '__setup__.pricelist_600',
}

CLIENT_PROMOTION_PRICELIST = {
    db2_id: True for db2_id in
    (100, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 210, 211, 212,
     213, 214, 301, 302, 303, 304, 308, 310, 311, 312, 314, 315, 316, 317,
     318, 319, 320, 321, 322, 323, 401, 402, 403, 404, 405, 406, 407, 410,
     411, 412, 600)
}

CLIENT_FISCAL_POSITION = {
  0: '__setup__.fiscal_position_nat',
  1: '__setup__.fiscal_position_nat',
  2: '',
}

CLIENT_DELIVERY_METHODS = {
    1: '__setup__.deliver_carrier_alcyon',
    2: '__setup__.deliver_carrier_transporter',
    3: '__setup__.deliver_carrier_post_pack',
    4: '__setup__.deliver_carrier_delegated',
    9: '__setup__.deliver_carrier_by_client',
    89: '__setup__.deliver_carrier_invoice',
}

PAYMENT_TERMS = {
    1: 'account.account_payment_term_net',
    2: '__setup__.account_payment_term_d60',
    3: '__setup__.account_payment_term_d90',
    4: '__setup__.account_payment_term_f30',
    5: '__setup__.account_payment_term_f60',
    6: '__setup__.account_payment_term_f90',
    7: '__setup__.account_payment_term_cr',
    8: '__setup__.account_payment_term_d10',
    9: '__setup__.account_payment_term_f120',
    10: 'account.account_payment_term_immediate',
    11: 'account.account_payment_term_net',
    12: '__setup__.account_payment_term_d60',
    13: '__setup__.account_payment_term_d90',
    14: '__setup__.account_payment_term_f30',
    15: '__setup__.account_payment_term_f60',
    16: '__setup__.account_payment_term_f90',
    17: '__setup__.account_payment_term_d7',
    18: '__setup__.account_payment_term_f0',
    19: 'account.account_payment_term_15days',
    20: 'account.account_payment_term_immediate',
    21: '__setup__.account_payment_term_d8',
    22: '__setup__.account_payment_term_f15',
    23: '__setup__.account_payment_term_d7',
    25: '__setup__.account_payment_term_d5',
    26: '__setup__.account_payment_term_d8',
    27: '__setup__.account_payment_term_d10',
    28: '__setup__.account_payment_term_d14',
    29: '__setup__.account_payment_term_d45',
    30: '__setup__.account_payment_term_d120',
    32: '__setup__.account_payment_term_d27',
    33: '__setup__.account_payment_term_d45',
    34: '__setup__.account_payment_term_f45',
    35: '__setup__.account_payment_term_d10',
    36: '__setup__.account_payment_term_d21',
    91: '__setup__.account_payment_term_f5',
    92: '__setup__.account_payment_term_f10',
    93: '__setup__.account_payment_term_f15',
    94: '__setup__.account_payment_term_f20',
    95: '__setup__.account_payment_term_f25',
}

CLIENT_PAYMENT_TERMS = PAYMENT_TERMS.copy()
CLIENT_PAYMENT_TERMS[10] = '__setup__.account_payment_term_d7'

SUPPLIER_PAYMENT_MODES = {
    1: '__setup__.account_payment_mode_out_man',
    2: '__setup__.account_payment_mode_out_dom',
    3: '__setup__.account_payment_mode_out_man',
    4: '__setup__.account_payment_mode_out_man',
    5: '__setup__.account_payment_mode_out_sep',
}

CLIENT_PAYMENT_MODES = {
    11: '__setup__.account_payment_mode_1',
    12: '__setup__.account_payment_mode_1',
    17: '__setup__.account_payment_mode_1',
    32: '__setup__.account_payment_mode_1',
}

PRODUCT_TRACKING = {
    0: 'none',
    1: 'lot',
    2: 'lot',
    4: 'lot',
}

COUNTRY = {
    1: 'base.fr',
    2: 'base.be',
    3: 'base.nl',
    4: 'base.de',
    5: 'base.it',
    6: 'base.uk',
    7: 'base.ie',
    8: 'base.dk',
    9: 'base.gr',
    10: 'base.pt',
    11: 'base.es',
    12: 'base.lu',
    24: 'base.is',
    27: 'base.sj',
    28: 'base.no',
    30: 'base.se',
    32: 'base.fi',
    37: 'base.li',
    38: 'base.at',
    39: 'base.ch',
    41: 'base.fo',
    43: 'base.sj',
    44: 'base.gi',
    45: 'base.va',
    46: 'base.mt',
    47: 'base.sm',
    52: 'base.tr',
    53: 'base.ee',
    54: 'base.lv',
    55: 'base.lt',
    60: 'base.pl',
    61: 'base.cz',
    63: 'base.sk',
    64: 'base.hu',
    66: 'base.ro',
    68: 'base.bg',
    70: 'base.al',
    72: 'base.ua',
    74: 'base.pn',
    75: 'base.ru',
    76: 'base.ge',
    77: 'base.am',
    78: 'base.az',
    79: 'base.kz',
    80: 'base.tm',
    81: 'base.uz',
    82: 'base.tj',
    83: 'base.kg',
    91: 'base.si',
    92: 'base.hr',
    93: 'base.ba',
    96: 'base.mk',
    204: 'base.ma',
    208: 'base.dz',
    212: 'base.tn',
    220: 'base.eg',
    224: 'base.sd',
    228: 'base.mr',
    232: 'base.ml',
    236: 'base.bf',
    240: 'base.ne',
    244: 'base.td',
    247: 'base.cv',
    248: 'base.sn',
    252: 'base.gm',
    260: 'base.gn',
    264: 'base.sl',
    272: 'base.ci',
    276: 'base.gh',
    280: 'base.tg',
    284: 'base.bj',
    302: 'base.cm',
    310: 'base.gq',
    314: 'base.ga',
    318: 'base.cg',
    324: 'base.rw',
    328: 'base.bi',
    330: 'base.ao',
    338: 'base.dj',
    342: 'base.so',
    346: 'base.ke',
    350: 'base.ug',
    352: 'base.tz',
    355: 'base.sc',
    366: 'base.mz',
    370: 'base.mg',
    373: 'base.mu',
    375: 'base.km',
    377: 'base.yt',
    378: 'base.zm',
    382: 'base.zw',
    386: 'base.mw',
    388: 'base.za',
    389: 'base.na',
    391: 'base.bw',
    393: 'base.sz',
    395: 'base.ls',
    400: 'base.us',
    404: 'base.ca',
    412: 'base.mx',
    413: 'base.bm',
    416: 'base.gt',
    424: 'base.hn',
    432: 'base.ni',
    436: 'base.cr',
    442: 'base.pa',
    446: 'base.ai',
    448: 'base.cu',
    452: 'base.ht',
    453: 'base.bs',
    459: 'base.ag',
    460: 'base.dm',
    462: 'base.mq',
    463: 'base.ky',
    464: 'base.jm',
    469: 'base.bb',
    470: 'base.ms',
    473: 'base.gd',
    474: 'base.aw',
    480: 'base.co',
    488: 'base.gy',
    496: 'base.gf',
    504: 'base.pe',
    508: 'base.br',
    512: 'base.cl',
    516: 'base.bo',
    520: 'base.py',
    524: 'base.uy',
    528: 'base.ar',
    600: 'base.cy',
    604: 'base.lb',
    608: 'base.sy',
    612: 'base.iq',
    616: 'base.ir',
    624: 'base.il',
    628: 'base.jo',
    632: 'base.sa',
    644: 'base.qa',
    649: 'base.om',
    653: 'base.ye',
    662: 'base.pk',
    664: 'base.in',
    667: 'base.mv',
    669: 'base.lk',
    672: 'base.np',
    675: 'base.bt',
    680: 'base.th',
    684: 'base.la',
    700: 'base.id',
    703: 'base.bn',
    706: 'base.sg',
    708: 'base.ph',
    716: 'base.mn',
    720: 'base.cn',
    724: 'base.kp',
    728: 'base.kr',
    732: 'base.jp',
    736: 'base.tw',
    740: 'base.hk',
    743: 'base.mo',
    800: 'base.au',
    803: 'base.nr',
    804: 'base.nz',
    807: 'base.tv',
    811: 'base.wf',
    812: 'base.ki',
    813: 'base.pn',
    815: 'base.fj',
    816: 'base.vu',
    817: 'base.to',
    823: 'base.fm',
}

CEE_COUNTRIES = {
    1: 'base.fr',
    2: 'base.be',
    3: 'base.nl',
    4: 'base.de',
    5: 'base.it',
    6: 'base.uk',
    7: 'base.ie',
    8: 'base.dk',
    9: 'base.gr',
    10: 'base.pt',
    11: 'base.es',
    12: 'base.lu',
}

PRODUCT_SALE_VAT = {
    0: "l10n_be.1_attn_VAT-OUT-00-L",
    1: "l10n_be.1_attn_VAT-OUT-06-L",
    2: "l10n_be.1_attn_VAT-OUT-12-L",
    3: "l10n_be.1_attn_VAT-OUT-21-L",
}

PRODUCT_PURCHASE_VAT = {
    0: "l10n_be.1_attn_VAT-IN-V81-00",
    1: "l10n_be.1_attn_VAT-IN-V81-06",
    2: "l10n_be.1_attn_VAT-IN-V81-12",
    3: "l10n_be.1_attn_VAT-IN-V81-21",
}

PRODUCT_ROUTES = {
    0: "purchase.route_warehouse0_buy",
    1: "stock.route_warehouse0_mto,purchase.route_warehouse0_buy",
}

BACKORDER_ACCEPTED = {
    0: True,
    1: False,
}


def phone_converter(*values):
    """ Try to guess landline and mobile phone numbers from a list of numbers.
    """
    phone, mobile = None, None
    values = [v.strip() for v in values if v and v.strip()]

    for value in list(values):
        numbers = ''.join(re.findall('\d+', value))
        if not mobile and len(numbers) == 10 and numbers.startswith('04'):
            mobile = value
            values.remove(value)

        elif not phone:
            phone = value
            values.remove(value)

    return phone, mobile


def date_converter(db2_entity, db2_name, default=None):
    dd = db2_entity[db2_name + 'jj']
    if not dd:
        return ''
    mm = db2_entity[db2_name + 'mm']
    Y = db2_entity[db2_name + 'ss'] * 100 + db2_entity[db2_name + 'aa']
    d = date(Y, mm, dd)
    return "{:%Y-%m-%d}".format(d)
