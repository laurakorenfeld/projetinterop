from socket import SocketIO

from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, ssl_context=('/Users/LKorenfeld/Documents/Travail/ITS/projetinterop/cert.pem', '/Users/LKorenfeld/Documents/Travail/ITS/projetinterop/key.pem'))

