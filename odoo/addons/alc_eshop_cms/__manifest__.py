# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Cms",
    "description": """
        Alcyon: Eshop CMS""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "mixin_past",
        # OCA
        "fs_file",
        "fs_image",
        "jsonifier",
        # Others
        "sales_team",
        # fmt: on
    ],
    "data": [
        "data/ir_attachment.xml",
        "data/alc_eshop_cms_page_group.xml",
        "data/alc_eshop_cms_page_slot.xml",
        "data/alc_eshop_cms_page-about_us.xml",
        "data/alc_eshop_cms_page-alcyon_services.xml",
        "data/alc_eshop_cms_page-others.xml",
        "data/alc_eshop_cms_page-useful_information.xml",
        "data/alc_eshop_cms_page-useful_links.xml",
        "data/alc_eshop_cms_snippet.xml",
        "security/res_groups.xml",
        "security/alc_eshop_cms_news.xml",
        "security/alc_eshop_cms_page.xml",
        "security/alc_eshop_cms_page_group.xml",
        "security/alc_eshop_cms_page_slot.xml",
        "security/alc_eshop_cms_snippet.xml",
        "views/alc_eshop_cms_menu.xml",
        "views/alc_eshop_cms_news.xml",
        "views/alc_eshop_cms_page.xml",
        "views/alc_eshop_cms_page_group.xml",
        "views/alc_eshop_cms_page_slot.xml",
        "views/alc_eshop_cms_snippet.xml",
    ],
    "external_dependencies": {"python": ["slugify"]},
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
