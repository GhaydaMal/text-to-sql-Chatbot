# text-to-sql-Chatbot

## Project Overview
The Teradata SQL Chatbot is a Streamlit-based application powered by OpenAI's GPT. It transforms natural language prompts into SQL queries, connects to a Teradata database, and visualizes query results through tables and customizable charts — making data analysis seamless and accessible.

## Features
**Database Schema Retrieval:** Automatically fetches the database schema to guide GPT in generating accurate SQL queries.
**Dynamic SQL Query Generation:** Leverages OpenAI's GPT-4 to generate syntactically correct Teradata SQL queries based on user prompts.
**Query Execution:** Connects to Teradata, executes the generated SQL queries, and returns results in a tabular format.
**Data Visualization:** Enables users to visualize query results with customizable charts (Bar, Line, Area, and Pie Charts).

## Usage
**Run the Application:**
- streamlit run app.py

**User Interface:**
1. Enter your natural language request in the text input (e.g., "Show total sales per region") and press Enter.
2. View the generated SQL query and corresponding query results in the output section.
3. Use the chart customization section to select chart types and customize X and Y axes.

## Dependencies
- teradatasql
- openai
- streamlit
- pandas
- matplotlib
