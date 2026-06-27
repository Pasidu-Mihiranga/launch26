# Launch 26 - Phase 01: The Relic Ring Protocol
## Challenge Analysis

### 1. What is this problem?
The "Relic Ring Protocol" is a competitive programming challenge designed around network routing and physics-based simulation. The narrative involves reconnecting a fractured star system (Zeta-26) using primitive legacy infrastructure. 

The core of the problem is to simulate data packets traveling between different planets (nodes) across a space network. The packets incur various mathematical delays as they travel through physical mediums:
- **Subsurface Fiber Transit:** Traveling across a planet's surface between towers.
- **Processing Tower Delay:** Data processing delays at each routing tower on a planet.
- **Atmospheric Refraction:** Signal slowdown when piercing a planet's atmosphere.
- **Void Transmission:** Laser transmission across the vacuum of space (with a strict maximum limit of 50,000,000 km per hop).

Additionally, the planets have different mathematical bases (dialects). A packet's payload must be continuously translated from one base to another (e.g., Base 8 -> ASCII -> Base 14) as it travels from node to node.

### 2. What do you have to do?
You need to build a software system (and provide a 10-15 min demo video) that does the following:
1. **Parses Configuration:** Dynamically loads the network topology and planet physics from `universe-config.json` (no hardcoding allowed).
2. **Shortest-Path Routing Algorithm:** Finds the most efficient (lowest latency) route from a source planet to a destination planet.
3. **Latency Calculation:** Computes the exact travel time using provided mathematical formulas from the `Equations .md` file (Void travel, Atmospheric refraction, Crust transit).
4. **Data Encoding/Decoding:** Translates the packet payload between different numerical bases as it hops through the network.
5. **Dynamic Resilience:** Automatically reroutes packets around failed nodes or broken links in real-time without crashing or dropping the data ("Chaos Test").
6. **Visualization/UI:** Provides a way for users to view the full packet path, detailed hop logs, and a breakdown of the latency calculations.

### 3. What type of challenge is this?
This is a **Graph Theory & Network Simulation** challenge. It heavily incorporates:
- **Algorithmic Optimization:** Specifically, implementing pathfinding algorithms like Dijkstra's or A* Search Algorithm, modified to use custom latency calculations as edge weights rather than simple distance.
- **Systems Engineering:** Building a robust architecture that can handle node failures and re-calculate paths dynamically.
- **Mathematics & Physics Simulation:** Applying provided geometry and physics equations to calculate accurate time delays.
- **Data Manipulation:** Handling base conversions and ASCII encoding/decoding.

### 4. Are there similar challenges available?
Yes! This specific blend of graph routing, physical constraints, and simulation is very popular in high-level collegiate and professional algorithmic competitions. If you want to practice or look for similar problem patterns, look into:

*   **IEEE IEEEXtreme Programming Competition:** Because this is an IEEE CS event, it draws heavy inspiration from IEEEXtreme. Past IEEEXtreme problems (available on platforms like CSAcademy) frequently feature these multi-layered simulation and graph tasks.
*   **Google Hash Code / Code Jam (Archived):** Google frequently used network routing and physical optimization simulations (e.g., routing internet balloons or optimizing fiber network layouts).
*   **Advent of Code:** These annual December programming puzzles often feature complex graph traversal problems with highly specific custom rules (similar to the base-conversion and tower-routing rules found here).
*   **ACM ICPC (International Collegiate Programming Contest):** Contains many advanced problems based on shortest-path algorithms with added physical constraints.

**Keywords for deep searching practice materials:**
- *Constrained Shortest Path First (CSPF) algorithms in Python/Java*
- *Dynamic Network Routing Simulation coding challenges*
- *Dijkstra's Algorithm with dynamic edge weights and node penalties*
- *Discrete-event network simulator tutorials*

### 5. Technologies, Algorithms, & Domain Knowledge Needed
*   **Algorithms:** 
    *   **Shortest-Path Graph Algorithms:** Dijkstra’s Algorithm or A* Search, heavily modified. Instead of calculating simple edge length, the "weight" of moving from node A to node B must be calculated on-the-fly using the provided latency equations.
    *   **Base Conversion Algorithms:** Fast radix conversions (converting Base X to Base Y via an intermediate like ASCII/Base 10).
*   **Domain Knowledge:** 
    *   **Graph Theory:** Nodes, edges, directed/undirected graphs, adjacency lists.
    *   **Physics/Math:** Basic kinematics (Time = Distance / Speed), trigonometry (for distance between circles, if needed), and atmospheric refraction.
    *   **Networking:** Packet switching, hop logs, routing protocols, and error handling (dead nodes).
*   **Technologies:** 
    *   **Backend/Logic:** Python, Java, C++, or Go (languages with strong math and data structure support). Python is highly recommended for its math libraries and quick iteration.
    *   **Visualization:** A way to build the UI/Demo. Python's `NetworkX` with `Matplotlib`/`Pygame`, or a web frontend (React + HTML5 Canvas / D3.js).

