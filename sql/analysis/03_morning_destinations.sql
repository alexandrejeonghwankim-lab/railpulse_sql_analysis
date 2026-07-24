-- Question 3: Find the top three most frequent terminal destinations
-- for trips whose first scheduled departure occurs before noon.
WITH first_stop AS 
(
SELECT 
    trip_id,
    MIN(stop_sequence) AS first_stop_sequence
FROM stop_times
GROUP BY trip_id
),

trip_departure AS (
    SELECT
        stop_times.trip_id,
        trips.trip_headsign,
        CAST(
            SUBSTR(stop_times.departure_time, 1, 2)
            AS INTEGER
        ) % 24 AS departure_hour
    FROM first_stop
    JOIN stop_times
        ON stop_times.trip_id = first_stop.trip_id 
        AND stop_times.stop_sequence = first_stop.first_stop_sequence 
    JOIN trips 
        ON stop_times.trip_id = trips.trip_id
)

SELECT trip_headsign, COUNT(*) AS counted_trips
FROM trip_departure
WHERE departure_hour < 12  
GROUP BY trip_headsign
ORDER BY counted_trips DESC 
LIMIT 3;
