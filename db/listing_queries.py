from db import DatabaseCursor
from flask import current_app
import psycopg2

# This script contains all queries for the user table


def get_listing(listing_name, owner_id):
    with DatabaseCursor() as cursor:
        current_app.logger.info("Getting listing {} from owner {} from database".format(listing_name, owner_id))
        cursor.execute('select * from listing where listing_name = %s and owner_id = %s;', (listing_name, owner_id))
        return cursor.fetchone()


def get_all_listing():
    with DatabaseCursor() as cursor:
        current_app.logger.info("Getting all listing from database".format())
        cursor.execute('SELECT * FROM LISTING;')
        return cursor.fetchall()


def insert_listing(listing_name, owner_id, description, listed_date, is_available=True):
    try:
        with DatabaseCursor() as cursor:
            cursor.execute('INSERT INTO listing VALUES(%s, %s, %s, %s, %s);', (listing_name, owner_id, description,
                                                                               listed_date, is_available))
            current_app.logger.info("Listing {} added to database: [{}, {}, {}, {}]"
                                    .format(listing_name, owner_id, description, listed_date, is_available))
            return True
    except psycopg2.IntegrityError:
        current_app.logger.error("INSERTION of {} FAILED: [{}, {}, {}, {}]".format(listing_name, owner_id, description,
                                                                                   listed_date, is_available))
        return False


def update_listing(listing_name, owner_id, description):
    try:
        with DatabaseCursor() as cursor:
            cursor.execute('UPDATE listing SET description = %s  where listing_name = %s and owner_id = %s;',
                           (description, listing_name, owner_id))
            current_app.logger.info("Listing ('{}') updated.".format(listing_name))
            return True
    except (Exception, psycopg2.DatabaseError) as error:
        current_app.logger.error("Listing update failed: [{}]".format(error))
        return False


def delete_listing(listing_id):
    with DatabaseCursor() as cursor:
        current_app.logger.info("Deleting listing {} from database".format(listing_id))
        cursor.execute("delete from listing where listing_id = %s", (listing_id,))


def get_listings_under_owner(owner_id):
    with DatabaseCursor() as cursor:
        current_app.logger.info("Getting listings under user with ID {}".format(owner_id))
        cursor.execute('select * from listing where owner_id = %s', (owner_id,))
        return cursor.fetchall()


def get_listings_by_owner_name(owner_name):
    with DatabaseCursor() as cursor:
        current_app.logger.info("Getting listings under user with name {}".format(owner_name))
        cursor.execute('SELECT * FROM listing WHERE owner_id IN (SELECT id FROM users WHERE name = %s)', (owner_name,))
        return cursor.fetchall()


def get_popular_listings():
    with DatabaseCursor() as cursor:
        cursor.execute('''select l.listing_name, l.owner_id, count(*)
                          from listing l, bid b
                          where l.listing_name = b.listing_name and l.owner_id = b.owner_id and l.is_available = 'true'
                          group by l.listing_name, l.owner_id
                          order by count(*) desc
                          limit 5''')
        return cursor.fetchall()


def get_expensive_listings():
    with DatabaseCursor() as cursor:
        cursor.execute('''select l.listing_name, l.owner_id , max(price)
                          from listing l , bid b 
                          where l.listing_name = b.listing_name and l.owner_id = b.owner_id and l.is_available = 'true'
                          group by l.listing_name, l.owner_id
                          order by max(price) desc
                          limit 5''')
        return cursor.fetchall()


def get_listings_with_tags(owner_id):
    with DatabaseCursor() as cursor:
        cursor.execute('''select l.listing_name, l.owner_id, l.description, lt.tag_id, tag.name AS tag_name,
                         l.is_available, l.listed_date from listing l left join listing_tag lt on l.listing_name = lt.listing_name
                         and l.owner_id = lt.owner_id left join tag tag on lt.tag_id = tag.tag_id and l.owner_id = %s
                         group by l.listing_name, l.owner_id, lt.tag_id, tag.name
                         order by l.listing_name asc, l.owner_id asc''', (owner_id,))
        return cursor.fetchall()