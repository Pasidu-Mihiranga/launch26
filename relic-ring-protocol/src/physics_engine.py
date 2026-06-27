import math
from typing import Tuple, List

# To avoid circular imports or redefining, we can import from config_parser
# (assuming it's in the same directory)
from config_parser import Planet

ROUNDING_PRECISION = 9

def void_distance(p1: Planet, p2: Planet, scale_unit_km: float) -> float:
    """
    Formula 1: Void Distance (L)
    Calculates the straight-line vacuum distance between two planets,
    subtracting their radii and atmospheric thicknesses.
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    center_dist_km = math.sqrt(dx**2 + dy**2) * scale_unit_km
    
    p1_shell = p1.radius_km + p1.atmosphere_thickness_km
    p2_shell = p2.radius_km + p2.atmosphere_thickness_km
    
    L = center_dist_km - p1_shell - p2_shell
    return round(max(L, 0.0), ROUNDING_PRECISION)

def atmosphere_travel_time(p1: Planet, p2: Planet, speed_of_light_kms: float) -> Tuple[float, float, float]:
    """
    Calculates the time spent traveling through the atmosphere of two planets.
    Returns (atm_1_time, atm_2_time, total_atm_time) in seconds.
    """
    C = speed_of_light_kms
    atm_1_time = (p1.atmosphere_thickness_km * p1.refraction_index) / C
    atm_2_time = (p2.atmosphere_thickness_km * p2.refraction_index) / C
    return round(atm_1_time, ROUNDING_PRECISION), round(atm_2_time, ROUNDING_PRECISION), round(atm_1_time + atm_2_time, ROUNDING_PRECISION)

def void_travel_time(p1: Planet, p2: Planet, L: float, speed_of_light_kms: float) -> float:
    """
    Formula 2: Void Travel Time (Tv)
    Calculates the time to travel through p1's atmosphere, the void distance L, 
    and p2's atmosphere. Refraction index slows the signal in the atmosphere.
    Returns time in seconds.
    """
    C = speed_of_light_kms
    atm_1_time, atm_2_time, total_atm_time = atmosphere_travel_time(p1, p2, C)
    void_time = L / C
    
    total_time = total_atm_time + void_time
    return round(total_time, ROUNDING_PRECISION)

def tower_positions(planet: Planet) -> List[Tuple[float, float]]:
    """
    Returns the (x, y) coordinates of all towers relative to the planet's center.
    Towers are placed at equal angular intervals starting from the top (+y axis),
    assigned clockwise.
    """
    N = planet.active_towers
    positions = []
    for i in range(N):
        # Top is 0 degrees. Clockwise means x = sin(angle), y = cos(angle)
        angle_rad = math.radians(i * (360.0 / N))
        tx = planet.radius_km * math.sin(angle_rad)
        ty = planet.radius_km * math.cos(angle_rad)
        positions.append((tx, ty))
    return positions

def get_optimal_tower_index(planet: Planet, dx: float, dy: float) -> int:
    """
    O(1) algorithmic optimization to find the tower facing the target vector.
    Towers are distributed clockwise from the +y axis. 
    math.atan2(dx, dy) computes the angle from the +y axis directly.
    """
    N = planet.active_towers
    angle_rad = math.atan2(dx, dy)
    if angle_rad < 0:
        angle_rad += 2 * math.pi
        
    tower_arc = 2 * math.pi / N
    # Snap to the closest tower slot
    index = math.floor((angle_rad + (tower_arc / 2)) / tower_arc) % N
    return index

def find_closest_tower_pair(p1: Planet, p2: Planet, scale_unit_km: float) -> Tuple[int, int]:
    """
    Line of Sight requirement: The tower pair that minimizes the straight-line 
    void distance between them is used for sending and receiving.
    
    Optimized from O(N^2) brute force to O(1) Angular Vector Projection.
    Returns (p1_tower_index, p2_tower_index).
    """
    # Vector from p1 to p2
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    
    t1 = get_optimal_tower_index(p1, dx, dy)
    t2 = get_optimal_tower_index(p2, -dx, -dy)  # Vector from p2 to p1 is exactly opposite
    
    return (t1, t2)

def crust_transit_time(planet: Planet, entry_tower: int, exit_tower: int, 
                       fiber_fraction: float, speed_of_light_kms: float, 
                       tower_delay_ms: float) -> float:
    """
    Formula 3: Internal Crust Transit Time (Tp)
    Calculates the time spent traveling internally via fiber between the entry and exit tower,
    plus the processing delay at each distinct tower hit.
    Returns time in seconds.
    """
    N = planet.active_towers
    raw_diff = abs(exit_tower - entry_tower)
    
    # Route via the shorter arc
    s = min(raw_diff, N - raw_diff)
    
    # Deduplication case: if entry == exit, m=1. Otherwise m=s+1
    m = 1 if s == 0 else s + 1
    
    # Fiber delay (using 2*pi*r / N for a single segment distance)
    arc_distance = s * (2 * math.pi * planet.radius_km / N)
    fiber_speed = fiber_fraction * speed_of_light_kms
    fiber_time = arc_distance / fiber_speed
    
    # Processing delay (convert ms to seconds)
    processing_time = m * (tower_delay_ms / 1000.0)
    
    total_time = fiber_time + processing_time
    return round(total_time, ROUNDING_PRECISION)
