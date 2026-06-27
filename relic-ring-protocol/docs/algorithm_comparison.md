# Routing Algorithm Architecture Comparison

For the Relic Ring Protocol, relying on a single routing algorithm is insufficient for handling both optimal pathfinding and instantaneous failure recovery (Chaos Test). Our architecture utilizes a **3-Layer Hybrid Approach**.

This document justifies the algorithmic choices against standard alternatives to demonstrate enterprise-grade engineering.

---

## 1. Core Router: Dijkstra's Algorithm (OSPF Standard)

**Why Dijkstra?**
- **Optimal Guarantees:** Dijkstra is provably optimal for graphs where all edge weights are non-negative. Since our edge weights ($T_v + T_p$) are physical time durations, they can never be negative.
- **Industry Standard:** This is the exact algorithm running inside the OSPF (Open Shortest Path First) protocol used by Cisco and Juniper enterprise routers globally.
- **Why not Bellman-Ford?** Bellman-Ford can handle negative weights (which we don't have) but runs in $O(V \times E)$ time. Dijkstra with a Min-Heap runs in $O((V+E) \log V)$ time, making it significantly faster and strictly superior for this physical topology.

---

## 2. Guided Search: A* (A-Star) Optimization

**Why A*?**
While Dijkstra blindly searches in all directions (like a ripple in water), A* uses a heuristic function $h(n)$ to pull the search direction toward the destination, massively reducing the number of nodes evaluated in large topologies.

**Admissibility Proof (Crucial for Optimality):**
For A* to guarantee the shortest path, the heuristic $h(n)$ must be **admissible** — meaning it must *never overestimate* the actual cost to reach the destination.

* **Our Heuristic:** $h(n) = \frac{\text{Straight-Line Distance}(n, \text{dest})}{C}$
* **Proof:** 
  1. The shortest possible physical path between two points in the universe is a straight line.
  2. The fastest possible speed in the universe is the speed of light ($C$) in a perfect vacuum.
  3. Our actual routes must pass through atmospheres (where refraction $n > 1$ slows light down) and fiber cables (where signals travel at $0.67 \times C$), plus incur tower processing delays ($\Delta t$).
  4. Therefore, the actual time will **always** be greater than or equal to $h(n)$. 
  5. Because $h(n)$ strictly underestimates the real cost, it is provably admissible and optimal.

---

## 3. Resilience Engine: Yen’s K-Shortest Paths (K=3)

**The Problem (The Chaos Test):**
If a node suddenly dies (e.g., planet explosion/tower failure), running Dijkstra again takes compute time. In high-frequency trading or critical space infrastructure, waiting milliseconds to recalculate a route is unacceptable.

**The Solution:**
At startup, we run **Yen's Algorithm** to compute not just the shortest path, but the top 3 shortest paths ($K=3$) for every planet pair.

* **Primary Route (K=1):** Used during normal operations.
* **Failover Routes (K=2, K=3):** Stored in a fast-lookup dictionary.

**Why Yen's?**
When the Chaos Test triggers a `kill_node()` event, the system does **zero math**. It simply instantly swaps to the $K=2$ route (as long as $K=2$ doesn't contain the dead node). This guarantees an $O(1)$ failover time, mimicking BGP (Border Gateway Protocol) route caching used by Tier 1 ISPs.
