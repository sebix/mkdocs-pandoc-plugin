import os
import logging
import contextlib
from pathlib import Path
from typing import List

log = logging.getLogger("mkdocs.plugins.pandoc")


@contextlib.contextmanager
def run_in_path(p):
    saved = os.getcwd()
    os.chdir(p)
    try:
        yield p
    finally:
        os.chdir(saved)


class Pandoc(object):
    def __init__(self, in_files: List[str], out_file, work_dir, extra_args: str = "", **opts):
        self.opts = opts
        self.in_files = in_files
        self.out_file = out_file
        self.work_dir = work_dir
        self.extra_args = extra_args

    @property
    def args(self):
        args = []
        for opt, val in self.opts.items():
            opt = opt.replace("_", "-")
            log.debug(f"Pandoc arg: --{opt}={val}")
            args.append(f"--{opt}={val}")
        return args

    def write(self, *args):
        args = [self.extra_args] + list(args) + self.args
        self.run(args, "-o", self.out_file, *self.in_files)

    def run(self, args: List, *argv):
        args = ["pandoc"] + args + list(argv)
        command = " ".join(args)
        with run_in_path(self.work_dir):
            log.debug(f"{os.getcwd()}> {command}")
            os.system(command)


class Renderer(object):
    def __init__(
        self,
        combined: bool,
        docs_dir: str = "",
        extra_args: str = "",
        template: str = "",
        **args,
    ):
        self.combined = combined
        self.docs_dir = docs_dir
        self.page_order = []
        self.pgnum = 0
        self.pages = []
        self.args = args
        self.extra_args = extra_args

        if os.path.isfile(template) and os.path.exists(template):
            self.args["template"] = template

    def write_pandoc(self, mk_filename: List[str], out_filename: str):
        mk_filename = [mk_filename] if not isinstance(mk_filename, list) else mk_filename
        pandoc = Pandoc(
            mk_filename,
            out_filename,
            self.docs_dir,
            extra_args=self.extra_args,
            **self.args,
        )
        pandoc.write()

    def add_doc(self, rel_path: str, abs_path: str):
        try:
            pos = self.page_order.index(rel_path)
            self.pages[pos] = abs_path
        except:
            pass

    def write_combined_pandoc(self, output_path: str):
        self.write_pandoc(self.pages, output_path)
