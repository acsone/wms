# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

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
    16: 'specific_data.product_categ_ketamine',
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
    62: 'specific_data.product_categ_psychotropes_38',
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
    15: 'specific_partner.partner_category_pharmacy',
    16: 'specific_partner.partner_category_pharmacy',
    17: 'specific_partner.partner_category_pharmacy',
    18: 'specific_partner.partner_category_pharmacy',
    19: 'specific_partner.partner_category_pharmacy',
    20: 'specific_partner.partner_category_student',
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

CLIENT_PAYMENT_TERMS = {
    1: '__setup__.account_payment_term_01',
    2: '__setup__.account_payment_term_02',
    3: '__setup__.account_payment_term_03',
    4: '__setup__.account_payment_term_04',
    5: '__setup__.account_payment_term_05',
    6: '__setup__.account_payment_term_06',
    7: '__setup__.account_payment_term_07',
    8: '__setup__.account_payment_term_08',
    10: '__setup__.account_payment_term_10',
    11: '__setup__.account_payment_term_01',
    12: '__setup__.account_payment_term_02',
    17: '__setup__.account_payment_term_23',
    19: '__setup__.account_payment_term_19',
    23: '__setup__.account_payment_term_23',
    32: '__setup__.account_payment_term_32',
    33: '__setup__.account_payment_term_33',
}

CLIENT_PAYMENT_MODES = {
    # FIXME
    # account_payment_mode_1 does not exist
    #11: '__setup__.account_payment_mode_1',
    #12: '__setup__.account_payment_mode_1',
    #17: '__setup__.account_payment_mode_1',
    #32: '__setup__.account_payment_mode_1',
    'not_empty': False,
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
