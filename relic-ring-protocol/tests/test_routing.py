import sys
import os
import pytest

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config_parser import load_universe_config
from graph_builder import build_network_graph, find_bridge_nodes

@pytest.fixture
def universe_data():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../universe-config.json'))
    meta, planets = load_universe_config(config_path)
    return meta, planets

def test_graph_builder_lmax_filtering(universe_data):
    meta, planets = universe_data
    graph = build_network_graph(meta, planets)
    
    assert len(graph.planets) == 6
    
    Lmax = meta.max_void_hop_distance_km
    for source_id, edges in graph.adjacency.items():
        for edge in edges:
            assert edge.void_distance_km <= Lmax, \
                f"Edge {edge.source_id} -> {edge.dest_id} exceeds Lmax ({edge.void_distance_km} > {Lmax})"

def test_graph_builder_edges(universe_data):
    meta, planets = universe_data
    graph = build_network_graph(meta, planets)
    
    # Verify Aegis (0, 0) and Boreas (150, 100) are connected
    aegis_edges = graph.adjacency.get("Aegis", [])
    aegis_to_boreas = [e for e in aegis_edges if e.dest_id == "Boreas"]
    assert len(aegis_to_boreas) == 1
    edge = aegis_to_boreas[0]
    
    assert edge.source_id == "Aegis"
    assert edge.dest_id == "Boreas"
    assert edge.void_distance_km > 0
    # Towers should be valid indices
    assert 0 <= edge.source_exit_tower < graph.planets["Aegis"].active_towers
    assert 0 <= edge.dest_entry_tower < graph.planets["Boreas"].active_towers

def test_bridge_nodes(universe_data):
    meta, planets = universe_data
    graph = build_network_graph(meta, planets)
    
    # Find bridges in the default active graph
    bridges = find_bridge_nodes(graph)
    # Just verify it returns a list (may or may not contain bridges depending on topology connectivity)
    assert isinstance(bridges, list)
    for b in bridges:
        assert b in graph.planets
