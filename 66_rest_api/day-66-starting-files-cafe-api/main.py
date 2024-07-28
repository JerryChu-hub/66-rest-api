from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
import os

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass

# Connect to Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cafes.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    if not all_cafes:
        return jsonify(error={"Not Found": "Sorry, we don't have any cafes at the moment."}), 404
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })

@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    if not all_cafes:
        return jsonify(error={"Not Found": "Sorry, we don't have any cafes at the moment."}), 404
    return jsonify(cafes = [cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search():
    result = db.session.execute(db.select(Cafe).where(Cafe.location == request.args.get("loc")))
    all_cafes = result.scalars().all()
    if not all_cafes:
        return jsonify(error={"Not Found": "Sorry, we don't have any cafes at the moment."}), 404
    else:
        return jsonify(cafes = [cafe.to_dict() for cafe in all_cafes])
    
@app.route("/search_id")
def search_id():
    result = db.session.execute(db.select(Cafe).where(Cafe.id == request.args.get("id")))
    cafe = result.scalars().all()
    if not cafe:
        return jsonify(error={"Not Found": "Sorry, we don't have any cafes at the moment."}), 404
    else:
        return jsonify(cafes = [cafe.to_dict()])
    
# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name = request.form.get('name'), 
        map_url = request.form.get('map_url'),
        img_url = request.form.get('img_url'),
        location = request.form.get('location'),
        seats = request.form.get('seats'),
        has_toilet = bool(request.form.get('has_toilet')),
        has_wifi = bool(request.form.get('has_wifi')),
        has_sockets = bool(request.form.get('has_sockets')),
        can_take_calls = bool(request.form.get('can_take_calls')),
        coffee_price = request.form.get('coffee_price'),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response = {'success': 'Successfully added the new cafe.'})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response = {'success': 'Successfully updated the price.'})
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have any cafes at the moment."})

# HTTP DELETE - Delete Record
@app.route('/delete/<int:id>', methods=["DELETE"])
def delete(id):
    key = request.args.get("api-key")
    if key == "TopSecretAPIKey":
        cafe = db.get_or_404(Cafe, id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response = {'success': 'Successfully deleted the cafe.'})
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have any cafes at the moment."})
    else:
        return jsonify(error={"Not Found": "Sorry, you are not authorized to delete the cafe."})

if __name__ == '__main__':
    app.run(debug=True)
