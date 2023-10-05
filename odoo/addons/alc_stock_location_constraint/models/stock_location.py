# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):
    def init(self):
        res = super().init()
        cr = self.env.cr
        cr.execute(
            """
            CREATE OR REPLACE FUNCTION alc_unique_location_coordinates_check()
            RETURNS TRIGGER AS $$
            DECLARE
                enable_check BOOLEAN;
                duplicate_name VARCHAR;
                duplicate_id INTEGER;
            BEGIN
                SELECT EXISTS (
                    SELECT
                        1
                    FROM
                        ir_config_parameter
                    WHERE
                        key = 'alc_stock_location_constraint.stock_location_constraint'
                        AND UPPER(value) in ('TRUE', '1')
                )
                INTO enable_check;
                IF enable_check THEN
                    IF EXISTS (
                        SELECT
                            1
                        FROM
                            stock_location
                        WHERE
                            (zone_location_id IS NOT NULL
                            AND zone_location_id IS NOT DISTINCT FROM NEW.zone_location_id)
                            AND (area_location_id IS NOT NULL AND area_location_id IS NOT DISTINCT FROM NEW.area_location_id)
                            AND (corridor IS NOT NULL AND corridor IS NOT DISTINCT FROM NEW.corridor)
                            AND (rack IS NOT NULL AND rack IS NOT DISTINCT FROM NEW.rack)
                            AND (level IS NOT NULL AND level IS NOT DISTINCT FROM NEW.level)
                            AND ((posx IS NOT NULL OR posy <> 0) AND posx IS NOT DISTINCT FROM NEW.posx)
                            AND ((posy IS NOT NULL OR posy <> 0) AND posy IS NOT DISTINCT FROM NEW.posy)
                            AND ((posz IS NOT NULL OR posz <> 0) AND posz IS NOT DISTINCT FROM NEW.posz)
                            AND id IS DISTINCT FROM NEW.id
                        LIMIT 1
                    )
                    THEN
                        SELECT name, id INTO duplicate_name, duplicate_id
                        FROM stock_location
                        WHERE
                            (zone_location_id IS NOT NULL
                            AND zone_location_id IS NOT DISTINCT FROM NEW.zone_location_id)
                            AND (area_location_id IS NOT NULL AND area_location_id IS NOT DISTINCT FROM NEW.area_location_id)
                            AND (corridor IS NOT NULL AND corridor IS NOT DISTINCT FROM NEW.corridor)
                            AND (rack IS NOT NULL AND rack IS NOT DISTINCT FROM NEW.rack)
                            AND (level IS NOT NULL AND level IS NOT DISTINCT FROM NEW.level)
                            AND ((posx IS NOT NULL OR posy <> 0) AND posx IS NOT DISTINCT FROM NEW.posx)
                            AND ((posy IS NOT NULL OR posy <> 0) AND posy IS NOT DISTINCT FROM NEW.posy)
                            AND ((posz IS NOT NULL OR posz <> 0) AND posz IS NOT DISTINCT FROM NEW.posz)
                            AND id IS DISTINCT FROM NEW.id
                        LIMIT 1;
                        RAISE EXCEPTION USING ERRCODE = 'unique_violation',
                            MESSAGE = 'Duplicate entry for location coordinates: ' ||
                                NEW.name || ' (id: ' || NEW.id || ') and ' ||
                                duplicate_name || ' (id: ' || duplicate_id || ')' ||
                                ' Coordinates: ' ||
                                COALESCE(NEW.zone_location_id, 0)  || '/' ||
                                COALESCE(NEW.area_location_id, 0) || '/' ||
                                COALESCE(NEW.corridor, '') || '/' ||
                                COALESCE(NEW.rack, '') || '/' ||
                                COALESCE(NEW.level, '') || '/' ||
                                COALESCE(NEW.posx, 0) || '/' ||
                                COALESCE(NEW.posy, 0) || '/' ||
                                COALESCE(NEW.posz, 0);
                   END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

             -- Create the trigger on stock_location
            DROP TRIGGER IF EXISTS alc_unique_location_coordinates_trigger ON stock_location;
            CREATE TRIGGER alc_unique_location_coordinates_trigger
            BEFORE INSERT OR UPDATE ON stock_location
            FOR EACH ROW
            EXECUTE FUNCTION alc_unique_location_coordinates_check();
            """
        )
        return res
