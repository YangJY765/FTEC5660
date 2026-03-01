Credits & Origin
This project is a reproduction and engineering optimization of the Original Repository [https://github.com/HKUDS/AI-Trader].
   Major Overrides implemented in this version:
        WSL2/Linux network compatibility patches.
        Gemini-2.5-Flash multimodal response handling.
        Liquidity-constrained prompt engineering.



AI-Trader: LLM-Driven Quantitative Agent (Gemini-2.5-Flash)

📋 Executive Summary
This project evaluates an autonomous quantitative trading agent powered by Gemini-2.5-Flash. The system utilizes a Decoupled Microservice Architecture (FastMCP) to integrate a suite of tools including Alpha Vantage news retrieval, local historical price databases, and a reasoning-based execution engine. The core objective is to replicate the agent's ability to synthesize unstructured news data with numerical price trends to manage a high-volatility portfolio (NVDA) over a backtesting window.


## 📁 Key File Overrides & Modifications
This project involves critical patches to the base repository to ensure stability in the WSL2 environment and compatibility with Gemini-2.5-Flash.

* `configs/default_config.json`:
    * **Mod:** Aligned backtest dates (Oct-Nov 2025) to match local CSV data availability.
    * **Mod:** Switched ticker scope to single-asset (`NVDA`) for volatility stress-testing.

* `agent/base_agent/base_agent.py`:
    * **Fix:** Injected type-casting logic (`str()`) in the response parser to handle multimodal List objects returned by Gemini-2.5, preventing `TypeError`.

* `agent_tools/tool_trade.py`:
    * **Fix:** Replaced unsafe dictionary lookups with `.get()` methods to prevent `KeyError: CASH` crashes during uninitialized state loops.

* `agent_tools/tool_get_price_local.py`:
    * **Fix:** Added `datetime.fromisoformat()` normalization layer to resolve date format mismatches between LLM queries (ISO) and CSV (YYYY-MM-DD).

* `env`:
    * **Fix:** Add:
        MODEL_NAME="gemini-2.5-flash"
        OPENAI_API_MODEL="gemini-2.5-flash"
        CHAT_MODEL="gemini-2.5-flash"
        SIGNATURE="gemini-2.5-flash"

🚀 Execution Flow
    Follow this exact sequence to replicate the results:

      Clone & Sanitize: Rebuild a native Linux venv inside WSL.

      Apply Patches: Replace the files listed in the "Pre-Execution Patching" section above.

      Launch Service Layer: Run python3 agent_tools/ in Terminals.

      Launch Reasoning Layer: Run python3 main.py in a new Terminal.

⚙️ Experimental Setup
  ·Core Logic: Multi-step ReAct planning loop.
  ·Infrastructure: WSL2 (Ubuntu 22.04), Python 3.12.
  ·Data Layer: Local CSV serialization for LocalPrices to ensure high I/O determinism.
  ·Model: Gemini-2.5-Flash (Temperature=0, Max\_Tokens=2048).
  ·Protocol: Model Context Protocol (MCP) for tool binding.


🛠️ Installation & Environment
To avoid binary compatibility issues observed in cross-platform migrations (Windows/WSL), follow these specific build steps:
 
 1. Clean environment build (Crucial for WSL)
    # Clone the repository
       git clone <this-repo-link>
       cd AI-Trader

    # IMPORTANT: Remove any Windows-created venv and rebuild natively in WSL
        rm -rf venv
        python3.12 -m venv venv
        source venv/bin/activate

    # Upgrade pip and install dependencies
        pip install --upgrade pip
        pip install -r requirements.txt


 2. Configuration Injection
    Export API keys to the environment. Do not hardcode these in the source.
        GEMINI_API_KEY="your_google_api_key"
        ALPHAVANTAGE_API_KEY="your_alphavantage_key"


🛠️ Pre-Execution Patching & Overrides
Before launching the main.py backtest, the following critical patches must be applied to the base repository to ensure compatibility with WSL2 and the Gemini-2.5-Flash multimodal response structure.

  1. Core Logic & Multimodal Defense
  File: agent/base_agent/base_agent.py

  Patch: Injected a type-casting wrapper str(msg.content) in the tool response parser.

  2. Data Schema Alignment
  File: agent_tools/tool_get_price_local.py

  Patch: Integrated datetime.fromisoformat() for timestamp normalization.
  Resolves the format mismatch between the LLM-generated ISO strings and the YYYY-MM-DD keys indexed in the local data/daily_prices_NVDA.json database.

  3. Robust State Management
  File: agent_tools/tool_trade.py

  Patch: Replaced direct dictionary indexing (pos['CASH']) with defensive .get() methods (positions.get('CASH', 0)) to prevent KeyError.

  4. Configuration Synchronization
  File: configs/default_config.json

  Patch: Synchronized start_date and end_date with the local NVDA historical dataset. Prevents "Data Not Found" errors by ensuring the backtest window (Oct 01 – Nov 07, 2025).

  5. `env`:
      Add:
        MODEL_NAME="gemini-2.5-flash"
        OPENAI_API_MODEL="gemini-2.5-flash"
        CHAT_MODEL="gemini-2.5-flash"
        SIGNATURE="gemini-2.5-flash"


🚀 Running the Backtest (Multi-Terminal Flow)
The system uses a Decoupled Terminal Architecture to prevent I/O blocking between the Tool Server and the Reasoning Agent.

Step 1: Initialize the Tool Server 
This hosts the FastMCP microservices for trading, price retrieval, and news search.

    Procedure: Open five separate terminal windows.

    Terminal 1: The Tool Server (Service Layer)
                Role: Math tool.
                Status: Must remain active throughout the backtest.
          # Activate environment
              source venv/bin/activate
          # Launch the tool service
              python3 agent_tools/tool_math.py
        
    Terminal 2: The Tool Server (Service Layer)
          # Activate environment
              source venv/bin/activate
          # Launch the tool service
              python3 agent_tools/tool_alphavantage_news.py

    Terminal 3: The Tool Server (Service Layer)
          # Activate environment
              source venv/bin/activate
          # Launch the tool service
              python3 agent_tools/tool_trade.py

    Terminal 4: The Tool Server (Service Layer)
          # Activate environment
              source venv/bin/activate
          # Launch the tool service
              python3 agent_tools/tool_get_price_local.py

    Terminal 5: The Tool Server (Service Layer)
          # Activate environment
              source venv/bin/activate
          # Launch the tool service
              python3 agent_tools/tool_crypto_trade.py


🛠️ Core Backtest Agent
    # Open a new terminal window
    Terminal 6: Execute Backtest
          # Activate environment
              source venv/bin/activate
          # Launch the main.py
              python3 main.py

🛠️ Modification Experiment
    Update the following system prompt in the agent_promt.py
    **IMPORTANT RULES **
      1. API FALLBACK: If the News tool fails or returns empty, you MUST switch to Technical Analysis immediately. Do NOT default to "Hold".
      2. MANDATORY TOOL: You are REQUIRED to call `tool_trade.py` in every single step to verify trends.
      3. LIQUIDITY: If Cash < $200, you MUST actively look for SELL signals (e.g., High RSI) to free up cash. Do not just sit on a full position.
    # Execute Backtest again
         python3 main.py

📊 Performance Metrics (Triple-Run Average)
    There are metrics to evaluate the results: Final Value, CR, SR, MDD, Vol

    Comparison between Baseline Group and Reference
      Metric	                Baseline 	Reference 	Delta (Δ)
      Cumulative Return (CR)	-0.54%	    -0.06%	    -0.48%
      Max Drawdown (MDD)	    9.04%	    7.73%	    +1.31%
      Volatility(Vol)	        36.64%	    22.06%	    +14.58%
      Sortino Ratio (SR)	    0.06	    0.09	    -0.03

    Baseline vs. Optimized Results (Oct 01 - Nov 07, 2025)
      Metric	                Baseline(Mean)	Experimental    Delta
      Final Portfolio Value	    $9,945.67	      $10,272.19	+$326.52
      Cumulative Return (CR)	-0.54%	          +2.72%	    +3.26%
      Max Drawdown (MDD)	    9.04%	          6.24%     	-31.0%
      Volatility(Vol)	        36.64%	          28.35%	    -22.6%
      Sortino Ratio(SR)	        0.06	          1.44	        +1.38

📂 Repository Structure
.
├── agent/               # Core reasoning logic and base_agent overrides
├── agent_tools/         # FastMCP microservices (News, Price, Trade)
├── configs/             # JSON configuration for backtest windows
├── data/                # Local CSV price databases (NVDA)
├── logs/                # Execution logs from the 3 independent runs
├── positions.jsonl      # Real-time state-machine tracking
└── README.md            # You are here

📝 Technical Debug 

If you encounter a Port already in use error for 8000-8005, a previous session may have left "zombie" processes. 
    #Clear them:
        pkill -9 -f python

Network Resilience (Blocker 3): Resolved WSL DNS resolution failures (/etc/resolv.conf) which caused an "Information Blind Spot," resulting in a $417 variance in final equity.

Structural Parsing (Blocker 7): Implemented a type-casting defense in base_agent.py to handle Gemini-2.5-Flash's occasional structured List responses, preventing TypeError during multimodal inference.

State Integrity (Blocker 6): Replaced direct dictionary indexing with defensive .get() methods in positions.jsonl to ensure the agent loop survives uninitialized asset states.


