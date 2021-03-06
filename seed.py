"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Movie, Rating
from model import connect_to_db, db
from server import app
from datetime import datetime



def load_users():
    """Load users from u.user into database."""

    print("Loading users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


# def get_date(date_string):
#     """ Converts a string like '05-Sept-2000' to a date obj """
#     if date_string:
#         day, month_str, year = date_string.split('-')
    
#         MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
#              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#         if month_str in MONTHS:
#             month = MONTHS.index(month_str) + 1
#             # if the string was an invalid date, should catch the
#             # ValueError exception taised by date and return None
#             return date(int(year), month, int(day))

#     return None


def load_movies():
    """Load movies from u.item into database."""

    print ("Loading Movies")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate movies
    Movie.query.delete()

    for line in open("seed_data/u.item"):
        tokens = line.rstrip().split('|')
        movie_id, title, rel_date_str, _, imdb_url = tokens[:5]
        
        title = title[:-7]
        # release_date = get_date(rel_date_str)
    
        # note: the release_date might not be present in the DB
        if rel_date_str: 
            release_date = datetime.strptime(rel_date_str, "%d-%b-%Y")
        else:
            release_date = None
            
        movie = Movie(movie_id = movie_id, 
                      title = title, 
                      released_at = release_date,
                      imdb_url = imdb_url)
        db.session.add(movie)

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print("Loading ratings")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate ratings.
    Rating.query.delete()

    for line in open("seed_data/u.data"):
        line = line.rstrip()
        user_id, movie_id, score, timestamp = line.split('\t')

        rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        score=score)
        db.session.add(rating)

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    
    max_id = result[0]

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
