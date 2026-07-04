# Crisis stress tests (expanded 14-asset)

Best config = minimum-variance base + vol-targeting + turbulence overlay + continuous
time-series momentum tilt. Leak-safe walk-forward, net of costs. SPY and equal-weight
shown as references.

## Total return through crisis windows

| Window | SPY (buy & hold) | Equal-weight | Strategy (base) | Strategy (+momentum) |
|---|---|---|---|---|
| GFC aftershock / Euro crisis (2011) | -15.7% | -6.4% | -0.4% | -0.5% |
| 2015-16 China / oil rout | -13.1% | -10.2% | -1.5% | -1.4% |
| 2018 Q4 selloff | -19.2% | -8.2% | -0.5% | -0.5% |
| COVID crash (peak->trough) | -35.4% | -21.9% | -3.2% | -2.5% |
| 2022 bear (rates shock) | -25.8% | -15.7% | -9.3% | -8.1% |
| 2026 Iran war oil shock | -5.1% | 0.2% | -0.3% | -0.3% |

## Max drawdown within crisis windows

| Window | SPY (buy & hold) | Equal-weight | Strategy (base) | Strategy (+momentum) |
|---|---|---|---|---|
| GFC aftershock / Euro crisis (2011) | -19.5% | -8.8% | -1.5% | -1.8% |
| 2015-16 China / oil rout | -13.2% | -10.9% | -2.0% | -2.0% |
| 2018 Q4 selloff | -19.8% | -9.1% | -1.1% | -1.0% |
| COVID crash (peak->trough) | -35.7% | -23.4% | -4.5% | -3.7% |
| 2022 bear (rates shock) | -26.2% | -16.6% | -9.4% | -8.3% |
| 2026 Iran war oil shock | -7.8% | -3.0% | -0.9% | -0.7% |

Note: a contemporaneous/short-horizon signal cushions but cannot fully dodge
2-week crashes (COVID), and the 2022 rates shock — where bonds and equities fell
together — is the hardest regime. The strategy gives up upside in sharp recoveries.
