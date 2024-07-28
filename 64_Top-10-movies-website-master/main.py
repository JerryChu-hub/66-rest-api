from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class RatingForm(FlaskForm):
    rating = StringField('Your Rating Out of 10', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    ranking = StringField('Your Ranking Out of 10', validators=[DataRequired()])
    submit = SubmitField('OK')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('OK')


# CREATE DB
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)




# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[str] = mapped_column(String, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f'<movie {self.title}>'
    
with app.app_context():
    db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.add(second_movie)
#     db.session.commit()

@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.ranking))
    movies = result.scalars()
    return render_template("index.html", all_movies = movies)

@app.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit(id):
    edit_form = RatingForm()
    if request.method == 'POST':
        movie_to_update = db.get_or_404(Movie, id)
        if edit_form.rating.data != '':
            movie_to_update.rating = edit_form.rating.data
        if edit_form.ranking.data != '':
            movie_to_update.ranking = edit_form.ranking.data
        if edit_form.review.data != '':
            movie_to_update.review = edit_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    movie_selected = db.get_or_404(Movie, id)
    return render_template('edit.html', movie = movie_selected, form = edit_form)

@app.route('/delete/<int:id>')
def delete(id):
    movie_to_delete = db.get_or_404(Movie, id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods = ['GET', 'POST'])
def add():
    add_form = AddForm()
    if request.method == 'POST':
        
        url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkYTgxNzJiZDQyMWViYWQzYWE1ZThmZGRjN2ZhODQzMyIsIm5iZiI6MTcyMDU0MDE4NS4yMDE5NjMsInN1YiI6IjY2OGQ1YTk5MDQxZTk1NjNlMTc0YTY0NCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.1SyYJUAyxg6VaMqQgr8O-rUoSKLFtR2AdRdZp7byCfg"
        }

        params = {
            "api_key": 'da8172bd421ebad3aa5e8fddc7fa8433',
            "query": add_form.title.data
        }

        response = requests.get(url, headers=headers, params=params)

        all_result = response.json()['results']
        return render_template('select.html', results = all_result)

    return render_template('add.html', form = add_form)

@app.route('/addmovie/<int:id>')
def select(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkYTgxNzJiZDQyMWViYWQzYWE1ZThmZGRjN2ZhODQzMyIsIm5iZiI6MTcyMDU0MDE4NS4yMDE5NjMsInN1YiI6IjY2OGQ1YTk5MDQxZTk1NjNlMTc0YTY0NCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.1SyYJUAyxg6VaMqQgr8O-rUoSKLFtR2AdRdZp7byCfg"
    }

    parameters = {
        'api_key': 'da8172bd421ebad3aa5e8fddc7fa8433',
    }

    response = requests.get(url, headers=headers, params=parameters).json()

    new_movie = Movie(
        title=response['original_title'],
        year=response["release_date"].split("-")[0],
        description=response["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500{response['poster_path']}"
    )

    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
