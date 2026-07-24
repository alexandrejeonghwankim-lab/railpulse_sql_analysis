-- Question 4: Classify active services by their average weekly frequency
-- and show the percentage of services in each category.

WITH active_service AS (
    SELECT DISTINCT service_id
    FROM trips
),

service_datefinder AS (
    SELECT
        service_exceptions.service_id,
        exception_date
    FROM service_exceptions
    JOIN active_service
        ON active_service.service_id = service_exceptions.service_id
    WHERE exception_type = 1
),

weekly_activity AS (
    SELECT
        service_id,
        STRFTIME('%Y-%W', exception_date) AS active_week,
        COUNT(DISTINCT exception_date) AS active_days_in_week
    FROM service_datefinder
    GROUP BY
        service_id,
        active_week
),

average_active AS (
    SELECT
        service_id,
        AVG(active_days_in_week) AS average_days_per_week
    FROM weekly_activity
    GROUP BY service_id
)

SELECT
    CASE
        WHEN average_days_per_week >= 5
            THEN 'High frequency'
        WHEN average_days_per_week < 2
            THEN 'Low frequency/special'
        ELSE 'Medium frequency'
    END AS frequency,
    COUNT(*) AS number_of_services,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_services
FROM average_active
GROUP BY frequency
ORDER BY percentage_of_services DESC;
