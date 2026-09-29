from app import create_app, db
from flask import send_from_directory

app = create_app()

# Runs every time the app starts, including under gunicorn on Render
with app.app_context():
    db.create_all()
    print("Tables ready!")


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js',
                               mimetype='application/javascript')

if __name__ == "__main__":
    print("Starting BulkMate...")
    app.run(debug=True)