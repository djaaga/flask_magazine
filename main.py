from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cloudipsp import Api, Checkout


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/buy/<int:id>/')
def buy(id):
    item = Item.query.get(id)
    api = Api(
        merchant_id=1396424,
        secret_key='test'
        )
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(item.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template('post_detail.html', article=article)


@app.route('/posts/<int:id>/del')
def post_delete(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'Че натворил(а) то, удаление не получилось!'


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']
        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return 'Че натворил(а) то ?'
    else:
        return render_template('post_update.html', article=article)

@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(
            title=title,
            intro=intro,
            text=text
        )
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'Че натворил(а) то ?'
    else:
        return render_template('create-article.html')

@app.route('/create-item', methods=['POST', 'GET'])
def create_item():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']

        item = Item(title=title, price=price, text=text)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return str(e)
        finally:
            db.session.close()
    else:
        return render_template('create-item.html')


# If you need to delete som record in data base use this function + html button
# @app.route('/delete-item/<int:id>/del', methods=['POST'])
# def delete_item(id):
#     item = Item.query.get(id)
#     if item:
#         try:
#             db.session.delete(item)
#             db.session.commit()
#             return redirect('/')
#         except Exception as e:
#             return str(e)
#     else:
#         return "Item with id {} does not exist".format(id)


if __name__ == '__main__':
    app.run(debug=True)
