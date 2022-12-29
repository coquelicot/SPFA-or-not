#!/usr/bin/python3

import sys
import argparse
import random


def gen(n, seed):
  assert n >= 3
  prng = random.Random(seed)

  edge_map = {}
  for i in range(n - 2):
    jitter = prng.randint(0, 1)
    edge_map[(i, i + 1)] = 2 + jitter
    edge_map[(i, i + 2)] = 5 - jitter
  edge_map[(n - 2, n - 1)] = 2

  for i in range(n - 3):
    while True:
      st = prng.randint(0, n - 1)
      ed = prng.randint(0, n - 1)
      if st > ed:
        st, ed = ed, st
      if st != ed and (st, ed) not in edge_map:
        break
    edge_map[(st, ed)] = (ed - st) * 3

  assert len(edge_map) == 3 * n - 6
  edge_list = [key + (value,) for key, value in edge_map.items()]
  prng.shuffle(edge_list)
  return edge_list


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--seed', type=int, default=514, help='PRNG seed')
  parser.add_argument('num_node', type=int, help='number of node n graph')
  parser.add_argument(
      'output_file', type=argparse.FileType('w'), help='output file')

  args = parser.parse_args()
  edges = gen(args.num_node, args.seed)

  print(args.num_node, len(edges), file=args.output_file)
  for (st, ed, cst) in edges:
    print(st, ed, cst, file=args.output_file)


if __name__ == '__main__':
  main()
