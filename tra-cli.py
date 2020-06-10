import argparse
from tasks import Tasker

t = Tasker()

task_map = {"match":None, "metric":None, "pit":None}
status_map = {"match":None, "metric":None, "pit":None}
status_map.update(task_map)

parser = argparse.ArgumentParser(prog = "TRA")
subparsers = parser.add_subparsers(title = "command", metavar = "C", help = "//commandhelp//")

parser_start = subparsers.add_parser("start", help = "//starthelp//")
parser_start.add_argument("target(s)", metavar = "T", nargs = "*", choices = task_map.keys())
parser_start.set_defaults(which = "start")

parser_stop = subparsers.add_parser("stop", help = "//stophelp//")
parser_stop.add_argument("target(s)", metavar = "T", nargs = "*", choices = task_map.keys())
parser_stop.set_defaults(which = "stop")

parser_status = subparsers.add_parser("status", help = "//stophelp//")
parser_status.add_argument("target(s)", metavar = "T", nargs = "*", choices = status_map.keys())
parser_status.set_defaults(which = "status")

options = parser.parse_args()
print(options)