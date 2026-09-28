from app import create_app, db
from flask import send_from_directory

app = create_app()



@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js',
                               mimetype='application/javascript')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Creates weightgain.db + all tables on first run
        #print("Database tables created!")
        print(" Starting BulkMate...")
    app.run(debug=True)