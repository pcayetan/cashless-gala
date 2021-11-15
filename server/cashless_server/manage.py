#!/usr/bin/env python3
# -*- coding:utf-8 -*
from datetime import tzinfo
import os
import sys

import click
import logging

import pytz


@click.group()
def default_group():
    pass


@default_group.command(name="runserver", help="Run the server")
@click.option(
    "--host",
    "-h",
    default="0.0.0.0",
    type=str,
    help='Host to listen from (default "0.0.0.0")',
)
@click.option(
    "--port", "-p", default=50051, type=int, help="Port to listen from (default 50051)"
)
@click.option(
    "--reflect",
    "-r",
    default=False,
    type=bool,
    help="Enable server reflection for debug (default False)",
)
def runserver(host, port, reflect):
    from . import server

    server.serve(host, port, reflect)


@default_group.command(name="protoc", help="Generate protoc files")
def protoc():
    from subprocess import Popen

    Popen(f"{sys.executable} ./protoc.py", shell=True).wait()


@default_group.command(name="setup", help="Generate database")
@click.argument("import_file", required=False, default=None, type=click.File("r"))
def _setup(import_file):
    setup(import_file)


def setup(import_file):
    """
    Generate database and import from json file
    """
    import json
    from importlib.resources import read_text
    from datetime import datetime
    from random import randint

    from slugify import slugify
    import jsonschema

    from . import settings, get_db, get_engine, com_pb2, models

    def datetime_helper(event_date, hour, minute):
        # Does not handle midnight and after
        return (
            datetime(
                year=event_date.year,
                month=event_date.month,
                day=event_date.day,
                hour=hour,
                minute=minute,
                tzinfo=settings.TIMEZONE,
            )
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )

    def generate_code(generated_codes, name):
        code = slugify(name).upper()
        while generated_codes.get(code, ""):
            code += str(randint(0, 9))
        generated_codes[code] = code
        return code

    if os.path.exists(settings.DB_PATH):
        logging.info("--- Deleting database ---")
        os.remove(settings.DB_PATH)
    logging.info("--- Creating database ---")

    models.Model.metadata.create_all(bind=get_engine())
    db_session = get_db()
    db = db_session()

    logging.info("--- Creating payment methods ---")
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.UNKNOWN, name="inconnu"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CASH, name="espèces"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CARD, name="carte"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CHECK, name="chèque"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.AE, name="AE"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.TRANSFER, name="transfert"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.OTHER, name="autre"))

    if import_file is not None:

        # Load user json
        logging.info(f"Importing data from {import_file.name}")
        try:
            data = json.loads(import_file.read())
        except json.decoder.JSONDecodeError as e:
            logging.error(f"Error loading {import_file.name}: {e}")
            return
        import_file.close()

        # Load schema for validation from current module resources files
        schema = json.loads(read_text(__package__, "db_import_schema.json"))
        logging.info("Matching against schema")
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as e:
            logging.error(f"Your json is incorrect: {e}")
            return

        generated_codes = {}
        event_date = data.get("event_date", {})
        event_date = datetime(
            year=event_date["year"], month=event_date["month"], day=event_date["day"]
        )
        logging.info(f"--- Event date is : {event_date} ---")

        logging.info("--- Creating counters ---")
        for counter in data.get("counters", []):
            logging.info(f"Creating counter {counter}")
            db.add(models.Counter(name=counter))

        db.commit()

        logging.info("--- Creating products ---")
        for product in data.get("products", []):
            p = models.Product(
                name=product["name"].capitalize(),
                code=generate_code(generated_codes, product["name"]),
                category=".".join(
                    [cat.capitalize() for cat in product.get("category", "").split(".")]
                ),
                default_price=product["price"],
            )
            logging.info(f"Creating product {p.name}")
            db.add(p)
            db.commit()

            # Get associated counters
            for counter in (
                db.query(models.Counter)
                .filter(models.Counter.name.in_(product.get("counters", [])))
                .all()
            ):
                db.add(
                    models.ProductAvailableInCounter(
                        counter_id=counter.id, product_id=p.id
                    )
                )

            for happy_hour in product.get("happy_hours", []):
                h = models.HappyHour(
                    start=datetime_helper(
                        event_date,
                        happy_hour["start"]["hour"],
                        happy_hour["start"]["minute"],
                    ),
                    end=datetime_helper(
                        event_date,
                        happy_hour["end"]["hour"],
                        happy_hour["end"]["minute"],
                    ),
                    price=happy_hour["price"],
                    product_id=p.id,
                )
                db.add(h)
            db.commit()

    db.commit()
    db_session.remove()
    logging.info("--- Database successfully created ---")


def main():
    click.CommandCollection(sources=[default_group])()


if __name__ == "__main__":
    main()