### 6. How will competitors evaluate this?
According to the challenge rubric, evaluation is heavily weighted towards **Accuracy** and **Resilience**:
1.  **Baseline Delivery (Critical):** First and foremost, the packet MUST reach the destination, and the mathematical base translations must be printed out accurately at every step.
2.  **Latency Accuracy (High):** The math must be flawless. A route is useless if the floating-point math for refraction or the speed of light is calculated incorrectly.
3.  **Resilience (High):** The "Chaos Test." When the judges ask you to kill a node or disconnect a fiber line mid-transit, your system must detect it, avoid crashing, and instantly find the *second-best* path.
4.  **Routing Efficiency (Medium):** Ensuring the shortest-path logic is sound and that the `Lmax` (max void distance) rule is strictly enforced.

### 7. Where do participants typically fail?
*   **Floating-Point Math Errors:** Mixing up units (e.g., kilometers vs. meters, milliseconds vs. seconds) resulting in wildly inaccurate latency values.
*   **Ignoring the `Lmax` Rule:** Routing a packet straight through space across a gap of 60,000,000 km when the absolute maximum limit is 50,000,000 km.
*   **The "Chaos Test" (State Management):** When a node goes down, poorly designed systems crash or get stuck in infinite routing loops because they don't update their graph adjacency lists dynamically.
*   **Over-engineering the UI:** Spending 90% of the time building a beautiful React web-app, leaving no time to perfect the complex routing and physics math.

### 8. Enterprise Best Practices for Routing & Resilience
If you were building a system like this in the real world (e.g., for enterprise SD-WAN, ISPs, or data center interconnects), you would follow these industry best practices:
*   **Redundancy & Multi-homing:** Never rely on a single path. Enterprise networks maintain multiple physical connections (diverse fiber paths) so traffic can instantly failover if a backhoe cuts a cable.
*   **Hierarchical Routing (BGP/OSPF):** Instead of every router knowing the entire universe (which doesn't scale), networks are broken into Autonomous Systems (AS) or areas. Routers only need to know how to get to the *border* of the next area.
*   **Event-Driven Chaos Engineering:** Real-world systems run continuous "Chaos Monkey" tests (made famous by Netflix) which randomly shut down production servers and network links to ensure the automated failover mechanisms actually work before a real disaster happens.
*   **Observability & Telemetry:** Relying on tools like OpenTelemetry to generate distributed "hop logs." Every packet leaves a trace, so if traffic slows down, engineers can pinpoint exactly which router or atmospheric link caused the delay.

---

## 9. Golden Rules to Win: The Hackathon Meta
Just like ML competitions are won on data cleaning and chatbot contests are won on latency/prompt optimization, algorithmic networking challenges like this have their own "meta" or golden rules to secure a podium finish.

**Golden Rule 1: The Math is the Test (Isolate & Unit Test)**
In this type of competition, a tiny rounding error cascades into completely failing the auto-grader's expected path. 
*   *The Hack:* Do NOT mix your math with your routing loop. Build a standalone `physics_engine.py` that exclusively calculates $T_p$ and $T_v$. Write unit tests for this file using extreme edge cases (e.g., massive distance, 0 processing delay). Use double-precision floats (`float64`) universally.

**Golden Rule 2: Pre-compute the Lmax Filter (Don't evaluate it late)**
Competitors fail because they run Dijkstra's algorithm and *then* check if the path violates the $L_{max}$ constraint. 
*   *The Hack:* Before you ever route a packet, build your graph (Adjacency Matrix). For every pair of planets $(A, B)$, calculate the Void Distance $L$. If $L > L_{max}$, simply do not add an edge between them in your graph. By filtering the edges at the architecture level, your Dijkstra algorithm never has to worry about $L_{max}$—it just runs natively and fast.

**Golden Rule 3: The "Chaos Test" Requires State Separation**
When the judges say "kill Planet C", you don't want to restart your whole simulation or crash. 
*   *The Hack:* Maintain your network state (the Graph) separate from your routing operation (Dijkstra). Build a simple function like `kill_node(node_id)` that removes the node from your adjacency list and forcefully triggers a graph recalculation. This proves to judges you understand *convergence* (how quickly a network heals itself after a link goes down).

**Golden Rule 4: Visuals Win the Demo (The Video is King)**
The deliverables ask for a 10-15 min demo video. You can have perfect, O(log N) optimized math, but if you show a wall of scrolling terminal text, judges will zone out.
*   *The Hack:* You don't need a heavy 3D React app. Use a lightweight GUI (like Python's `NetworkX` + `Matplotlib`, `Pygame`, or a basic HTML5 Canvas). Draw the planets as circles, draw lines for viable edges, and animate the packet (a glowing dot) moving from A to B. When you run the Chaos Test, make the dead node visually turn red and watch the route instantly draw a new path around it. Visualizing the failover perfectly guarantees a high score.

**Golden Rule 5: Architecture Modularity (No Monoliths)**
Judges grade on code quality. Split your code into distinct subsystems:
1.  `config_parser.py`: Reads JSON, validates missing fields against defaults.
2.  `physics_engine.py`: Pure math functions ($T_v, T_p, L$).
3.  `graph_router.py`: Dijkstra algorithm and dynamic node removal.
4.  `packet_codec.py`: Handles Base-N ↔ ASCII conversions and builds the `hop_log`.
5.  `main.py / visualizer`: Glues it together and handles the UI.
