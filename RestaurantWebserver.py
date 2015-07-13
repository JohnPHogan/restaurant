from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print self.path
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/formdata'"
                output += " action = 'restaurants/new'>"
                output += "<input name = 'newRestaurantname' type = 'text'"
                output += " placeholder = 'New Restaurant Name'>"
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                print output
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Restaurants</h1>"

                restaurants = session.query(Restaurant).all()
                output += "<a href = 'restaurants/new'>Add New Restaurant</a>"
                output += "</br></br>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href = '#' >edit</a>"
                    output += "</br>"
                    output += "<a href = '#' >delete</a>"
                    output += "</br> "
                    output += "</br> "
                    output += "</br> "

                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):

        try:
            if self.path.endswith("restaurants/new"):
                print "made it into the logic"
                ctype, pdict = cgi.parse_header(
                    self.headers.getheaders('Content-type')
                )
                print ctype
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('newRestaurantname')
                    print restaurant_name[0]
                    print restaurant_name
                    new_restaurant = Restaurant(name=restaurant_name[0])
                    session.add(new_restaurant)
                    session.commit()

            if self.path.endswith("/edit") or self.path.endswith("/delete"):
                self.send_response(301)

                if self.path.endswith("/edit"):
                    ctype, pdict = cgi.parse_header(
                        self.headers.getheader('content-type')
                    )
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
            return

        except Exception:
            print "Had an error"


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server is running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
