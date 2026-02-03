from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html', title="Главная", content="Добро пожаловать на главную страницу!")

@app.route('/page1')
def page1():
    return render_template('base.html', title="Страница 1", content="Это содержимое страницы 1")

@app.route('/page2')
def page2():
    return render_template('base.html', title="Страница 2", content="Это содержимое страницы 2")

@app.route('/page3')
def page3():
    return render_template('base.html', title="Страница 3", content="Это содержимое страницы 3")

if __name__ == '__main__':
    app.run(debug=True)