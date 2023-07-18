from website import create_app
from flask import render_template, request
from flask_login import current_user

app = create_app()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    return render_template('search.html', query=query, results=[], user=current_user)

if __name__ == '__main__':
    app.run(debug=True)