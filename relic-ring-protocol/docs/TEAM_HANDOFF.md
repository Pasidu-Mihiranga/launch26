# Relic Ring Protocol — Team Handoff Document

Welcome to the project! This repository has been professionally scaffolded to allow our 3-person team to work in parallel without causing Git merge conflicts. 

This document serves as the "Source of Truth" for where we are right now, and exactly what each team member needs to do next.

---

## 🟢 Current Project State (What is already done)
**Member 1 (Physics & Data Model)** has completed their core responsibilities:
1. **Config Loading**: `src/config_parser.py` is fully functional. It extracts universe limits and planet data from `universe-config.json` into typed Python dataclasses.
2. **Physics Engine**: `src/physics_engine.py` is finished. It uses **$O(1)$ angular vector projections** to find line-of-sight towers and strict 9-decimal rounding to prevent floating-point precision loss.
3. **Tests**: All mathematical rules ($L, T_v, T_p$) have been verified by `pytest` in `tests/test_physics.py`.

---

## 🎯 Next Steps: Member 2 (Routing & Resilience)

**Your Goal:** Build the brain of the network using the physics engine built by Member 1.

1. **Read the Docs:** Before coding, read `docs/algorithm_comparison.md` and `docs/latency_breakdown.md`. They explain our architectural decisions (A* admissibility, Yen's K=3).
2. **Graph Builder (`src/graph_builder.py`):**
   - Write a script that iterates through all pairs of planets.
   - Use `physics_engine.void_distance()` to check if the distance exceeds $L_{max}$ (50,000,000 km). **If it does, do not create the edge.**
   - If it is valid, use `void_travel_time()` and `crust_transit_time()` to calculate the exact latency cost. Store these costs in an Adjacency Dictionary (the pre-computed hybrid model).
3. **Routing Engine (`src/routing_engine.py`):**
   - Implement Dijkstra's algorithm using Python's `heapq` module.
   - Implement A* (A-Star) using the straight-line distance divided by $C$ (speed of light) as your heuristic.
4. **Resilience Engine (`src/resilience_engine.py`):**
   - Implement `kill_node()` to simulate the Chaos Test.
   - Implement Yen’s K-Shortest Paths to ensure if the primary route fails, we instantly failover to Route #2 in $O(1)$ time.

---

## 🎯 Next Steps: Member 3 (Codec & UI Visualization)

**Your Goal:** Handle the data translation and the final visual demo for the judges. You are currently unblocked and can build these components using mock routing data!

1. **Read the Challenge Spec:** Specifically the "Hello World" example in `Launch26 - Phase 01 - Challenge.md` to understand how `hop_log` objects are structured.
2. **Packet Codec (`src/packet_codec.py`):**
   - The user payload ("Hello World") starts in ASCII.
   - Every planet uses a different numerical Base (Aegis = Base 8, Caelum = Base 14).
   - Write the translation logic to convert the payload from ASCII $\to$ Planet A's Base $\to$ Planet B's Base $\to$ Destination ASCII.
3. **Visualizer (`src/visualizer.py`):**
   - Use `matplotlib`, `pygame`, or a simple HTML canvas to draw the planets using their $(x, y)$ coordinates.
   - Draw lines between them representing the fiber/laser routes.
   - When Member 2 kills a node, the UI should visually show the primary route flashing red and instantly swapping to the backup path.

---

## ⚠️ Golden Rules for the Team
- **Do not modify `physics_engine.py`**: It is mathematically locked. If you need a physics property, just import it.
- **Run the tests**: Before committing your code, run `pytest`. If you break the physics engine tests, do not push!
- **Commit frequently**: Write small, descriptive commits (e.g., `feat: added A* heuristic function`).
