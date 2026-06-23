# Project Overview

This project was developed as an end-to-end analytics solution for the Nova SuperApp ecosystem, covering the complete data lifecycle from raw data ingestion to business intelligence dashboards and machine learning-based fraud detection.

The solution combines modern data engineering, analytics engineering, business intelligence, and machine learning practices to transform large-scale transactional data into actionable business insights.

---

## Technology Stack

| Layer                              | Technology         |
| ---------------------------------- | ------------------ |
| Data Warehouse                     | BigQuery           |
| Analytics Engineering              | dbt                |
| Data Processing & Machine Learning | Python             |
| Notebook Environment               | Jupyter Notebook   |
| Business Intelligence              | Tableau            |

---

## End-to-End Data Pipeline

### 1. Data Storage & Processing (BigQuery)

The project utilizes Google BigQuery as the central cloud data warehouse.

Raw transactional, user, and service datasets are stored and processed in BigQuery, allowing scalable analysis on millions of records.

Responsibilities:

•⁠  ⁠Raw data storage
•⁠  ⁠Large-scale SQL processing
•⁠  ⁠Analytical data modeling
•⁠  ⁠Machine learning data extraction

---

### 2. Data Transformation (dbt)

dbt (Data Build Tool) was used to build a modular and maintainable transformation layer.

The data model follows a layered architecture:

#### Staging Layer

Raw data cleaning and standardization.

Examples:

•⁠  ⁠stg_users
•⁠  ⁠stg_services
•⁠  ⁠stg_interactions

#### Intermediate Layer

Business logic implementation and metric calculations.

Examples:

•⁠  ⁠Service health metrics
•⁠  ⁠Risk metrics
•⁠  ⁠Repeat behavior calculations

#### Mart Layer

Business-ready aggregated tables designed specifically for reporting and analytics.

Examples:

•⁠  ⁠mart_service_monthly_performance
•⁠  ⁠mart_service_repeat_behavior
•⁠  ⁠mart_category_market_performance

Benefits:

•⁠  ⁠Reusable SQL models
•⁠  ⁠Version-controlled transformations
•⁠  ⁠Scalable analytics workflow
•⁠  ⁠Documentation and lineage support

---

### 3. Development Environment (Visual Studio Code) --remove

Visual Studio Code was used as the primary development environment.

Activities performed:

•⁠  ⁠dbt model development
•⁠  ⁠SQL transformations
•⁠  ⁠Git version control
•⁠  ⁠Branch management
•⁠  ⁠Project collaboration

---

### 4. Machine Learning & Fraud Detection (Python + Jupyter Notebook)

Machine learning workflows were developed using Python in Jupyter Notebook.

The notebook environment was used for:

•⁠  ⁠Data exploration
•⁠  ⁠Feature engineering
•⁠  ⁠Statistical analysis
•⁠  ⁠Fraud detection modeling
•⁠  ⁠Model evaluation

#### Fraud Detection Approach

Since no labeled fraud dataset was available, an Unsupervised Learning approach was selected.

Algorithm used:

*Isolation Forest*

Generated features included:

•⁠  ⁠Transaction amount
•⁠  ⁠Transaction frequency
•⁠  ⁠Spending behavior
•⁠  ⁠Time-based activity patterns
•⁠  ⁠User transaction history
•⁠  ⁠Cross-market behavior
•⁠  ⁠Failed and refunded transactions

Model output:

•⁠  ⁠Fraud Anomaly Score
•⁠  ⁠Is Anomaly Flag

The model identifies transactions that significantly deviate from normal customer behavior patterns.

---

### 5. Business Intelligence & Visualization (Tableau)

Final analytical outputs were visualized using Tableau.

Interactive dashboards were developed to support executive-level decision making.

Key dashboards include:

#### Category Performance Intelligence

Focus Areas:

•⁠  ⁠Revenue contribution
•⁠  ⁠Risk exposure
•⁠  ⁠Service quality
•⁠  ⁠Growth opportunities

#### Customer Repeat & Risk Intelligence

Focus Areas:

•⁠  ⁠Customer loyalty
•⁠  ⁠Repeat revenue dependency
•⁠  ⁠Fraud risk monitoring
•⁠  ⁠Market-level anomaly analysis

Dashboard Features:

•⁠  ⁠Interactive filters
•⁠  ⁠KPI cards
•⁠  ⁠Drill-down analysis
•⁠  ⁠Comparative benchmarking
•⁠  ⁠Executive-level visual storytelling

---

## Business Value

This project demonstrates a complete modern analytics workflow by integrating:

•⁠  ⁠Cloud Data Warehousing
•⁠  ⁠Analytics Engineering
•⁠  ⁠Machine Learning
•⁠  ⁠Fraud Detection
•⁠  ⁠Business Intelligence

The resulting solution enables stakeholders to make data-driven decisions regarding:

•⁠  ⁠Category performance optimization
•⁠  ⁠Customer retention strategies
•⁠  ⁠Operational risk management
•⁠  ⁠Fraud detection and monitoring
•⁠  ⁠Growth opportunity identification

Through this architecture, raw transactional data is transformed into scalable analytical assets and actionable business insights.