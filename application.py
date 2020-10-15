import os
from flask import Flask, session, render_template, request, redirect,flash,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import sys
from passlib.hash import sha256_crypt
app = Flask(__name__)
app.debug=True
# Check for environment variable

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    #login
    if request.method=='POST':
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        data_id= db.execute("SELECT id,password FROM users WHERE username = :username ", {"username": username}).fetchone()
        #no user
        if data_id is None : 
            flash("No user with such username/password")
            return render_template("login.html")
        #pssword check
        if not sha256_crypt.verify(password, data_id['password']):
            flash("Incorrect password")
            return render_template("login.html")
        #store session
        session["user_id"]=data_id[0]
        session["user_name"]=username
       
        return redirect(url_for('welcome'))
    else:
        return render_template("login.html")

  #logout     
@app.route("/logout",methods=['GET'])
def logout():
    if "user_name" in session:
       session.clear()
       flash("You have been logged out")
       return redirect(url_for('login'))
    else:
       flash("You arent logged in")
       return redirect(url_for('login'))




@app.route("/register", methods=['GET', 'POST'])
def register():

   
     # Get form information.
    if request.method=='POST': 
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
    # check if no data
        if  request.form.get("username") is None:
            flash("Username Field is required")
            return render_template("register.html")

        if  request.form.get("password") is None:
            flash("Password Field is required")
            return render_template("register.html") 

        if(password != confirm_password):
            flash("Password's dont match")
            return render_template("register.html")

        # Make sure username doesent exists.
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
            flash("This username already exists")
            return render_template("register.html")


        #encrypt
        password =sha256_crypt.hash(password)

        db.execute("INSERT INTO users(username, password) VALUES (:username, :password)",
                {"username": username, "password": password})
        db.commit()

        data=db.execute("SELECT id FROM users WHERE username = :username AND password = :password", {"username": username,"password": password}).fetchone()

        session["user_id"]=data[0]
        session["user_name"]=username
        

        return redirect(url_for('login'))
    else:
        return render_template("register.html")



#welcome page after login
@app.route("/welcome",methods=['GET','POST'])
def welcome():
    #check if logged in
    if "user_name" in session:
        user_name=session["user_name"]
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))    

    
    if request.method=="POST":
        results=request.form.get("query")
        results.title()
        print(results, file=sys.stderr)
        
        if results is None:
            return render_template("welcome.html",user= user_name,message="search cant be empty")
        # is there a book 
        books = db.execute("SELECT isbn, title, author, year FROM books WHERE (title ILIKE :results) OR (author ILIKE :results) OR (isbn ILIKE :results)",{"results" : '%' + results + '%'})

        if books.rowcount==0:
            flash("No books that match this search")
            return render_template("welcome.html",user= user_name)
            
        return render_template("welcome.html",user= user_name,found=True,books=books)     
    else:
        return render_template("welcome.html",user= user_name,found=False,books="")   





@app.route("/welcome/<string:book_isbn>",methods=['GET', 'POST'])
def book(book_isbn):
    #logged in ?

    if "user_name" in session:
        user_name=session["user_name"]
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))    


    # fetch books with given isbn
    book=db.execute("SELECT * FROM books WHERE isbn = :isbn" , {"isbn":book_isbn}).fetchone()
    if book is None:
        flash("We dont have a book with this isbn")
        return redirect(url_for('welcome'))

    #goodreads
    key = os.getenv("GOODREADS_KEY")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": book_isbn})
    res=res.json()
    review_count=res['books'][0]['work_ratings_count']   
    review_average=res['books'][0]['average_rating'] 
    #fetch reviews
    reviews=db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn":book_isbn}).fetchall() 
    if request.method=="GET":
        return render_template("book.html",reviews=reviews,book=book,review_count=review_count,review_average=review_average)
    else:
        review_text=request.form.get("text")
        rating = request.form.get("rating")
        # if empty value
        if review_text is None :
            flash("Sorry , we didnt get any text")
            return render_template("book.html",reviews=reviews,book=book,review_count=review_count,review_average=review_average)
        if rating is None :
            flash("Sorry , we didnt get any rating")
            return render_template("book.html",reviews=reviews,book=book,review_count=review_count,review_average=review_average)  

      

        # user exists?
        user_name=session["user_name"]
        exists=db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username":user_name,"isbn":book_isbn}).fetchone()

        if exists is not None:
            flash("You have already submitted a review about this book")
            return render_template("book.html",reviews=reviews,book=book,review_count=review_count,review_average=review_average) 

        rating=int(rating)
        db.execute("INSERT INTO reviews(isbn,rating,review_text,username) VALUES (:isbn, :rating, :review_text,:username)",
                {"isbn":book_isbn,"rating": rating, "review_text":review_text,"username":user_name})

        db.commit()
        reviews=db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn":book_isbn}).fetchall()
        flash("Review Submitted")
        return render_template("book.html",reviews=reviews,book=book,review_count=review_count,review_average=review_average)


@app.route("/api/<string:isbn>")
def api(isbn):
    results=db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    if results is None:
        return jsonify({"error": "Invalid isbn"}), 404

    avg=db.execute("SELECT AVG(rating) as rating,COUNT(rating) as coun FROM reviews WHERE isbn = :isbn",{"isbn":isbn})
    tmp=avg.fetchone()
    res=dict(tmp.items())
    res['rating']=float('%.2f'%(res['rating']))

    return jsonify({
              "title": results['title'],
              "author": results['author'],
              "year": results['year'],
              "isbn": results['isbn'],
              "review_count":res['coun'],
              "average_score": res['rating']
          })












