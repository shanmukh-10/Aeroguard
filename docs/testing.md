# AeroGuard Testing Plan & Quality Assurance

## 1. Test Architecture
The test suite spans Unit, Integration, and Regression tests:
- `tests/test_aqi.py`: CPCB linear interpolation formulas, sub-index breakpoints, and multi-pollutant maximum rules.
- `tests/test_preprocessing.py`: Data loading, timestamp sorting, physical bound constraints, and time-aware linear interpolation limit.
- `tests/test_ml.py`: Lag feature calculation, cyclical sine/cosine encoders, model artifact loading, and multi-horizon inference.
- `tests/test_api.py`: FastAPI REST routes, query parameter handling, schema validation, and status codes.
- `tests/test_iot_ingestion.py`: Sensor telemetry payload ingestion, rejection of out-of-range inputs, and automated alert triggering.

## 2. Executing Automated Tests

```bash
# Run complete test suite with verbose output
pytest tests/ -v
```
