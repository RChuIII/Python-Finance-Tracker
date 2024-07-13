# Python-Finance-Tracker
## Description

A self hosted finance tracker to help visualize cash flow. Built in Python with Streamlit.

## Usage

To use this repository, simply clone it to your local machine:
```bash
git clone https://github.com/RChuIII/Python-Finance-Tracker
```

You can run the program in two different ways:
```bash
streamlit run pyFinanceTrackerWebapp.py
```
or using docker:
```bash
docker build -t pynance-tracker .;
docker run -dt -v /path/to/app/:/app -p 6900:6900 --name pynance-tracker pynance-tracker
```

Access the webapp on:
```bash
localhost:6900
```
you can change the port in `.streamlit/config.toml` or, if you are using docker change: `-p [PORT YOU WANT]:6900`
