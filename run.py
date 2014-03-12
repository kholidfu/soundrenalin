#!/usr/bin/env python
from app import app

#app.config['SERVER_NAME'] = 'www.soundrenalin.org'
if __name__ == "__main__":
    app.run(debug=False)
