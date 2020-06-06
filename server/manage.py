#!/usr/bin/env python3
# -*- coding:utf-8 -*
import os

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
def setup(**kwargs):
    from server import settings, db, Model, engine, com_pb2, models

    if os.path.exists(settings.DB_PATH):
        print("Deleting database")
        os.remove(settings.DB_PATH)
    print("Creating database")

    Model.metadata.create_all(bind=engine)

    print("Creating payment methods")
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.UNKNOWN, name="inconnu"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CASH, name="espèces"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CARD, name="carte"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.CHECK, name="chèque"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.AE, name="AE"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.TRANSFER, name="transfert"))
    db.add(models.PaymentMethod(id=com_pb2.PaymentMethod.OTHER, name="autre"))

    if kwargs["import"] is not None:
        print("TODO: import data from %s" % kwargs["import"])

    db.commit()
    print("Database successfully created")


if __name__ == "__main__":
    click.CommandCollection(sources=[setup_group, random_key_group])()
