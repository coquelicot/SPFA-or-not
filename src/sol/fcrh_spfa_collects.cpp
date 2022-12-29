#include <deque>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <queue>
#include <random>
#include <string>
#include <utility>
#include <vector>

using Node = int;
using Cost = int;
using Dist = long long;
using DistVec = std::vector<long long>;
using Graph = std::vector<std::vector<std::pair<Node, Cost>>>;

class QueueSched {  // {{{
 public:
  std::optional<Node> Next() {
    if (que_.empty()) return std::nullopt;
    Node n = que_.front();
    que_.pop();
    return n;
  }
  void Enque(Node n, const DistVec&) { que_.push(n); }

 private:
  std::queue<Node> que_;
};  // }}}

class RandSched {  // {{{
 public:
  std::optional<Node> Next() {
    if (nodes_.empty()) return std::nullopt;
    std::uniform_int_distribution<size_t> idx_dist(0, nodes_.size() - 1);
    std::swap(nodes_[idx_dist(prng_)], nodes_.back());
    Node n = nodes_.back();
    nodes_.pop_back();
    return n;
  }
  void Enque(Node n, const DistVec&) { nodes_.push_back(n); }

 private:
  std::mt19937 prng_;
  std::vector<Node> nodes_;
};  // }}}

class SlfSched {  // {{{
 public:
  std::optional<Node> Next() {
    if (deq_.empty()) return std::nullopt;
    Node n = deq_.front();
    deq_.pop_front();
    return n;
  }
  void Enque(Node n, const DistVec& dists) {
    if (deq_.empty() || dists[deq_.front()] < dists[n]) {
      deq_.push_back(n);
    } else {
      deq_.push_front(n);
    }
  }

 private:
  std::deque<Node> deq_;
};  // }}}

class HeapSched {  // {{{
 public:
  std::optional<Node> Next() {
    if (heap_.empty()) return std::nullopt;
    Node n = heap_.top().second;
    heap_.pop();
    return n;
  }
  void Enque(Node n, const DistVec& dists) { heap_.push({dists[n], n}); }

 private:
  using Pair = std::pair<Dist, Node>;
  std::priority_queue<Pair, std::vector<Pair>, std::greater<Pair>> heap_;
};  // }}}

template <typename Sched>
Dist Spfa(const Graph& graph) {  // {{{
  Sched sched;
  std::vector<bool> in_que(graph.size());
  DistVec dists(graph.size(), std::numeric_limits<Dist>::max());

  dists[0] = 0;
  in_que[0] = true;
  sched.Enque(0, dists);
  while (auto nopt = sched.Next()) {
    in_que[*nopt] = false;
    for (auto [adj, cost] : graph[*nopt]) {
      // Assumes no overflow here.
      if (dists[adj] > dists[*nopt] + cost) {
        dists[adj] = dists[*nopt] + cost;
        if (in_que[adj]) continue;
        in_que[adj] = true;
        sched.Enque(adj, dists);
      }
    }
  }

  return dists.back();
}  // }}}

Dist Dijkstra(const Graph& graph) {  // {{{
  using Pair = std::pair<Dist, int>;
  std::priority_queue<Pair, std::vector<Pair>, std::greater<Pair>> heap;
  DistVec dists(graph.size(), std::numeric_limits<Dist>::max());

  dists[0] = 0;
  heap.push({0, 0});
  while (!heap.empty()) {
    auto [rec_dist, node] = heap.top();
    heap.pop();
    if (rec_dist != dists[node]) continue;
    for (auto [adj, cost] : graph[node]) {
      if (dists[adj] > dists[node] + cost) {
        dists[adj] = dists[node] + cost;
        heap.push({dists[adj], adj});
      }
    }
  }

  return dists.back();
}  // }}}

void Solve(Dist (*algo)(const Graph&)) {
  std::ios::sync_with_stdio(false);

  int n, m;
  std::cin >> n >> m;
  Graph graph(n);
  for (int i = 0; i < m; ++i) {
    Node src, dst;
    Cost cst;
    std::cin >> src >> dst >> cst;
    graph[src].push_back({dst, cst});
  }

  std::cout << algo(graph) << std::endl;
}

int main(int argc, char* argv[]) {
  std::string target_algo = argc > 1 ? argv[1] : "queue";

  std::map<std::string, Dist (*)(const Graph&)> algo_map = {
      {"queue", &Spfa<QueueSched>}, {"random", &Spfa<RandSched>},
      {"slf", &Spfa<SlfSched>},     {"heap", &Spfa<HeapSched>},
      {"dijkstra", &Dijkstra},
  };

  auto it = algo_map.find(target_algo);
  if (it == algo_map.end()) {
    std::cerr << "Unknown variant: " << target_algo << std::endl;
    for (auto item : algo_map) {
      std::cerr << "  " << item.first << std::endl;
    }
    return 1;
  }
  Solve(it->second);
}
