from server import app, socketio

if __name__ == '__main__':
    socketio.run(app, log_output=True)
