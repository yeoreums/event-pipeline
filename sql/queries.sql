-- 1. Event count by type
SELECT event_type, COUNT(*) AS count
FROM events
GROUP BY event_type
ORDER BY count DESC;

-- 2. Hourly event trend
SELECT DATE_TRUNC('hour', timestamp) AS hour, COUNT(*) AS count
FROM events
GROUP BY hour
ORDER BY hour;

-- 3. Top users by event count
SELECT user_id, COUNT(*) AS count
FROM events
GROUP BY user_id
ORDER BY count DESC
LIMIT 10;