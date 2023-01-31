from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from requests import get

app = Flask(__name__)

app.app_context().push()

# Initializes out database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# uses an api to get book information
def getBookInfo(title):
    GET = "https://www.googleapis.com/books/v1/volumes?q="
    URL = GET + "'" + title + "'"
    response = get(URL).json()

    books = response['items']
    item = books[0]
    book = item['volumeInfo']
    return book


# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(50))
    genre = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    publisher = db.Column(db.String(50))
    img = db.Column(db.String(500))
    count = db.Column(db.Integer)
    found = db.Column(db.Boolean)


db.create_all()

# Home directory


@app.route("/")
def home():
    library = db.session.query(Book).all()
    return render_template("home.html", library=library)

# Add a new book route, redirects to home page


@app.route("/add", methods=['POST'])
def add():
    search = request.form.get("title")

    try:
        bookInfo = getBookInfo(search)
        title = bookInfo['title']
        author = bookInfo['authors'][0]
        genre = bookInfo['categories'][0]
        description = bookInfo['description']
        publisher = bookInfo['publisher']
        img = bookInfo['imageLinks']['smallThumbnail']
        count = bookInfo['pageCount']
        found = True
    except:
        print("BOOK NOT FOUND")
        found = False

        title = "Book Not Found"
        author = ""
        genre = ""
        description = ""
        publisher = ""
        img = ""
        count = ""

    newBook = Book(title=title, author=author, genre=genre, description=description,
                   publisher=publisher, img=img, count=count, found=found)
    db.session.add(newBook)
    db.session.commit()
    return redirect(url_for("home"))

# Delete a book


@app.route("/delete/<int:book_id>")
def delete(book_id):
    bookToDelete = db.session.query(Book).filter(Book.id == book_id).first()
    db.session.delete(bookToDelete)
    db.session.commit()
    return redirect(url_for("home"))

# Goes to view page


@app.route("/view/<int:book_id>")
def view(book_id):
    book = db.session.query(Book).filter(Book.id == book_id).first()
    return render_template("view.html", book=book)


if __name__ == '__main__':
    app.run()
    
