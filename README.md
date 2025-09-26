# Polymarket LMSR Simulator

A Python-based simulation tool designed to explore the mechanics of Automated Market Makers (AMMs) in prediction markets, with a focus on the **Logarithmic Market Scoring Rule (LMSR)**. The application provides an interactive web interface implemented with **Gradio**.

---

## Features

- **Configurable Liquidity Parameter ($\mathbf{b}$):** Adjust the $\mathbf{b}$ parameter to study its effect on market depth and price sensitivity.  
- **Initial Price Bias:** Define the initial market odds (e.g., 30% or 70%) to simulate scenarios with prior beliefs or pre-existing information.  
- **Trading Simulation:** Execute "BUY YES" or "BUY NO" transactions and observe the resulting price adjustments (slippage).  
- **Dynamic Visualization:** Monitor price evolution in real time using a Matplotlib chart that updates after each trade.  
- **Inventory Tracking:** Track cumulative contracts sold ($q_O$ and $q_N$) and the automated market maker’s current position.  

---

## Getting Started

### 1. Prerequisites

- Python version 3.7 or higher.  

### 2. Clone the Repository

```bash
git clone https://github.com/YourUsername/polymarket-lmsr-simulator.git
cd polymarket-lmsr-simulator
```

### 3. Install Dependencies

Install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Launch the simulator:

```bash
python main.py
```

The application will open in your browser at `http://127.0.0.1:7860/`.

---

## Application Overview

### 1. Market Setup and Initial Conditions

Users can configure the liquidity parameter ($\mathbf{b}$) and the initial price before the market begins.  

**[Placeholder: Screenshot of the Gradio interface showing configuration sliders for $\mathbf{b}$ and initial price.]**

### 2. Trading and Price Evolution

The simulator records and visualizes market activity, including trades, price trajectories, and inventory changes.  

**[Placeholder: Screenshot of the interface displaying the price chart and trade history after several transactions.]**

---

## Project Structure

The simulator separates the user interface from the core LMSR logic for modularity.  

```
/polymarket-simulator/
├── README.md               # Documentation (this file)
├── requirements.txt        # Dependencies (Gradio, Matplotlib, etc.)
├── main.py                 # Gradio interface and simulation management
└── src/
    └── lmsr_market.py      # Core LMSR implementation: cost function, pricing, and inventory
```

---

## LMSR Mechanics (Overview)

The **Logarithmic Market Scoring Rule (LMSR)** is an automated market maker mechanism designed for prediction markets.  

The **cost function** is defined as:

$$
C(\mathbf{q}) = b \cdot \ln \left( \sum_{i} e^{q_i / b} \right)
$$

where:
- $\mathbf{q}$ denotes the vector of outstanding shares for each outcome,  
- $b$ is the liquidity parameter.  

The **price of outcome $i$** is derived as the partial derivative of the cost function with respect to $q_i$:  

$$
P_i = \frac{e^{q_i / b}}{\sum_j e^{q_j / b}}
$$

**Interpretation:**
- Smaller values of $b$ lead to higher price sensitivity (low liquidity).  
- Larger values of $b$ yield greater liquidity but require more capital to move prices.  

This formulation ensures **bounded loss** for the market maker while allowing continuous price adjustment.  

---

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.  

---

## Contributing

Contributions are welcome. Potential areas include extending functionality, improving the user interface, or enhancing documentation. Please open an issue or submit a pull request to propose changes.  

---

## Acknowledgments

- Inspired by **Polymarket** and Robin Hanson’s foundational research on automated market makers.  
- Developed using [Gradio](https://gradio.app/) for the interface and [Matplotlib](https://matplotlib.org/) for visualization.  
