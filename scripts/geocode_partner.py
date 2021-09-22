#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import logging
import time
from contextlib import contextmanager

import click
import click_odoo
import requests
import unicodecsv as csv

from odoo import _, exceptions, fields

_logger = logging.getLogger("Geocode partner")


def batch(iterable, size=100):
    _len = len(iterable)
    for ndx in range(0, _len, size):
        yield iterable[ndx : min(ndx + size, _len)]


class PartnerGeocoder(object):
    def __init__(self, env, osmurl, csvfile):
        self.env = env
        self.osmurl = osmurl
        self.csvfile = csvfile
        self.error_msgs = []
        self.next_call_osm = datetime.datetime.now()
        self.bpost_customers_batch_validate = []

    def run(self):
        self.error_msgs = []
        all_customers = (
            self.env["res.partner"]
            .browse([r.id for r in self._iter_partner()])
            .with_context(lang="fr_BE")
        )
        coordinates_by_customer = {}
        _logger.info("%d customers to geolocalize", len(all_customers))
        for customer in all_customers:
            r = self._geocode_partner(customer)
            if r and r["place_rank"] == 30:
                coordinates_by_customer[customer] = {"lat": r["lat"], "lon": r["lon"]}
            else:
                if customer.country_id.name == "Belgique":
                    self.bpost_customers_batch_validate.append(customer)
        _logger.info("%d customers geolocalized by osm", len(coordinates_by_customer))
        coordinates_by_customer.update(self._geocode_partners_bpost())
        _logger.info(
            "%d customers geolocalized by osm and bbost", len(coordinates_by_customer)
        )

        reader = csv.DictReader(self.csvfile, delimiter=";")
        id_by_ref = {c.ref: c.id for c in all_customers}
        for row in reader:
            ref = row["ref"]
            cid = id_by_ref[ref]
            customer = self.env["res.partner"].browse(cid)
            if customer not in coordinates_by_customer:
                coordinates_by_customer[customer] = {
                    "lat": row["lat"],
                    "lon": row["lon"],
                }
        _logger.info("%d customers geolocalized", len(coordinates_by_customer))
        self._update_partners_coordinate(coordinates_by_customer)

    def _geocode_partners_bpost(self):
        coordinates_by_customer = {}
        for customers in batch(self.bpost_customers_batch_validate):
            address_to_validate = []
            rqst = {
                "ValidateAddressesRequest": {
                    "AddressToValidateList": {"AddressToValidate": address_to_validate},
                    "ValidateAddressOptions": {
                        "IncludeNumberOfSuffixes": True,
                        "IncludeDefaultGeoLocation": True,
                    },
                    "CallerIdentification": {"CallerName": "Alcyon Benelux"},
                }
            }
            for customer in customers:
                address_to_validate.append(
                    {
                        "@id": customer.id,
                        "AddressBlockLines": {
                            "UnstructuredAddressLine": [
                                customer.street,
                                customer.street2 or "",
                                u"{} {}".format(
                                    customer.zip or "", customer.city or ""
                                ),
                            ]
                        },
                        "DeliveringCountryISOCode": "BE",
                        "DispatchingCountryISOCode": "BE",
                    }
                )

            result = requests.post(
                "https://webservices-pub.bpost.be/ws/ExternalMailingAddressProofingCSREST_v1/address/validateAddresses",
                json=rqst,
            )
            result.raise_for_status()
            json_result = result.json()
            for validate_address_result in json_result["ValidateAddressesResponse"][
                "ValidatedAddressResultList"
            ]["ValidatedAddressResult"]:
                if "Error" in validate_address_result:
                    continue
                address_list = validate_address_result.get(
                    "ValidatedAddressList", {}
                ).get("ValidatedAddress", [])
                if not address_list:
                    continue
                validated_address = address_list[0]
                partner_id = int(validate_address_result["@id"])
                geo_loc_info = (
                    validated_address.get("ServicePointDetail", {})
                    .get("GeographicalLocationInfo", {})
                    .get("GeographicalLocation")
                )
                if not geo_loc_info:
                    continue
                coordinates_by_customer[self.env["res.partner"].browse(partner_id)] = {
                    "lat": geo_loc_info["Latitude"]["Value"],
                    "lon": geo_loc_info["Longitude"]["Value"],
                }
        return coordinates_by_customer

    def _update_partners_coordinate(self, coordinates_by_partner):
        with open("coordinatet.csv", "wb") as out_csvfile:
            writer = csv.DictWriter(out_csvfile, fieldnames=["id", "lat", "lon"])
            writer.writeheader()
            for partner, coordinates in coordinates_by_partner.items():
                writer.writerow(
                    {
                        "id": partner.id,
                        "lat": coordinates["lat"],
                        "lon": coordinates["lon"],
                    }
                )
        for partner, coordinates in coordinates_by_partner.items():
            partner.write(
                {
                    "partner_latitude": coordinates["lat"],
                    "partner_longitude": coordinates["lon"],
                    "date_localization": fields.Date.context_today(partner),
                }
            )

    @contextmanager
    def _with_osm_serialize(self):
        now = datetime.datetime.now()
        if self.next_call_osm < now:
            yield
        else:
            time.sleep((self.next_call_osm - now).total_seconds())
            yield
        self.next_call_osm = datetime.datetime.now() + datetime.timedelta(seconds=1)

    def _iter_partner(self):
        # get partner with a SO into the last 6 months
        self.env.cr.execute(
            "select distinct partner_shipping_id from sale_order so join res_partner rp on rp.id = partner_shipping_id where rp.is_b2c_customer=false and so.create_date > CURRENT_DATE - INTERVAL '6 months' "
        )
        current_customer_ids = {r[0] for r in self.env.cr.fetchall()}
        _logger.info("%d partner to process", len(current_customer_ids))
        for partner in (
            self.env["res.partner"]
            .search([("is_b2c_customer", "=", False), ("customer", "=", True)])
            .with_context(lang="fr_BE")
            .filtered(lambda p, customer_ids=current_customer_ids: p.id in customer_ids)
        ):
            if partner.id not in current_customer_ids:
                continue
            if partner.not_in_dynamic_delivery_round and partner.round_itinerary_ids:
                yield partner
            if not partner.not_in_dynamic_delivery_round:
                yield partner

    def _geocode_partner(self, customer):
        # Fisrt try with OSM (local server)
        result = self._geocode_address_osm(
            customer.street,
            customer.zip,
            customer.city,
            customer.state_id.name,
            customer.country_id.name,
        )
        return result

    def _geocode_address_loc(
        self, street=None, zip_code=None, city=None, state=None, country=None
    ):
        """Get the latitude and longitude by requesting Openstreetmap"
        """
        pay_load = {
            "street": street or "",
            "postcode": zip_code or "",
            "city": city or "",
            "country": country or "",
        }

        request_result = requests.post("http://localhost:5001/search/", params=pay_load)
        try:
            request_result.raise_for_status()
        except Exception as e:
            _logger.exception("Geocoding error")
            raise exceptions.Warning(_("Geocoding error. \n %s") % e.message)
        values = request_result.json()
        v = {}
        match = values.get("match")
        if match:
            v = match[0]
            for vl in match[1:]:
                if vl["place_rank"] > v["place_rank"]:
                    v = vl
        return v

    def _geocode_address_osm(
        self,
        street=None,
        zip_code=None,
        city=None,
        state=None,
        country=None,
        force_osm=False,
    ):
        """Get the latitude and longitude by requesting Openstreetmap"
        """
        pay_load = {
            "limit": 1,
            "format": "jsonv2",
            "street": street or "",
            "postalCode": zip_code or "",
            "city": city or "",
            "state": state or "",
            "country": country or "",
        }

        osmurl = self.osmurl
        if force_osm or (country and country != u"Belgique"):
            osmurl = "https://nominatim.openstreetmap.org/search"
        request_result = requests.get(osmurl, params=pay_load)
        try:
            request_result.raise_for_status()
        except Exception as e:
            _logger.exception("Geocoding error")
            raise exceptions.Warning(_("Geocoding error. \n %s") % e.message)
        values = request_result.json()
        values = values[0] if values else {}
        return values


@click.command()
@click.option("csvfile", "--csv-file", type=click.File(mode="rb"), required=True)
@click.option(
    "osmurl",
    "--osm-url",
    type=click.types.STRING,
    default="https://nominatim.openstreetmap.org/search",
)
@click_odoo.env_options(default_log_level="info")
def main(env, osmurl, csvfile):
    click.echo("Start processing file. . .")
    builder = PartnerGeocoder(env, osmurl, csvfile)
    builder.run()
    env.cr.commit()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
