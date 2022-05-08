#  Copyright (c) 2022, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN

from csv import DictReader, DictWriter
import ezomero
import logging
import sys
from argparse import ArgumentParser


class OMESlidesPathResolver(object):
    def __init__(
        self,
        host,
        port,
        user,
        password,
        slides_list,
        out_file,
        log_level="INFO",
        log_file=None,
    ):
        self.conn = self._get_connection(host, port, user, password)
        self.slides_list = slides_list
        self.out_file = out_file
        self.logger = self.get_logger(log_level, log_file)

    def get_logger(self, log_level="INFO", log_file=None, mode="a"):
        LOG_FORMAT = "%(asctime)s|%(levelname)-8s|%(message)s"
        LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

        logger = logging.getLogger("slides_path_resolver")
        if not isinstance(log_level, int):
            try:
                log_level = getattr(logging, log_level)
            except AttributeError:
                raise ValueError("Unsupported literal log level: %s" % log_level)
        logger.setLevel(log_level)
        logger.handlers = []
        if log_file:
            handler = logging.FileHandler(log_file, mode=mode)
        else:
            handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _get_connection(self, host, port, user, password):
        return ezomero.connect(
            host=host, port=port, secure=True, user=user, password=password, group=""
        )

    def _close_connection(self):
        self.conn.close()

    def run(self):
        with open(self.slides_list) as f, open(self.out_file, "w") as of:
            reader = DictReader(f)
            writer = DictWriter(of, ["slide_label", "omero_id", "slide_path"])
            writer.writeheader()
            for row in reader:
                self.logger.info(
                    "Loading data for slide {0} with OME ID {1}".format(
                        row["slide_label"], row["omero_id"]
                    )
                )
                fpath = ezomero.get_original_filepaths(self.conn, int(row["omero_id"]))[
                    0
                ]
                writer.writerow(
                    {
                        "slide_path": fpath,
                        "slide_label": row["slide_label"],
                        "omero_id": row["omero_id"],
                    }
                )
        self._close_connection()


def get_parser():
    parser = ArgumentParser("Get file paths for a given set of OMERO slides")
    parser.add_argument("--ome-host", type=str, required=True, help="OMERO host")
    parser.add_argument("--port", type=int, default=4064, help="OMERO server port")
    parser.add_argument("--user", type=str, required=True, help="username")
    parser.add_argument("--passwd", type=str, required=True, help="password")
    parser.add_argument(
        "--slides-list",
        type=str,
        required=True,
        help="the CSV file containing the slides list",
    )
    parser.add_argument(
        "--output-file", type=str, required=True, help="outout CSV file"
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO", help="log level (default=INFO)"
    )
    parser.add_argument(
        "--log-file", type=str, default=None, help="log file (default=stderr)"
    )
    return parser


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    path_resolver = OMESlidesPathResolver(
        args.ome_host,
        args.port,
        args.user,
        args.passwd,
        args.slides_list,
        args.output_file,
        args.log_level,
        args.log_file,
    )
    path_resolver.run()


if __name__ == "__main__":
    main(sys.argv[1:])
