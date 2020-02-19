from enum import Enum


class ComponentStatus(Enum):
    OPERATIONAL = 'operational'
    DEGRADED_PERFORMANCE = 'degraded_performance'
    PARTIAL_OUTAGE = 'partial_outage'
    MAJOR_OUTAGE = 'major_outage'
    UNDER_MAINTENANCE = 'under_maintenance'
