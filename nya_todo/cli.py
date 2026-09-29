"""CLI: python3 -m nya_todo.cli {serve,meow,why}"""
import argparse
import json

from .cat_engine_bridge import CatEngineBridge
from .server import makeServer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="nya_todo")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve", help="run the todo server (or accounting server, or space agency)")
    meow = sub.add_parser("meow", help="score a todo with the catgirl compiler")
    meow.add_argument("title")
    meow.add_argument("--priority", type=int, default=1)
    sub.add_parser("why", help="no")
    args = parser.parse_args(argv)

    if args.cmd == "serve":
        server = makeServer()
        print("nya_todo listening on http://%s:%s" % server.server_address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    elif args.cmd == "meow":
        print(json.dumps(CatEngineBridge().compile(args.title, args.priority)))
    else:
        print("historical reasons")


if __name__ == "__main__":
    main()
