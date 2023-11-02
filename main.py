from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = '273e34bfdd0c7164d3bf3664291934ee'
API_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyNzNlMzRiZmRkMGM3MTY0ZDNiZjM2NjQyOTE5MzRlZSIs' \
          'InN1YiI6IjY1NDEzYzg1ZWVjNWI1MDEzYjIxYjRmMyIsInNjb3BlcyI6WyJhcG' \
          'lfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.-c6Wdt-CzbBWgkXTvdqPwvHVO2HhbXzTSpFfZfccf4g'
URL = 'https://api.themoviedb.org/3/search/movie'
headers = {
    "accept": "application/json",
    "Authorization": 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyNzNlMzRiZmRkMGM3MTY0ZDNiZjM2NjQyOTE5MzRlZSIsInN1YiI6IjY1NDEzYzg1ZWVjNWI1MDEzYjIxYjRmMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.-c6Wdt-CzbBWgkXTvdqPwvHVO2HhbXzTSpFfZfccf4g'
}
URL_FOR_DATA = 'https://api.themoviedb.org/3/movie/'

URL_FOR_PICTURES = 'https://image.tmdb.org/t/p/w500'
'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
Bootstrap5(app)

db.init_app(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.String(250), nullable=False)
    ranking = db.Column(db.String(250), nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# with app.app_context():
#     db.create_all()

# with app.app_context():
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth,"
#                     " pinned down by an extortionist's sniper rifle."
#                     " Unable to leave or receive outside help,"
#                     " Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")
#     db.session.add(new_movie)
#     db.session.commit()


@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    ranks = len(movies)
    for movie in movies:
        movie.ranking = ranks
        ranks = ranks - 1
    return render_template("index.html", movies=movies)


class RateMovieForm(FlaskForm):
    rate = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')


class AddingForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route('/edit', methods=['GET', 'POST'])
def editing():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    print(movie_id)
    movie_to_update = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie_to_update.review = form.review.data
        movie_to_update.rating = float(form.rate.data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def adding():
    form = AddingForm()
    if form.validate_on_submit():
        title_movie = form.title.data
        response = requests.get(f"{URL}?query={title_movie}", headers=headers)
        print(response.status_code)
        print(response.json()['results'][0])
        movies_to_choose = response.json()['results']
        return render_template('select.html', movies=movies_to_choose)
    return render_template('add.html', form=form)


params = {
    'language': 'en-US'
}


@app.route('/selecting', methods=['GET', 'POST'])
def selection():
    movie_id = request.args.get('choose')
    response = requests.get(f"{URL_FOR_DATA}{movie_id}", headers=headers, params=params)
    result = response.json()
    database_movie = Movie(
        title=result['title'],
        year=result['release_date'].split('-')[0],
        description=result['overview'],
        rating="None",
        ranking="None",
        review="None",
        img_url=f"{URL_FOR_PICTURES}{result['poster_path']}"
    )
    db.session.add(database_movie)
    db.session.commit()
    return redirect(url_for('editing', id=database_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
