# Official CPCB AQI Methodology & Machine Learning Framework

## 1. Indian National Air Quality Index (CPCB) Methodology

The Central Pollution Control Board (CPCB) calculates the National Air Quality Index using an 8-pollutant piecewise linear interpolation sub-index scheme:

$$I_p = I_{low} + \frac{I_{high} - I_{low}}{B_{high} - B_{low}} \times (C_p - B_{low})$$

Where:
- $C_p$: Actual pollutant concentration (24-hr avg for PM2.5, PM10, NO2, SO2, NH3; 8-hr avg for CO, O3).
- $B_{low}, B_{high}$: Breakpoint concentrations enclosing $C_p$.
- $I_{low}, I_{high}$: AQI sub-index range corresponding to $[B_{low}, B_{high}]$.

### Official CPCB Breakpoints Table
| Category | AQI Range | PM2.5 (24h) | PM10 (24h) | NO2 (24h) | SO2 (24h) | CO (8h) | O3 (8h) | NH3 (24h) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Good** | 0 - 50 | 0 - 30 | 0 - 50 | 0 - 40 | 0 - 40 | 0 - 1.0 | 0 - 50 | 0 - 200 |
| **Satisfactory** | 51 - 100 | 31 - 60 | 51 - 100 | 41 - 80 | 41 - 80 | 1.1 - 2.0 | 51 - 100 | 201 - 400 |
| **Moderate** | 101 - 200 | 61 - 90 | 101 - 250 | 81 - 180 | 81 - 380 | 2.1 - 10 | 101 - 168 | 401 - 800 |
| **Poor** | 201 - 300 | 91 - 120 | 251 - 350 | 181 - 280 | 381 - 800 | 10.1 - 17 | 169 - 208 | 801 - 1200 |
| **Very Poor** | 301 - 400 | 121 - 250 | 351 - 430 | 281 - 400 | 801 - 1600 | 17.1 - 34 | 209 - 748 | 1201 - 1800 |
| **Severe** | 401 - 500 | 250+ | 430+ | 400+ | 1600+ | 34+ | 748+ | 1800+ |

### CPCB AQI Calculation Rule
$$\text{Overall AQI} = \max(I_{\text{PM2.5}}, I_{\text{PM10}}, I_{\text{NO2}}, I_{\text{SO2}}, I_{\text{CO}}, I_{\text{O3}}, I_{\text{NH3}})$$
*Condition: Minimum of 3 pollutants must be monitored, of which at least one must be PM2.5 or PM10.*

---

## 2. Machine Learning Forecasting Architecture

### 2.1 Feature Set (34 Dimensions)
1. **Lags**: $PM_{2.5}(t-1), PM_{2.5}(t-2), PM_{2.5}(t-4), PM_{2.5}(t-8), PM_{2.5}(t-16), PM_{2.5}(t-32), PM_{2.5}(t-96)$
2. **Rolling Statistics**: Rolling Mean & Std over 1-hr, 4-hr, 24-hr windows.
3. **Diurnal & Seasonal Cyclical Transformations**:
   $$\text{hour\_sin} = \sin\left(\frac{2\pi \cdot \text{hour}}{24}\right), \quad \text{hour\_cos} = \cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$$
   $$\text{month\_sin} = \sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \quad \text{month\_cos} = \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$$
4. **Cross-Pollutants & Meteo**: $PM_{10}, NO_2, SO_2, CO, O_3, RH, WS, \text{wd\_sin}, \text{wd\_cos}$.

### 2.2 Models Benchmarked
1. **Persistence Baseline**: $\hat{y}_{t+h} = y_t$
2. **Random Forest Regressor**: Tuned ensemble with residual formulation ($\Delta y$).
3. **PyTorch LSTM**: 2-layer recurrent network with sequence depth = 16 (4 hours).

### 2.3 Evaluation Metrics
- **Mean Absolute Error (MAE)**: $\frac{1}{n}\sum |y_i - \hat{y}_i|$
- **Root Mean Squared Error (RMSE)**: $\sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$
- **Coefficient of Determination ($R^2$)**: $1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$
