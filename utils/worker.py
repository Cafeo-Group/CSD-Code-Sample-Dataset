import multiprocessing
import psutil

def get_optimal_max_workers(buffer: int = 2) -> int:
    """
    Suggests an optimal number of workers based on system specs.
    
    Args:
        buffer (int): Number of cores to leave idle (for system responsiveness).
        
    Returns:
        int: Suggested number of max_workers.
    """
    cpu_count = multiprocessing.cpu_count()
    mem = psutil.virtual_memory()
    
    multiplier = 5 if mem.total >= 8 * 1024**3 else 2
    return max(4, (cpu_count - buffer) * multiplier)
