from app import app as application
from app import ecb_initial


if __name__ == '__main__':
    #ecb_initial()
    application.run(debug=True)
