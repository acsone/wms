import csv
import os

FILE_NAME_IN = 'FOURNISSEUR_UTILISATEUR.csv'
FILE_NAME_OUT = '../install/supplier_add_data.csv'
DELIMITER = ','
QUOTECHAR = '"'
BACKUP_RESPONSIBLE = '__setup__.res_user_fmichiels'

ODOO_FIELD_PURCHASE_MANAGER = 'purchase_manager_id'

# Mapping
DAYS_MAPPING = {
    'Revision Lundi': 'is_manage_day_1',
    'Revision Mardi': 'is_manage_day_2',
    'Revision Mercredi': 'is_manage_day_3',
    'Revision Jeudi': 'is_manage_day_4',
    'Revision Vendredi': 'is_manage_day_5',
}
USERS_MAPPING = {
    'HEINEVI': '__setup__.res_user_vheine',
    'CHRISTOPHE': '__setup__.res_user_cpetry',
}


class Converter:
    def process(self):
        if not os.path.isfile(FILE_NAME_IN):
            raise Exception("The file %s doesn't exist" % FILE_NAME_IN)

        suppliers_values = {}
        with open(FILE_NAME_IN, 'rb') as csvfile:
            lines = csv.reader(
                csvfile, delimiter=DELIMITER, quotechar=QUOTECHAR
            )

            if not lines:
                raise Exception("The file is empty")
            first_line = lines.next()

            ref_index = first_line.index('D_No Fournisseur')
            manager_index = first_line.index('UTILISATEUR')
            for key, field_day in DAYS_MAPPING.iteritems():
                index = first_line.index(key)
                setattr(self, field_day, index)

            for line in lines:
                supplier_days = suppliers_values.get(line[ref_index], {})

                purchase_manager = line[manager_index]
                if purchase_manager in USERS_MAPPING.keys():
                    supplier_days[ODOO_FIELD_PURCHASE_MANAGER] = USERS_MAPPING[
                        purchase_manager
                    ]
                else:
                    supplier_days[
                        ODOO_FIELD_PURCHASE_MANAGER
                    ] = BACKUP_RESPONSIBLE

                for field_day in DAYS_MAPPING.values():
                    day_value = line[getattr(self, field_day)]
                    if day_value:
                        supplier_days[field_day] = True
                    # Do not overwrite existing value
                    elif not supplier_days.get(field_day):
                        supplier_days[field_day] = False

                suppliers_values[line[ref_index]] = supplier_days

        csv_first_line = ['id', ODOO_FIELD_PURCHASE_MANAGER + '/id']
        for field_day in DAYS_MAPPING.values():
            csv_first_line.append(field_day)
        csv_values = [csv_first_line]

        for supplier_ref, supplier_values in suppliers_values.iteritems():
            csv_line = [
                '__import__.supplier_%s' % supplier_ref,
                supplier_values[ODOO_FIELD_PURCHASE_MANAGER],
            ]
            for field_day in DAYS_MAPPING.values():
                csv_line.append(supplier_values[field_day])
            csv_values.append(csv_line)

        with open(FILE_NAME_OUT, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"')
            csvwriter.writerows(csv_values)


if __name__ == "__main__":
    importer = Converter()
    importer.process()
