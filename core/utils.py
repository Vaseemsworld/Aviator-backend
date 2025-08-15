import random
from decimal import Decimal
from django.conf import settings

# Default weighted probability distribution
DEFAULT_CRASH_DISTRIBUTION = [
    (0.50, (1.00, 2.00)),     # 50% chance
    (0.80, (2.00, 5.00)),     # 30% chance
    (0.95, (5.00, 10.00)),    # 15% chance
    (0.995, (10.00, 50.00)),  # 4.5% chance
    (1.00, (50.00, 200.00)),  # 0.5% chance
]

def generate_crash_point(seed: str = None) -> Decimal:
    """
    Generates a crash point similar to Spribe's Aviator style.
    Optional seed for reproducibility.
    """
    if seed:
        random.seed(seed)  # For provably fair mode or testing

    distribution = getattr(settings, "CRASH_DISTRIBUTION", DEFAULT_CRASH_DISTRIBUTION)

    roll = random.random()
    for threshold, (low, high) in distribution:
        if roll < threshold:
            return Decimal(str(round(random.uniform(low, high), 2)))

    return Decimal("1.00")
