from server import app, socketio

if __name__ == '__main__':
    socketio.run(app, port=5080, debug=True)
    # app.run(port=5080, debug=True)
