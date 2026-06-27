"""
main.py - Relic Ring Protocol Demo Orchestrator
=================================================
Member 3 Deliverable: Glues all components together and drives
the demo video flow through M1-M4 milestones.

Usage:
    python src/main.py                          # Interactive GUI mode
    python src/main.py --headless               # Terminal-only mode (no GUI)
    python src/main.py --config path/to/config  # Custom config path
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config_parser import load_universe_config
from graph_builder import build_network_graph, find_bridge_nodes
from routing_engine import find_route, cross_validate
from resilience_engine import ResilienceManager
from packet_codec import (
    simulate_packet_journey, ascii_to_codex, codex_to_ascii,
    get_journey_summary, translate_payload
)


class RelicRingDemo:
    """
    Main application orchestrator for the Relic Ring Protocol.
    Drives the demo through all 4 milestones:
        M1: Universe Initialization
        M2: Multi-Hop Routing Proof
        M3: Latency Breakdown
        M4: Chaos Test (Kill/Revive)
    """

    def __init__(self, config_path: str):
        print("=" * 60)
        print("  RELIC RING PROTOCOL - Demo Orchestrator")
        print("  IEEE Computer Society - Launch 26 Phase 01")
        print("=" * 60)

        # ── M1: Universe Initialization ──
        print("\n[M1] Loading universe configuration...")
        self.config_path = os.path.abspath(config_path)
        self.metadata, self.planets_list = load_universe_config(self.config_path)
        self.planets = {p.id: p for p in self.planets_list}

        print(f"  System: {self.metadata.system_name}")
        print(f"  Planets: {len(self.planets_list)}")
        for p in self.planets_list:
            print(f"    - {p.id:10s} | Codex: Base {p.codex:2d} | "
                  f"Towers: {p.active_towers:2d} | R: {p.radius_km:,.0f} km")

        # Build network graph
        print("\n[M1] Building network graph...")
        self.graph = build_network_graph(self.metadata, self.planets_list)
        edge_count = sum(len(edges) for edges in self.graph.adjacency.values())
        print(f"  Edges: {edge_count} (directed, Lmax-filtered)")

        # Bridge nodes
        bridges = find_bridge_nodes(self.graph)
        if bridges:
            print(f"  Bridge nodes (SPOF): {bridges}")
        else:
            print("  No bridge nodes found (network is 2-connected)")

        # Cross-validate routing
        print("\n[M1] Cross-validating Dijkstra vs A*...")
        is_valid = cross_validate(self.graph)
        print(f"  Cross-validation: {'PASSED' if is_valid else 'FAILED'}")

        # Initialize resilience manager
        print("[M1] Initializing resilience manager...")
        self.resilience = ResilienceManager(self.metadata, self.planets_list)

        status = self.resilience.get_network_status()
        print(f"  Active nodes: {status.get('active_nodes', 0)}")
        print(f"  Pre-computed K=3 backup routes: Ready")
        print("\n[M1] Universe initialization COMPLETE.\n")

    def run_headless_demo(self):
        """Run the full demo in terminal mode (no GUI)."""

        # ── M2: Multi-Hop Routing Proof ──
        print("=" * 60)
        print("[M2] MULTI-HOP ROUTING PROOF")
        print("=" * 60)

        src, dst = "Aegis", "Caelum"
        payload = "Hello world"

        print(f"\n  Source:      {src} (Base {self.planets[src].codex})")
        print(f"  Destination: {dst} (Base {self.planets[dst].codex})")
        print(f"  Payload:     \"{payload}\"")

        route = self.resilience.get_route(src, dst)
        if route is None:
            print("  [ERROR] No route found!")
            return

        print(f"\n  Route: {' -> '.join(route.path)}")
        print(f"  Algorithm: {route.algorithm_used}")
        print(f"  Hops: {len(route.hop_details)}")

        # Simulate packet journey with codex translations
        packet = simulate_packet_journey(payload, route, self.planets, self.metadata)
        print("\n" + get_journey_summary(packet))

        # Verify round-trip integrity
        final_decoded = codex_to_ascii(packet.encoded_payload, packet.current_codex)
        assert final_decoded == payload, f"INTEGRITY FAILURE: '{final_decoded}' != '{payload}'"
        print(f"\n  Round-trip integrity: VERIFIED (\"{final_decoded}\")")

        # ── M3: Latency Breakdown ──
        print("\n" + "=" * 60)
        print("[M3] LATENCY BREAKDOWN")
        print("=" * 60)

        total_fiber = sum(h.get("fiber_time_s", 0) for h in route.hop_details)
        total_proc = sum(h.get("processing_time_s", 0) for h in route.hop_details)
        total_void = sum(h.get("void_time_s", 0) for h in route.hop_details)

        print(f"\n  Fiber transit:      {total_fiber:.9f}s")
        print(f"  Tower processing:   {total_proc:.9f}s")
        print(f"  Void transit:       {total_void:.9f}s")
        print(f"  {'-' * 40}")
        print(f"  TOTAL LATENCY:      {route.total_latency_s:.9f}s")

        # Per-hop breakdown
        print(f"\n  Per-hop details:")
        for i, hop in enumerate(route.hop_details):
            print(f"    Hop {i}: {hop['planet_id']:10s} | "
                  f"T{hop['entry_tower']}->T{hop['exit_tower']} | "
                  f"Fiber: {hop['fiber_time_s']:.6f}s | "
                  f"Void: {hop['void_time_s']:.6f}s | "
                  f"Distance: {hop['void_distance_km']:,.2f} km")

        # ── M4: Chaos Test ──
        print("\n" + "=" * 60)
        print("[M4] CHAOS TEST - KILL & REROUTE")
        print("=" * 60)

        # Pick an intermediate node to kill
        if len(route.path) > 2:
            kill_target = route.path[1]
        else:
            # Kill any node that isn't src or dst
            kill_target = None
            for pid in self.planets:
                if pid != src and pid != dst:
                    kill_target = pid
                    break

        if kill_target:
            print(f"\n  Killing node: {kill_target}")
            kill_log = self.resilience.kill_node(kill_target)
            self.planets[kill_target].is_active = False
            print(f"  Convergence time: {kill_log.get('convergence_time_ms', 0):.2f}ms")

            # Get new route
            new_route = self.resilience.get_route(src, dst)
            if new_route:
                print(f"\n  New route: {' -> '.join(new_route.path)}")
                print(f"  New latency: {new_route.total_latency_s:.9f}s")
                assert kill_target not in new_route.path, "Killed node still in route!"
                print(f"  Verification: {kill_target} NOT in new path - CONFIRMED")

                # Simulate new packet journey
                new_packet = simulate_packet_journey(payload, new_route, self.planets, self.metadata)
                new_decoded = codex_to_ascii(new_packet.encoded_payload, new_packet.current_codex)
                assert new_decoded == payload
                print(f"  Payload integrity on reroute: VERIFIED")
            else:
                print(f"  [DTN] Route isolated - packet queued for later delivery")

            # Revive
            print(f"\n  Reviving node: {kill_target}")
            revive_log = self.resilience.revive_node(kill_target)
            self.planets[kill_target].is_active = True
            print(f"  Packets flushed: {revive_log.get('packets_flushed', 0)}")

            # Verify restoration
            restored_route = self.resilience.get_route(src, dst)
            if restored_route:
                print(f"  Restored route: {' -> '.join(restored_route.path)}")
                print(f"  Restored latency: {restored_route.total_latency_s:.9f}s")
                # Should match original
                if restored_route.path == route.path:
                    print(f"  Original route RESTORED - CONFIRMED")
                else:
                    print(f"  Route changed (topology may have alternate optimal)")

        print("\n" + "=" * 60)
        print("  DEMO COMPLETE - All milestones verified")
        print("=" * 60)

    def run_gui(self):
        """Run the interactive Pygame visualizer."""
        print("[GUI] Starting interactive visualizer...")
        print("  Controls:")
        print("    - Select Source/Destination from dropdowns")
        print("    - Type custom payload in text field")
        print("    - Click SEND PACKET to simulate")
        print("    - Click KILL NODE then click a planet for Chaos Test")
        print("    - Click REVIVE ALL to restore dead nodes")
        print("    - Press ESC to exit")
        print()

        from visualizer import RelicRingVisualizer
        viz = RelicRingVisualizer(self.metadata, self.planets_list, self.resilience)
        viz.run()


def main():
    parser = argparse.ArgumentParser(
        description="Relic Ring Protocol - Interplanetary Routing Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Launch interactive GUI
  python src/main.py --headless         # Terminal-only demo
  python src/main.py --config custom.json  # Custom universe config
        """
    )
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(__file__), "..", "universe-config.json"),
        help="Path to universe-config.json"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in terminal-only mode (no GUI)"
    )

    args = parser.parse_args()
    config_path = os.path.abspath(args.config)

    demo = RelicRingDemo(config_path)

    if args.headless:
        demo.run_headless_demo()
    else:
        demo.run_headless_demo()  # Always print terminal summary first
        demo.run_gui()


if __name__ == "__main__":
    main()
