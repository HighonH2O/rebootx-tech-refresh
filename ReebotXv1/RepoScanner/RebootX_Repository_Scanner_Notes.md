# RebootX Learning Notes -- Repository Scanner Module

## Role

**Repository Analysis Engineer**

Mission:

> Given an enterprise application's source code, discover everything
> that will be affected by a technology upgrade.

This module is responsible for understanding the repository **without
executing it**.

------------------------------------------------------------------------

# High-Level Goal

The Repository Scanner produces structured facts for the rest of
RebootX.

It does **not** call the LLM.

It performs:

-   Repository traversal
-   Static code analysis
-   Dependency extraction
-   Technology detection
-   Configuration analysis
-   Dependency graph generation
-   Risk tagging

Output is a structured JSON consumed by downstream services.

------------------------------------------------------------------------

# Expected Repository Scan Report

The scanner should identify:

## Languages

-   Python
-   Java
-   SQL
-   Shell
-   YAML
-   JSON
-   XML

## Frameworks

-   FastAPI
-   Spring Boot
-   Django
-   Flask

## Dependencies

-   pandas
-   numpy
-   cx_Oracle
-   pyspark
-   boto3

## Databases

-   Oracle
-   PostgreSQL
-   MySQL

## Cloud Services

-   AWS Glue
-   S3
-   EMR

## Containers

-   Docker
-   Docker Compose

## Configuration Files

-   requirements.txt
-   pyproject.toml
-   Dockerfile
-   application.properties
-   config.yaml

## Potential Upgrade Risks

Examples:

-   cx_Oracle
-   Deprecated Python Runtime
-   Oracle Client Dependencies

------------------------------------------------------------------------

# Repository Scanner Architecture

Repository Scanner

-   File Discovery
-   Language Detector
-   Dependency Extractor
-   Configuration Scanner
-   Database Scanner
-   Cloud Scanner
-   API Scanner
-   Risk Tagger
-   Dependency Graph Builder

Each component has **one responsibility**.

------------------------------------------------------------------------

# Component Breakdown

## 1. File Discovery

Input: - GitHub Repository

Output: - List of all files

Responsibilities:

-   Walk recursively through repository
-   Ignore:
    -   .git
    -   venv
    -   .venv
    -   node_modules
    -   **pycache**

------------------------------------------------------------------------

## 2. Language Detector

Detect language using:

### Extension Based

-   .py → Python
-   .java → Java
-   .sql → SQL
-   .scala → Scala
-   .sh → Shell

### Filename Based

-   Dockerfile
-   Jenkinsfile
-   Makefile

### Content Based

If extension is misleading, inspect file contents.

------------------------------------------------------------------------

## 3. Dependency Extractor

Extract imports from source code.

Examples:

Python imports:

-   pandas
-   numpy
-   cx_Oracle
-   pyspark

Also parse:

-   requirements.txt
-   pyproject.toml

Store:

-   Package Name
-   Version

------------------------------------------------------------------------

## 4. Configuration Scanner

Parse configuration files.

Examples:

-   config.yaml
-   application.properties
-   .env

Detect:

-   Database URLs
-   Hosts
-   Credentials (metadata only)
-   Runtime configurations

------------------------------------------------------------------------

## 5. Database Scanner

Identify database technologies through:

-   cx_Oracle
-   psycopg2
-   sqlalchemy
-   jdbc:oracle
-   mysql.connector

------------------------------------------------------------------------

## 6. Cloud Scanner

Detect cloud integrations.

Examples:

-   boto3
-   AWS Glue
-   Spark
-   S3

------------------------------------------------------------------------

## 7. API Scanner

Detect:

-   REST APIs
-   FastAPI
-   Spring Controllers
-   External API calls

------------------------------------------------------------------------

## 8. Risk Tagger

Apply deterministic rules.

Example:

-   Python 3.8 → Deprecated Runtime
-   cx_Oracle → High Compatibility Risk

No LLM required.

------------------------------------------------------------------------

## 9. Dependency Graph Builder

Example:

customer_etl.py

↓

database.py

↓

cx_Oracle

↓

Oracle Database

This graph enables impact analysis.

------------------------------------------------------------------------

# Static vs Dynamic Analysis

## Static Analysis

Definition:

Analyze source code **without executing it**.

Advantages:

-   Safe
-   Fast
-   Finds dependencies
-   No runtime side effects

## Dynamic Analysis

Definition:

Execute the application to observe runtime behavior.

For RebootX, static analysis is the primary approach.

------------------------------------------------------------------------

# Repository Traversal Pipeline

Repository

↓

Traversal

↓

Ignore Files

↓

Classification

↓

Metadata Extraction

↓

Dependency Extraction

↓

Technology Detection

↓

Dependency Graph

↓

Risk Tags

↓

Structured JSON

------------------------------------------------------------------------

# Folder Structure

repository_scanner/

-   scanner/
    -   traversal.py
    -   classifier.py
    -   parser.py
    -   extractor.py
    -   graph_builder.py
    -   risk_rules.py
-   models/
    -   file.py
    -   dependency.py
    -   repository.py
-   services/
    -   scan_service.py
    -   report_service.py
-   utils/
    -   helpers.py
-   tests/

Each file has one responsibility.

------------------------------------------------------------------------

# JSON Output Contract

``` json
{
  "repository": "CustomerPortal",
  "languages": ["Python", "SQL"],
  "frameworks": ["FastAPI"],
  "dependencies": [
    {
      "name": "cx_Oracle",
      "version": "8.3"
    }
  ],
  "databases": ["Oracle"],
  "cloud_services": ["AWS Glue"],
  "risk_flags": [
    {
      "component": "cx_Oracle",
      "reason": "Potential compatibility issue with Python 3.12"
    }
  ]
}
```

------------------------------------------------------------------------

# Story-001: Repository Discovery Engine

## Objective

Build a component that:

1.  Accepts a repository path.
2.  Traverses recursively.
3.  Ignores:
    -   .git
    -   venv
    -   .venv
    -   node_modules
    -   **pycache**
4.  Classifies every discovered file.
5.  Produces summary JSON.

Example:

``` json
{
  "total_files": 148,
  "python_files": 42,
  "sql_files": 8,
  "shell_scripts": 5,
  "dockerfiles": 2,
  "yaml_files": 4,
  "unknown_files": 87
}
```

------------------------------------------------------------------------

# Learning Roadmap

1.  Repository Discovery
2.  File Classification
3.  Static Code Analysis (AST)
4.  Dependency Extraction
5.  Configuration Analysis
6.  Dependency Graph Construction
7.  Technology Fingerprinting
8.  Compatibility Rule Engine
9.  RebootX Integration

------------------------------------------------------------------------

# Key Architectural Principles

-   One responsibility per component.
-   Prefer static analysis over execution.
-   Produce structured facts, not AI-generated guesses.
-   Use deterministic rules wherever possible.
-   Keep the Repository Scanner independent of the LLM.
-   Design for extensibility so new languages and frameworks can be
    added with minimal changes.

------------------------------------------------------------------------

# Final Takeaway

The Repository Scanner is the foundation of RebootX.

If it extracts accurate facts:

-   The Dependency Graph is correct.
-   The Risk Engine becomes reliable.
-   The LLM reasons over trustworthy evidence.
-   The final report becomes explainable and enterprise-ready.
