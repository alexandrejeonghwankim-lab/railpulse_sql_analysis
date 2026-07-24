SELECT COUNT(*) AS scheduled_visits, platform_code
FROM stop_times
JOIN stops on stop_times.stop_id = stops.stop_id 
WHERE stop_name ='Bruxelles-Central' AND platform_code IS NOT NULL 
GROUP BY platform_code
ORDER BY scheduled_visits DESC
LIMIT 3;
