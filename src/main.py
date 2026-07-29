import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import FocoNoTrabalhoApp

def main():
    app = FocoNoTrabalhoApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
