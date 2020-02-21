from enum import Enum


class ComponentStatus(Enum):
    OPERATIONAL = 'operational'
    DEGRADED_PERFORMANCE = 'degraded_performance'
    PARTIAL_OUTAGE = 'partial_outage'
    MAJOR_OUTAGE = 'major_outage'
    UNDER_MAINTENANCE = 'under_maintenance'


class IncidentStatus(Enum):
    INVESTIGATING = 'investigating'
    IDENTIFIED = 'identified'
    MONITORING = 'monitoring'
    RESOLVED = 'resolved'


class IncidentImpactOverride(Enum):
    NONE = None
    MINOR = 'minor'
    MAJOR = 'major'
    CRITICAL = 'critical'
