-- Write and test your Question 1 SQL here.

WITH leaving_time AS(
SELECT CAST(SUBSTR(departure_time, 1,2) AS INTEGER)%24 AS onlyhour
FROM stop_times 
)

SELECT onlyhour, COUNT(onlyhour) AS departure_count
FROM leaving_time
GROUP BY onlyhour
ORDER BY departure_count DESC
LIMIT 3;
