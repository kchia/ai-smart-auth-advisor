# Parable Technical Interview

This repository contains data analytics and AI workflow exploration for Parable's technical interview, focusing on SSO audit log analysis to drive employee productivity improvements.

## Interview Focus

- **Data Analytics**: Analyzing Okta SSO audit logs to identify productivity patterns
- **AI Workflow**: Building AI-powered solutions based on SSO login data
- **System Design**: End-to-end architecture from application design to productionalization

## Project Structure

```
parable-interview/
├── data/
│   ├── raw_fixture.json          # 18 Okta SSO audit log records (anonymized)
│   └── parsed_data.json          # Parsed version with expanded nested JSON
├── docs/
│   ├── data-analytics/           # Data exploration & analysis docs
│   │   ├── data_dictionary.md    # Comprehensive field documentation
│   │   ├── key_statistics.md     # Dataset statistics
│   │   ├── hypotheses.md         # Productivity hypotheses
│   │   └── time_usage_metrics.md # Time usage analysis
│   └── system-design/            # Architecture & design docs
│       ├── data_privacy.md       # Privacy considerations
│       ├── parable_context.md    # Company context & tech stack
│       └── production_scale_reality.md
├── scripts/
│   ├── parse_data.py             # Data parsing & exploration
│   └── generate_statistics.py   # Statistical analysis
├── logs/                          # Script outputs
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
└── .gitignore                    # Git ignore rules
```

## Quick Start

### 1. Set Up Python Environment

```bash
# Ensure you're using Python 3.11+
python --version

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- **Data Analysis**: pandas, numpy, scipy
- **Visualization**: matplotlib, seaborn, plotly
- **Machine Learning**: scikit-learn
- **AI/LLM**: OpenAI, LangChain, tiktoken
- **Development**: JupyterLab, IPython, Black
- **Utilities**: rich, tqdm, python-dotenv

### 3. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your key from: https://platform.openai.com/api-keys
```

**Important**: Never commit your `.env` file to version control!

### 4. Explore the Data

```bash
# Run existing scripts
python scripts/parse_data.py
python scripts/generate_statistics.py

# Or start a Jupyter notebook for interactive exploration
jupyter lab
```

## Data Overview

- **Dataset**: 18 Okta SSO audit log records
- **Users**: 10 unique users (anonymized)
- **Applications**: 11 unique apps
- **Date Range**: April 1, 2025
- **Key Fields**: `actor`, `target`, `outcome`, `published`, `raw_data`

### Key Assumptions

From the interview brief:

- Perfect SSO data coverage (all work app logins go through Okta)
- Login sessions last 1 working day
- Each app usage per day generates 1 audit log entry
- Focus on productivity improvements, not SSO implementation

## Productivity Hypotheses

Some areas to explore in the data:

1. **App Switching Patterns**: Frequent context switching reducing productivity
2. **Login Friction**: Authentication overhead in daily workflows
3. **Tool Consolidation**: Opportunities to reduce app sprawl
4. **Usage Patterns**: Identifying underutilized or redundant tools
5. **Temporal Analysis**: Peak usage times, workflow sequences

## Available Scripts

### `scripts/parse_data.py`

Parses the raw Okta audit logs and expands nested JSON data.

```bash
python scripts/parse_data.py
```

### `scripts/generate_statistics.py`

Generates basic statistics about users, apps, and outcomes.

```bash
python scripts/generate_statistics.py
```

## Development Tips

### Code Formatting

```bash
# Format your code before the interview
black scripts/
```

### Interactive Analysis

```bash
# Start Jupyter Lab for live exploration
jupyter lab

# Or use IPython for a better REPL
ipython
```

### Quick Data Load

```python
import json
import pandas as pd

# Load parsed data
with open('data/parsed_data.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame(data)
```

## Interview Preparation Checklist

- [ ] Install all dependencies (`pip install -r requirements.txt`)
- [ ] Set up OpenAI API key in `.env`
- [ ] Review data dictionary (`docs/data-analytics/data_dictionary.md`)
- [ ] Explore the sample data (`data/parsed_data.json`)
- [ ] Test your IDE setup and tools
- [ ] Prepare questions about Parable's tech stack
- [ ] Think about productivity hypotheses
- [ ] Review system design considerations

## Resources

- **Parable Context**: See `docs/system-design/parable_context.md`
- **Data Dictionary**: See `docs/data-analytics/data_dictionary.md`
- **Privacy Considerations**: See `docs/system-design/data_privacy.md`
- **Okta API Docs**: [Okta System Log API](https://developer.okta.com/docs/reference/api/system-log/)

## Notes

- This is an **open book** interview - use AI tools, search, and previous work
- Screen sharing will be required
- Pre-written code is allowed but not required
- Focus on problem-solving and system thinking, not memorization
