from flask import Flask, render_template, request
import werkzeug.serving
import ssl
import OpenSSL

class PeerCertWSGIRequestHandler( werkzeug.serving.WSGIRequestHandler ):
    """
    We subclass this class so that we can gain access to the connection
    property. self.connection is the underlying client socket. When a TLS
    connection is established, the underlying socket is an instance of
    SSLSocket, which in turn exposes the getpeercert() method.

    The output from that method is what we want to make available elsewhere
    in the application.
    """
    def make_environ(self):
        """
        The superclass method develops the environ hash that eventually
        forms part of the Flask request object.

        We allow the superclass method to run first, then we insert the
        peer certificate into the hash. That exposes it to us later in
        the request variable that Flask provides
        """
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        x509 = OpenSSL.crypto.load_certificate( OpenSSL.crypto.FILETYPE_ASN1, x509_binary )
        environ['peercert'] = x509
        return environ

app = Flask(__name__)

# to establish an SSL socket we need the private key and certificate that
# we want to serve to users.
#
# app_key_password here is None, because the key isn't password protected,
# but if yours is protected here's where you place it.
app_key = './server.key'
app_key_password = None
app_cert = './server.crt'

# in order to verify client certificates we need the certificate of the
# CA that issued the client's certificate. In this example I have a
# single certificate, but this could also be a bundle file.
ca_cert = './server.crt'

# create_default_context establishes a new SSLContext object that
# aligns with the purpose we provide as an argument. Here we provide
# Purpose.CLIENT_AUTH, so the SSLContext is set up to handle validation
# of client certificates.
ssl_context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH,
                                          cafile=ca_cert )

# load in the certificate and private key for our server to provide to clients.
# force the client to provide a certificate.
ssl_context.load_cert_chain( certfile=app_cert, keyfile=app_key, password=app_key_password )
ssl_context.verify_mode = ssl.CERT_REQUIRED

# now we get into the regular Flask details, except we're passing in the peer certificate
# as a variable to the template.
@app.route('/')
def hello_world():
    return render_template('helloworld.html', client_cert=request.environ['peercert'])

# start our webserver!
if __name__ == "__main__":
    app.run(ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler)