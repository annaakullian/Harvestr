from flask import Flask, render_template, request

app =  Flask(__name__)

#this is the home page
@app.route('/')
def home_page():
	return render_template("base.html")


if __name__ == '__main__':
	app.run(debug=True)