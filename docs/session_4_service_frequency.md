# Session 4 — Service Frequency

## Question

Classify each active service ID into a weekly frequency category:

- **High Frequency:** operates 5 or more days per week
- **Medium Frequency:** operates 2–4 days per week
- **Low Frequency/Special:** operates fewer than 2 days per week or operates irregularly

The final result must show the percentage of active services in each category.

## Data problem

The normal GTFS weekly schedule is stored in `calendar.txt`, which was imported into the `services` table. However, all weekday columns from Monday through Sunday contain zero in this dataset.

Those columns therefore cannot be used to calculate the real weekly frequency.

The workaround uses `calendar_dates.txt`, imported as `service_exceptions`. Each row with `exception_type = 1` identifies a date on which a service operates.

## Definition of an active service

For this analysis, an active service is defined as:

> A `service_id` referenced by at least one scheduled trip in the `trips` table.

This is implemented with:

```sql
SELECT DISTINCT service_id
FROM trips
```

The database contains:

- 51,593 service IDs in `services`
- 51,593 service IDs in `service_exceptions`
- 17,288 service IDs referenced by `trips`
- 34,305 service IDs without a corresponding scheduled trip

Only the 17,288 service IDs connected to scheduled trips are included in the final classification.

## Query process

### 1. Find active service IDs

The `active_service` CTE selects distinct service IDs from `trips`.

Using `DISTINCT` is important because one service can be connected to many trips. Joining raw trip rows directly to exception dates would multiply the data.

### 2. Find operating dates

The `service_datefinder` CTE joins the active service IDs to `service_exceptions` and retains rows where:

```sql
exception_type = 1
```

These rows represent dates when a service operates.

### 3. Count active days per week

The `weekly_activity` CTE converts every ISO date into a year-and-week value:

```sql
STRFTIME('%Y-%W', exception_date)
```

The year is included so that the same week number in different years is not combined.

Rows are grouped by:

- `service_id`
- active year/week

The number of operating days is calculated with:

```sql
COUNT(DISTINCT exception_date)
```

Using `DISTINCT` prevents duplicate service-date records from increasing the count.

### 4. Calculate one weekly frequency per service

A service can have different numbers of active days in different weeks. For example, it could operate three days in one week and five days in another.

The `average_active` CTE calculates:

```sql
AVG(active_days_in_week)
```

This produces one average number of active days per week for every active service ID.

The average is not rounded before classification. Rounding first could incorrectly classify a value such as `4.6` as High Frequency.

### 5. Classify each service

A searched `CASE WHEN` expression applies the categories:

```sql
CASE
    WHEN average_days_per_week >= 5
        THEN 'High frequency'
    WHEN average_days_per_week < 2
        THEN 'Low frequency/special'
    ELSE 'Medium frequency'
END
```

The `ELSE` branch covers averages from 2 up to, but not including, 5.

### 6. Calculate category percentages

The number of services in each category is calculated with:

```sql
COUNT(*)
```

The total number of classified services is calculated as a window aggregate:

```sql
SUM(COUNT(*)) OVER ()
```

The percentage is:

```sql
100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()
```

`100.0` is used to ensure decimal division. The result is rounded to two decimal places for display.

## Final results

| Frequency category | Number of services | Percentage |
|---|---:|---:|
| Medium frequency | 10,835 | 62.67% |
| Low frequency/special | 6,046 | 34.97% |
| High frequency | 407 | 2.35% |

The category counts total 17,288 active service IDs.

The displayed percentages total 99.99% because each category percentage is rounded to two decimal places.

## Why another analysis may produce different results

An analysis that includes all 51,593 IDs from `services` or `service_exceptions` will produce a different total. It includes 34,305 service IDs that are not referenced by any scheduled trip.

Results can also differ if the calculation:

- counts all dates across the complete schedule period instead of counting days within each week;
- applies `CASE` before producing one frequency value per service;
- does not remove duplicate dates;
- treats partial first or last weeks differently;
- rounds the weekly average before classification.

The definition of an active service and the weekly-frequency method must therefore be stated with the results.

## Limitations

The first and last week of a service may be partial weeks. Including partial weeks in the average can reduce the calculated weekly frequency.

The method also depends on `calendar_dates.txt` because the regular weekday flags in `calendar.txt` are unusable in this dataset. The results describe the supplied GTFS schedule and should not be interpreted as a permanent description of SNCB service patterns.

## Saved SQL

The final query is available in:

```text
sql/analysis/04_service_frequency.sql
```
