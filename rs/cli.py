import argparse
import datetime
import sys

from rs import data


def _iso_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid --as-of {value!r}, expected YYYY-MM-DD")


def parse_args(argv):
    p = argparse.ArgumentParser(prog="review-status")
    p.add_argument("submission_id")
    p.add_argument("--as-of", dest="as_of", type=_iso_date, default=None,
                   help="YYYY-MM-DD (default: see SPEC Q9, unresolved)")
    p.add_argument("--json", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        submission = data.fetch_submission(args.submission_id)
    except data.DataSourceError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if submission is None:
        print(f"error: unknown submission {args.submission_id}", file=sys.stderr)
        return 1
    return 0
