# -*- coding: utf-8 -*-
import os
import click
import logging
from dotenv import find_dotenv, load_dotenv
import collections
import itertools
import sqlite3
from src.data import mappings
from src.data.mappings import canonicalize
from src.data import parsers

def lines(messages, self_name):
    for contacts in messages:
        cleaned_contacts = set()
        for contact in contacts:
            contact = canonicalize(contact)
            if contact != self_name:
                cleaned_contacts.add(contact)
        if len(cleaned_contacts) == 1:
            c = next(iter(cleaned_contacts))
            gender = mappings.genders.get(c, 'u')
            friendship = 2016 - mappings.met.get(c, mappings.avg_age)
            age_group = mappings.age_buckets.get(c, -1)
        else:
            gender = 'n/a'
            friendship = -1
            age_group = -2
        thread_name = ",".join(cleaned_contacts)
        for line in messages[contacts]:
            yield  (thread_name, canonicalize(line['contact']), line['timestamp'],
                    line['source'], line['protocol'], line['nick'],
                    line['message'], gender, friendship, age_group)

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
@click.option('--hangouts_path', type=click.Path(exists=True))
@click.option('--viber_path', type=click.Path(exists=True))
@click.option('--sqlite_table', default='messages')
@click.option('--drop_table/--nodrop_table', default=False)
@click.option('--clean_table/--noclean_table', default=True)
@click.option('--self_name', default='',
              help="The canonical name for you, to filter out from contact lists")
@click.argument('sqlite_path', type=click.Path())
def main(facebook_path, trillian_path, digsby_path, pidgin_path, whatsapp_path,
         hangouts_path, viber_path, sqlite_table, drop_table, clean_table,
         self_name, sqlite_path):
    logger = logging.getLogger(__name__)
    logger.info('parsing logs')
    messages = collections.defaultdict(list)

    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()

    if drop_table:
        c.execute('DROP TABLE IF EXISTS '+sqlite_table)
    c.execute('CREATE TABLE IF NOT EXISTS %s (contact TEXT, sender TEXT, datetime TEXT,'
            'source TEXT, protocol TEXT, nick TEXT, message TEXT, friendship INT,'
            'gender TEXT, age_group INT)' % sqlite_table)

    if digsby_path:
        for contact, text in parsers.Digsby(digsby_path):
            messages[frozenset(contact)].append(text)
        logger.info("Digsby parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Digsby"))
            logger.info("Digsby cleaning done")
    if trillian_path:
        for contact, text in parsers.Trillian(trillian_path):
            messages[frozenset(contact)].append(text)
        logger.info("Trillian parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Trillian"))
            logger.info("Trillian cleaning done")
    if pidgin_path:
        for contact, text in parsers.Pidgin(pidgin_path):
            messages[frozenset(contact)].append(text)
        logger.info("Pidgin parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Pidgin"))
            logger.info("Pidgin cleaning done")
    if whatsapp_path:
        for contact, text in parsers.Whatsapp(whatsapp_path):
            messages[frozenset(contact)].append(text)
        logger.info("Whatsapp parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Whatsapp"))
            logger.info("Whatsapp cleaning done")
    if facebook_path:
        for contact, text in parsers.Facebook(facebook_path):
            messages[frozenset(contact)].append(text)
        logger.info("Facebook parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Facebook"))
            logger.info("Facebook cleaning done")
    if hangouts_path:
        for contact, text in parsers.Hangouts(hangouts_path):
            messages[frozenset(contact)].append(text)
        logger.info("Hangouts parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Hangouts"))
            logger.info("Hangouts cleaning done")

    if viber_path:
        for contact, text in parsers.Viber(viber_path):
            messages[frozenset(contact)].append(text)
        logger.info("Viber parsing done")
        if clean_table:
            c.execute("DELETE FROM %s WHERE source = '%s'" % (sqlite_table, "Viber"))
            logger.info("Viber cleaning done")

    for contact in messages:
        messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
        messages[contact].sort(key=lambda x: x['timestamp'])
        print(len(messages[contact]))
    logger.info("Message joining and sorting done.")

    for gr in grouper(5000, lines(messages, self_name)):
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

