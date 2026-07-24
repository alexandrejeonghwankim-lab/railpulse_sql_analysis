-- Question 5: Calculate the ratio and percentage of scheduled trips per
-- route that explicitly guarantee wheelchair accessibility or bicycle
-- accommodation, and identify the routes with the lowest documented score.

WITH trip_features AS (
    SELECT
        t.route_id,
        r.route_short_name,
        r.route_long_name,
        t.bikes_allowed,
        t.wheelchair_accessible,
        CASE
            WHEN r.route_short_name = 'BUS'
                THEN 'Bus service'
            ELSE 'Train service'
        END AS service_type
    FROM trips AS t
    JOIN routes AS r
        ON t.route_id = r.route_id
),

route_amenities AS (
    SELECT
        route_id,
        route_short_name,
        route_long_name,
        service_type,
        COUNT(*) AS total_trips,
        SUM(
            CASE
                WHEN bikes_allowed = 1 THEN 1
                ELSE 0
            END
        ) AS bike_guaranteed_trips,
        SUM(
            CASE
                WHEN bikes_allowed IS NULL THEN 1
                ELSE 0
            END
        ) AS bike_unknown_trips,
        SUM(
            CASE
                WHEN wheelchair_accessible = 1 THEN 1
                ELSE 0
            END
        ) AS wheelchair_guaranteed_trips,
        SUM(
            CASE
                WHEN wheelchair_accessible IS NULL THEN 1
                ELSE 0
            END
        ) AS wheelchair_unknown_trips,
        SUM(
            CASE
                WHEN wheelchair_accessible = 1
                  OR bikes_allowed = 1
                    THEN 1
                ELSE 0
            END
        ) AS amenity_guaranteed_trips
    FROM trip_features
    GROUP BY
        route_id,
        route_short_name,
        route_long_name,
        service_type
)

SELECT
    route_id,
    route_short_name,
    route_long_name,
    service_type,
    total_trips,
    bike_guaranteed_trips,
    bike_unknown_trips,
    wheelchair_guaranteed_trips,
    wheelchair_unknown_trips,
    amenity_guaranteed_trips,
    amenity_guaranteed_trips || '/' || total_trips
        AS amenity_guarantee_ratio,
    ROUND(
        100.0 * amenity_guaranteed_trips / total_trips,
        2
    ) AS amenity_guarantee_percentage
FROM route_amenities
ORDER BY
    amenity_guarantee_percentage ASC,
    total_trips DESC;
