import sys
import os
import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config_parser import load_universe_config, Planet
from graph_builder import build_network_graph
from resilience_engine import yens_k_shortest_paths, ResilienceManager

@pytest.fixture
def universe_data():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../universe-config.json'))
    meta, planets = load_universe_config(config_path)
    return meta, planets

def test_yens_k_shortest_paths(universe_data):
    meta, planets = universe_data
    graph = build_network_graph(meta, planets)
    
    routes = yens_k_shortest_paths(graph, "Aegis", "Caelum", K=3)
    assert len(routes) > 0
    assert len(routes) <= 3
    
    # Assert loopless paths, unique paths, and sorted by cost
    seen_paths = set()
    prev_cost = -1.0
    for r in routes:
        assert r.is_reachable
        # Loopless
        assert len(r.path) == len(set(r.path))
        # Unique
        path_tuple = tuple(r.path)
        assert path_tuple not in seen_paths
        seen_paths.add(path_tuple)
        # Sorted
        assert r.total_latency_s >= prev_cost
        prev_cost = r.total_latency_s

def test_kill_and_revive_node(universe_data):
    meta, planets = universe_data
    # Create ResilienceManager
    manager = ResilienceManager(meta, planets)
    
    # Get best route before chaos
    route_before = manager.get_route("Aegis", "Caelum")
    assert route_before is not None
    assert route_before.is_reachable
    
    # Pick an intermediate node to kill
    path_nodes = route_before.path
    assert len(path_nodes) > 2, "Path must have at least one intermediate node to test failover"
    kill_target = path_nodes[1]
    
    # Kill the node
    kill_log = manager.kill_node(kill_target)
    assert kill_target in manager.dead_nodes
    assert kill_log["action"] == "kill_node"
    assert kill_log["convergence_time_ms"] >= 0.0
    
    # Get route again and assert it doesn't use the killed node
    route_after = manager.get_route("Aegis", "Caelum")
    assert route_after is not None
    assert route_after.is_reachable
    assert kill_target not in route_after.path
    
    # Revive the node
    revive_log = manager.revive_node(kill_target)
    assert kill_target not in manager.dead_nodes
    assert revive_log["action"] == "revive_node"
    
    # Route again and assert it's restored (should match route_before)
    route_restored = manager.get_route("Aegis", "Caelum")
    assert route_restored is not None
    assert route_restored.path == route_before.path

def test_dtn_queue_and_flush(universe_data):
    meta, planets = universe_data
    manager = ResilienceManager(meta, planets)
    
    # Find all path nodes for Aegis -> Caelum
    route = manager.get_route("Aegis", "Caelum")
    assert route is not None
    
    # Kill all intermediate nodes in that route to ensure isolation
    for node in route.path[1:-1]:
        manager.kill_node(node)
        
    # Get route should fail or be different
    route_isolated = manager.get_route("Aegis", "Caelum")
    
    # If it is still reachable, kill remaining active nodes besides source/dest
    if route_isolated:
        for node in list(manager.all_planets.keys()):
            if node != "Aegis" and node != "Caelum":
                manager.kill_node(node)
                
    # Now it must be isolated since Lmax is 50,000,000 km, and direct Aegis->Caelum is too far
    route_isolated = manager.get_route("Aegis", "Caelum")
    assert route_isolated is None
    
    # Queue a packet
    manager.queue_undeliverable("Aegis", "Caelum", "Test Payload")
    status = manager.get_network_status()
    assert status["pending_packets"] == 1
    
    # Revive the nodes
    for node in list(manager.all_planets.keys()):
        if not manager.all_planets[node].is_active:
            manager.revive_node(node)
            
    # Verify DTN queue is flushed
    status = manager.get_network_status()
    assert status["pending_packets"] == 0
