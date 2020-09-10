import math


def calc_distance(a, b):
    """Calculate distance in km."""

    if "longitude" not in a or "longitude" not in b:
        return 1000000

    return haversine_distance(a["latitude"], a["longitude"], b["latitude"], a["longitude"]) / 1000.0


# https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def haversine_distance(lat1, lon1, lat2, lon2):
    """
        Calculate the Haversine distance.

        Returns
        -------
        distance_in_meters : float

        Examples
        --------
        >>> # From Munich
        >>> # to Berlin
        >>> round(haversine_distance(48.1372, 11.5756, 52.5186, 13.4083), 1)
        504358.2
        """
    earth_radius = 6372800  # Earth radius in meters

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * earth_radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
