#!/usr/bin/env python3
# -*- coding:utf-8 -*
import os
import sys

import click


@click.group()
def protoc_group():
    pass


@click.group()
def setup_group():
    pass


@click.group()
def random_key_group():
    pass


@setup_group.command(name="protoc", help="Generate protoc files")
def protoc():
    from subprocess import Popen

    Popen(
        "python -m grpc_tools.protoc -I%s --python_out=%s --grpc_python_out=%s %s"
        % ("../protos", "./server/", "./server/", "../protos/com.proto"),
        shell=True,
    )


@setup_group.command(name="setup", help="Generate database")
@click.option("--import", "-i", default=None, help="Import initial data from json file")
@click.option(
    "--schema",
    "-s",
    default="db_import_schema.json",
    help="Location of the schema used to validate the json of the import command",
)
def setup(**kwargs):
    import json
    from datetime import datetime
    from random import randint

    from slugify import slugify
    import jsonschema

    from server import settings, db, Model, engine, com_pb2, models

    def datetime_helper(event_date, hour, minute):
        # Does not handle midnight and after
        return datetime(
            year=event_date.year,
            month=event_date.month,
            day=event_date.day,
            hour=hour,
            minute=minute,
        )

    def generate_code(generated_codes, name):
        code = slugify(name).upper()
        while generated_codes.get(code, ""):
            code += str(randint(0, 9))
        generated_codes[code] = code
        return code

    if os.path.exists(settings.DB_PATH):
        print("--- Deleting database ---")
        os.remove(settings.DB_PATH)
    print("--- Creating database ---")

    Model.metadata.create_all(bind=engine)

    print("--- Creating payment methods ---")
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.UNKNOWN, name="inconnu"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CASH, name="espèces"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CARD, name="carte"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CHECK, name="chèque"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.AE, name="AE"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.TRANSFER, name="transfert"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.OTHER, name="autre"))

    if kwargs["import"] is not None:

        # Load user json
        print("Importing data from %s" % kwargs["import"])
        try:
            f = open(kwargs["import"], "r")
        except OSError as e:
            print("Error opening %s: %s" % (kwargs["import"], e), file=sys.stderr)
            return
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("Error loading %s: %s" % (kwargs["import"], e), file=sys.stderr)
            return
        f.close()
        print(kwargs["schema"])

        # Load schema for validation
        print("Matching against schema")
        try:
            f = open(kwargs["schema"], "r")
        except OSError as e:
            print("Error opening %s: %s" % (kwargs["import"], e), file=sys.stderr)
            return
        try:
            schema = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("Error loading %s: %s" % (kwargs["import"], e), file=sys.stderr)
            return
        f.close()
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as e:
            print("Your json is incorrect: %s" % e, file=sys.stderr)
            return

        generated_codes = {}
        event_date = data.get("event_date", {})
        event_date = datetime(
            year=event_date["year"], month=event_date["month"], day=event_date["day"]
        )
        print("--- Event date is : %s ---", event_date)

        print("--- Creating counters ---")
        for counter in data.get("counters", []):
            print("Creating counter %s" % counter)
            db.add(models.Counter(name=counter))

        db.commit()

        print("--- Creating products ---")
        for product in data.get("products", []):
            p = models.Product(
                name=product["name"].capitalize(),
                code=generate_code(generated_codes, product["name"]),
                category=".".join(
                    [cat.capitalize() for cat in product.get("category", "").split(".")]
                ),
                default_price=product["price"],
            )
            print("Creating product %s" % p.name)
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
    print("--- Database successfully created ---")


if __name__ == "__main__":
    click.CommandCollection(sources=[setup_group, random_key_group])()
