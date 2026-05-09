# Local MVP Results

## Dataset

Source file: `AIS_2024_01_01.zip`

Full source profile:

- Total records scanned: 7,296,275
- Rejected records: 16,875
- Full-file rejection rate: 0.2313%

Random sample used for analytical outputs:

- Sample size: 500,000 records
- Valid records: 498,874
- Rejected records: 1,126
- Random sample rejection rate: 0.2252%

## Data Quality Results

Rejected records in the random sample:

- speed_not_available: 1,121
- impossible_speed: 3
- duplicate_message_id: 2

Severity distribution:

- low: 1,121
- medium: 5

## Port Proximity Results

Vessels and AIS positions within 20 km of MVP ports:

- Houston: 302 distinct vessels, 15,110 AIS positions
- Los Angeles / Long Beach: 324 distinct vessels, 9,730 AIS positions
- New York / New Jersey: 300 distinct vessels, 12,295 AIS positions
- Savannah: 79 distinct vessels, 2,804 AIS positions
- Seattle / Tacoma: 711 distinct vessels, 20,629 AIS positions

## Vessel Stop Results

Detected stop episodes:

- Houston: 945 stops, 279 stopped vessels, 211.16 average dwell minutes
- Los Angeles / Long Beach: 1,078 stops, 272 stopped vessels, 126.38 average dwell minutes
- New York / New Jersey: 783 stops, 257 stopped vessels, 183.93 average dwell minutes
- Savannah: 235 stops, 64 stopped vessels, 167.32 average dwell minutes
- Seattle / Tacoma: 2,516 stops, 614 stopped vessels, 121.13 average dwell minutes

## Gold Port Congestion Results

Final local Gold table:

| Port | Vessels Near Port | Stopped Vessels | Avg Dwell Minutes | P90 Dwell Minutes | Stopped Position Count | Anomaly Count | Port Congestion Index |
|---|---:|---:|---:|---:|---:|---:|---:|
| Houston | 302 | 279 | 211.16 | 494.16 | 13,400 | 0 | 0.6649 |
| Los Angeles / Long Beach | 324 | 272 | 126.38 | 254.97 | 8,856 | 2 | 0.2635 |
| New York / New Jersey | 300 | 257 | 183.93 | 428.91 | 9,834 | 44 | 0.4906 |
| Savannah | 79 | 64 | 167.32 | 339.20 | 2,610 | 13 | 0.1796 |
| Seattle / Tacoma | 711 | 614 | 121.13 | 228.02 | 19,626 | 23 | 0.6500 |

## Interpretation

Houston and Seattle / Tacoma ranked highest in the sample-based Port Congestion Index.

This result should be interpreted as a relative score within the selected random sample and MVP ports, not as a definitive real-world congestion ranking.
