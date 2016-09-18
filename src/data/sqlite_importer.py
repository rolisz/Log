# -*- coding: utf-8 -*-
import os
import click
import logging
from dotenv import find_dotenv, load_dotenv
import logging
import parsers
import collections
import itertools
import json
from datetime import datetime
import mappings
import sqlite3


def lines(messages):
    for contact in messages:
        gender = mappings.genders.get(contact, 'n')
        friendship = 2016 - mappings.met.get(contact, mappings.avg_age)
        age_group = mappings.age_buckets.get(contact, -1)
        for line in messages[contact]:
            yield  (contact, line['contact'],line['timestamp'], line['source'],
                    line['protocol'],line['nick'],line['message'], gender,
                    friendship, age_group)

def grouper(n, iterable):
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk


@click.command()
@click.option('--facebook_path', type=click.Path(exists=True))
@click.option('--trillian_path', type=click.Path(exists=True))
@click.option('--digsby_path', type=click.Path(exists=True))
@click.option('--pidgin_path', type=click.Path(exists=True))
@click.option('--whatsapp_path', type=click.Path(exists=True))
@click.option('--sqlite_table', default='messages')
@click.option('--drop_table/--nodrop_table', default=False)
@click.argument('sqlite_path', type=click.Path())
def main(facebook_path, trillian_path, digsby_path, pidgin_path, whatsapp_path,
         sqlite_table, drop_table, sqlite_path):
    logger = logging.getLogger(__name__)
    logger.info('parsing logs')
    messages = collections.defaultdict(list)
    if digsby_path:
        for contact, text in parsers.Digsby(digsby_path):
            messages[contact].append(text)
        logger.info("Digsby parsing done")
    if trillian_path:
        for contact, text in parsers.Trillian(trillian_path):
            messages[contact].append(text)
        logger.info("Trillian parsing done")
    if pidgin_path:
        for contact, text in parsers.Pidgin(pidgin_path):
            messages[contact].append(text)
        logger.info("Pidgin parsing done")
    if whatsapp_path:
        for contact, text in parsers.Whatsapp(whatsapp_path):
            messages[contact].append(text)
        logger.info("Whatsapp parsing done")
    if facebook_path:
        for contact, text in parsers.Facebook(facebook_path):
            messages[contact].append(text)
        logger.info("Facebook parsing done")

    for contact in messages:
        messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
        messages[contact].sort(key=lambda x: x['timestamp'])
    logger.info("Message joining and sorting done")

    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()

    if drop_table:
        c.execute('DROP TABLE IF EXISTS '+sqlite_table)
    c.execute('CREATE TABLE IF NOT EXISTS %s (contact TEXT, sender TEXT, datetime TEXT,'
            'source TEXT, protocol TEXT, nick TEXT, message TEXT, friendship INT,'
            'gender TEXT, age_group INT)' % sqlite_table)

    for gr in grouper(5000, lines(messages)):
        conn.executemany("INSERT INTO %s (contact, sender, datetime, source,"
                    "protocol, nick, message, gender, friendship, age_group) values"
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % sqlite_table, gr)
        logger.info("Inserted 5000 messages.")
    conn.commit()
    conn.close()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()

