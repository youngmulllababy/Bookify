import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY,isbn VARCHAR NOT NULL,title VARCHAR NOT NULL, author VARCHAR NOT NULL,year INTEGER NOT NULL)")
    db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR NOT NULL,password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews(id SERIAL PRIMARY KEY,isbn VARCHAR NOT NULL,rating INTEGER NOT NULL,review_text VARCHAR NOT NULL,username VARCHAR NOT NULL)")
    file=open("books.csv")
    books=csv.reader(file)
    next(books)
    for isbn,title,author,year in books :
        db.execute("INSERT INTO books (isbn, title, author,year) VALUES (:isbn, :title, :author,:year)",
                    {"isbn": isbn, "title": title, "author": author,"year":year})
    db.commit()


if __name__ == "__main__":
    main()
