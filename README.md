# Sigma: Risk-Adjusted Quantitative Trading Engine for Hypixel Bazaar

This is a full-stack quantitative analysis tool and trading dashboard designed for the Hypixel Skyblock's high-frequency virtual commodity market, the Bazaar. This project implements a real-time data pipeline, statistical modeling (Sharpe Ratios, Alpha Scoring), and a Streamlit-based terminal to identify high-probability profit opportunities.

Data is requested from the [Hypixel Public API](https://api.hypixel.net/) network every minute
Requested data is then inserted into the bazaar.db database, located in ./data(a new database is created when run for the first time)
Website is resynced with new data every minute(local to your device) while main.py is running
1800+ items are automatically filtered and sorted to display top 10 current trades. 
Real-time Plotly charts showcase buy/sell spread trends and historical volatility.

## Core Methodology
Sigma treats the bazaar as a true financial market, using:
Risk-Adjusted Returns: Implements rolling Sharpe Ratios to weigh potential profit against price volatility, wheras traditional "flip finders" are easily influenced by sudden changes in margin and are prone to displaying risky trades. 
Alpha Scoring: A proprietary 70/30 weighted metric combining Projected Profit Per Hour (PPH) and Normalized Sharpe Ratios to rank trades.
Market Velocity Analysis: Uses time-series derivatives to calculate real-time trade throughput, providing precise recent market activity not influenced by activity days prior.

## Tech Stack/Dependencies
Language: Python 3.10+
Data Science: NumPy, Pandas (Statistical modeling & Vectorized data processing)
Engineering: SQLite (Time-series data persistence), Requests (REST API integration)
Frontend: Streamlit & Plotly (Visualization/interactive frontend)

## Base Logic:
Expected Profit: $E[Profit] = (\text{Buy Price} \times 0.9875) - \text{Sell Price}$ 
Sharpe Ratio: $S = \frac{\mu_{margin}}{\sigma_{margin}}$, where $\sigma$ is the standard error of the trade margin over a 12-hour window.



## Getting Started
### Environment Setup.
Clone the repository and initialize a Python virtual environment to manage dependencies:

Clone the repository(Bash)
```
git clone https://github.com/Omilyfewd/Sigma.git
cd Sigma
```

Create and activate a virtual environment
```
python -m venv venv
```
On Windows:
```
.\venv\Scripts\activate
```
On macOS/Linux:
```
source venv/bin/activate
```

Install required dependencies
```
pip install -r requirements.txt
```

### Launch the Data Pipeline.
You must start the data collector to start populating, or download(and extract) and replace the existing bazaar.db with sample data found [here](https://drive.google.com/file/d/1lieeaMuYN1dzP_b8M6Y_Eav_EFJNKV7n/view?usp=sharing):

```
python src/main.py
```
Note: Ensure the data/ folder exists in your project root, as the DatabaseManager expects this directory.

### Launch the Dashboard
In a separate terminal window (with the venv activated), run the Streamlit application to visualize market insights:

```
streamlit run src/dashboard.py
```

The dashboard will be available at http://localhost:8501.

Lawrence's Tip: For optimal results, allow main.py to run for at least 10–15 minutes to generate the historical data required for rolling Sharpe Ratio calculations.

### Get To Flipping💰!!!
Log onto Skyblock, reference the webpage, and start placing your buy/sell orders!
