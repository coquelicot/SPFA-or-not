#!/usr/bin/python3

import argparse
import re
import sys

MAX_N = 1_000_000
MAX_M = 3_000_000
MAX_ABS_CST = 1_000_000_000

HEADER_LINE_FMT = r'^\d+ \d+$'
EDGE_LINE_FMT = r'^\d+ \d+ -?\d+$'


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'target_file', type=argparse.FileType('r'), help='the file to check')
  parser.add_argument(
      '--allow_self_cyc', action='store_true', help='allow self cycle')
  parser.add_argument(
      '--allow_dup', action='store_true', help='allow duplicated edges')
  parser.add_argument(
      '--allow_neg', action='store_true', help='allow negative edge')
  parser.add_argument(
      '--allow_orphen',
      action='store_true',
      help='allow unreachable node(s) from, except for the destination')
  args = parser.parse_args()

  try:
    check_format(args.target_file, args.allow_self_cyc, args.allow_dup,
                 args.allow_neg, args.allow_orphen)
  except CheckError as exc:
    print(exc, file=sys.stderr)
    sys.exit(1)


class CheckError(Exception):
  pass


def check_format(target_file, allow_self_cyc, allow_dup, allow_neg,
                 allow_orphen):
  line_iter = iter(target_file)
  min_cst = -MAX_ABS_CST if allow_neg else 0

  header_line = _next_or_die(line_iter, 'missing header line').rstrip('\n')
  _check_match(HEADER_LINE_FMT, header_line, 'invalid header line')
  n, m = map(int, header_line.split())
  _check_range(n, 1, MAX_N, 'invalid number of node')
  _check_range(m, 1, MAX_M, 'invalid number of edge')

  edges = set()
  for _ in range(m):
    edge_line = _next_or_die(line_iter, 'missing edge line').rstrip('\n')
    _check_match(EDGE_LINE_FMT, edge_line, 'invalid edge line')
    src, dst, cst = map(int, edge_line.split())
    edge = (src, dst)
    _check_range(src, 0, n - 1, 'invalid source node')
    _check_range(dst, 0, n - 1, 'invalid destination node')
    _check_range(cst, min_cst, MAX_ABS_CST, 'invalid cost')
    _check(allow_self_cyc or src != dst, 'self cycle {} detected'.format(edge))
    _check(allow_dup or edge not in edges,
           'duplicated edge {} detected'.format(edge))
    edges.add(edge)

  _stop_or_die(line_iter, 'extra line(s) detected')
  _check_connectivity(n, edges, allow_orphen, 'invalid graph')


def _check_connectivity(n, edges, allow_orphen, msg):
  vis = [False] * n
  adjs = [[] for _ in range(n)]
  for edge in edges:
    adjs[edge[0]].append(edge[1])

  candis = [0]
  vis[0] = True
  while candis:
    curr = candis.pop()
    for adj in adjs[curr]:
      if not vis[adj]:
        vis[adj] = True
        candis.append(adj)

  orphens = [i for i, v in enumerate(vis) if not v]
  if orphens and (not allow_orphen or orphens[-1] == n - 1):
    raise CheckError('{}: {} is not reachable from 0'.format(msg, orphens[-1]))


def _check_range(v, mn, mx, msg):
  _check(mn <= v <= mx, '{}: {} not in [{}, {}]'.format(msg, v, mn, mx))


def _check_match(fmt, line, msg):
  _check(re.match(fmt, line), '{}: "{}" not matching {}'.format(msg, line, fmt))


def _check(cond, msg):
  if not cond:
    raise CheckError(msg)


def _next_or_die(gen, msg):
  try:
    return next(gen)
  except StopIteration:
    raise CheckError(msg)


def _stop_or_die(gen, msg):
  try:
    next(gen)
    raise CheckError(msg)
  except StopIteration:
    pass


if __name__ == '__main__':
  main()
