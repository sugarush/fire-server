import argparse

import handlers
import resource
import seed
import log

from server import server


parser = argparse.ArgumentParser(description='Sugar Server')

parser.add_argument('--workers', type=int, default=1)
parser.add_argument('--host', default='0.0.0.0')
parser.add_argument('--port', type=int, default=8001)
parser.add_argument('--debug', action='store_const', const=True, default=False)

args = parser.parse_args()


server.run(host=args.host, port=args.port, debug=args.debug, workers=args.workers)
