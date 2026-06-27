# Latency Topology & Breakdown Strategy

This document details the exact mathematical constraints that govern the graph generation and latency weighting for the Relic Ring Protocol. 

By isolating the physics engine from the routing engine, we ensure absolute mathematical determinism.

---

## 1. Graph Generation Constraints

Before any routing algorithm runs, the **Graph Builder** pre-filters the universe based on strict physical limitations.

### The $L_{max}$ Cutoff Boundary
The challenge spec enforces a hard limit: $L_{max} = 50,000,000$ km. 

* **Implementation:** When constructing the adjacency list, if the calculated void distance $L$ between Planet A and Planet B exceeds $L_{max}$, the edge is **not added to the graph**.
* **Result:** The routing engine (Dijkstra) never even sees invalid physical paths, eliminating the need to check distances on the fly during routing loops. This massive optimization speeds up convergence time by pruning the search tree at the root.

---

## 2. The Weight of an Edge

In a standard graph, an edge connects Node A to Node B with a single weight $W$. 
In the Relic Ring Protocol, the weight of traversing from Planet A to Planet B is composite.

To route a packet successfully, the latency cost is:
$$W_{AB} = T_p(\text{Planet A}) + T_v(\text{Void A} \to \text{Void B}) + T_p(\text{Planet B})$$

### Component Breakdown:

#### A. Crust Transit Time ($T_p$)
The time taken to route the signal via physical fiber optics around the planet's crust to the optimal transmission tower.
* **Fiber Delay:** Calculated based on the shortest arc between the entry tower and the exit tower, traveling at $f = 0.67C$.
* **Tower Processing Delay:** Every distinct tower the packet passes through incurs a $\Delta t$ penalty (default 7ms).
* **The Deduplication Rule:** If the packet arrives from the void at Tower 0, and leaves for the next planet via Tower 0, the segments traveled is 0. Instead of charging 0 delay, the formula correctly assigns $m=1$ to charge exactly one $\Delta t$ processing penalty for hitting the tower hardware.

#### B. Void Travel Time ($T_v$)
The time taken to beam the laser through the vacuum of space, including planetary atmospheres.
* **Atmospheric Refraction:** Passing through a planet's atmosphere (thickness $h$) slows the light down based on the refraction index $n$. This is calculated as exactly straight through the shell.
* **Vacuum Speed:** The bulk of the distance ($L$) is traveled at exactly $C$ (300,000 km/s).

---

## 3. Precision Engineering
All time outputs ($T_v$ and $T_p$) are rounded to 9 decimal places at the API boundary. This ensures that floating-point addition of large and small magnitudes does not cause non-deterministic behavior across different CPU architectures.
