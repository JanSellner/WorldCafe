from server import app

if __name__ == '__main__':
    '''For development'''
    app.run(port=5080, debug=True)
