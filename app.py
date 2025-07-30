from backend import app 
import backend.routes 
import backend.user_routes

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
