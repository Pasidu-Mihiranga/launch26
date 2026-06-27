import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from config_parser import Planet, UniverseMetadata
from physics_engine import (
    void_distance,
    void_travel_time,
    find_closest_tower_pair,
    crust_transit_time
)

@dataclass
class EdgeInfo:
    """Represents a directed edge between two planets in the universe."""
    source_id: str
    dest_id: str
    void_distance_km: float
    void_travel_time_s: float
    source_exit_tower: int
    dest_entry_tower: int

@dataclass
class NetworkGraph:
    """The network graph representing the connectivity and details of the planets."""
    metadata: UniverseMetadata
    planets: Dict[str, Planet] = field(default_factory=dict)
    adjacency: Dict[str, List[EdgeInfo]] = field(default_factory=dict)

def build_network_graph(metadata: UniverseMetadata, planets: List[Planet]) -> NetworkGraph:
    """
    Builds the adjacency graph from the list of planets.
    Only active planets are included.
    Pre-filters edges where the void distance exceeds max_void_hop_distance_km (Lmax).
    """
    graph = NetworkGraph(metadata=metadata)
    
    # Store all planets by their ID
    for planet in planets:
        graph.planets[planet.id] = planet
        graph.adjacency[planet.id] = []
        
    # We only build connections between active planets
    active_planets = [p for p in planets if p.is_active]
    
    S = metadata.coordinate_scale_unit_km
    C = metadata.speed_of_light_kms
    Lmax = metadata.max_void_hop_distance_km
    
    # Create directed edges for every pair of active planets
    for p1 in active_planets:
        for p2 in active_planets:
            if p1.id == p2.id:
                continue
                
            # Compute void distance L
            L = void_distance(p1, p2, S)
            
            # Pre-filter using Lmax boundary condition
            if L > Lmax:
                continue
                
            # Calculate void travel time Tv
            Tv = void_travel_time(p1, p2, L, C)
            
            # Find the closest tower pair for sending and receiving
            t1_exit, t2_entry = find_closest_tower_pair(p1, p2, S)
            
            edge = EdgeInfo(
                source_id=p1.id,
                dest_id=p2.id,
                void_distance_km=L,
                void_travel_time_s=Tv,
                source_exit_tower=t1_exit,
                dest_entry_tower=t2_entry
            )
            graph.adjacency[p1.id].append(edge)
            
    return graph

def find_bridge_nodes(graph: NetworkGraph) -> List[str]:
    """
    Identifies 'bridge' nodes (cut vertices) whose removal increases the number of connected components
    of the currently active subnetwork.
    Uses BFS connectivity checks for simplicity and correctness on this small graph size.
    """
    active_node_ids = [pid for pid, p in graph.planets.items() if p.is_active]
    
    # If there are fewer than 3 active nodes, removing one cannot disconnect the rest
    if len(active_node_ids) < 3:
        return []
        
    bridges = []
    
    for candidate in active_node_ids:
        # Build the set of nodes that should be reachable if candidate is removed
        remaining_nodes = [nid for nid in active_node_ids if nid != candidate]
        if not remaining_nodes:
            continue
            
        start_node = remaining_nodes[0]
        visited = set()
        queue = [start_node]
        visited.add(start_node)
        
        while queue:
            curr = queue.pop(0)
            for edge in graph.adjacency.get(curr, []):
                # Skip the candidate node and any inactive nodes
                if edge.dest_id == candidate:
                    continue
                dest_planet = graph.planets.get(edge.dest_id)
                if dest_planet and dest_planet.is_active and edge.dest_id not in visited:
                    visited.add(edge.dest_id)
                    queue.append(edge.dest_id)
                    
        # If BFS cannot reach all remaining active nodes, candidate is a bridge node
        if len(visited) < len(remaining_nodes):
            bridges.append(candidate)
            
    return bridges
