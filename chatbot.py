import teradatasql
import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# OpenAI API key
openai.api_key = "" 
# Function to connect to the Teradata database
def connect_to_db():
    try:
        connection = teradatasql.connect(
            host="", # host 
            user="", # username 
            password="", # password
            database="" #db name
        )
        return connection
    except Exception as e:
        return f"Error connecting to the database: {e}"

# Function to retrieve database schema
def get_database_schema(connection):
    schema_query = """
    SELECT 
        TableName, 
        ColumnName, 
        ColumnType
    FROM 
        DBC.ColumnsV
    WHERE 
        DatabaseName = 'SC';  -- Ensure to replace 'SC' with your database name
    """
    cursor = connection.cursor()
    cursor.execute(schema_query)
    schema_data = cursor.fetchall()
    cursor.close()
    
    schema_description = "Database Schema:\n"
    table_columns = {}
    for table_name, column_name, column_type in schema_data:
        if table_name not in table_columns:
            table_columns[table_name] = []
        table_columns[table_name].append(f"{column_name} ({column_type})")
    
    for table_name, columns in table_columns.items():
        schema_description += f"Table: {table_name}\n"
        schema_description += f"  Columns: {', '.join(columns)}\n"
    
    return schema_description

# Generate SQL query dynamically using GPT
def generate_dynamic_sql(prompt, schema):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[ 
                {"role": "system", "content": (
                    "You are an expert SQL assistant. Generate syntactically correct Teradata SQL queries. "
                    "Ensure all table names include the database name as a prefix (e.g., sc.teacher). "
                    "For string comparisons, use UPPER(column_name) = UPPER(value) to ensure case-insensitivity. "
                    "Do not add 'sql' or any other unnecessary words in the query."
                )},
                {"role": "system", "content": schema},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        sql_query = response["choices"][0]["message"]["content"]
        sql_query = sql_query.replace("`", "").strip()
        if not sql_query.endswith(";"):
            sql_query += ";"
        return sql_query
    
    except Exception as e:
        return f"Error generating SQL query: {str(e)}"

# Execute the generated SQL query
def execute_dynamic_query(user_request):
    connection = connect_to_db()
    if not connection or isinstance(connection, str):
        return connection, None

    schema = get_database_schema(connection)
    sql_query = generate_dynamic_sql(user_request, schema)
    
    if sql_query.startswith("Error"):
        return sql_query, None
    
    cursor = connection.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results_df = pd.DataFrame(results, columns=columns)
        return sql_query.strip(), results_df
    
    except Exception as e:
        return f"Error executing the SQL query: {e}\n\nGenerated SQL Query:\n{sql_query}", None
    finally:
        cursor.close()
        connection.close()

# Streamlit interface
def streamlit_interface():
    st.title("Ask your Teradata SQL Chatbot")
    user_request = st.text_input("Enter your request (e.g., 'Find the average sales by region')")

    if user_request:
        sql_query, query_results = execute_dynamic_query(user_request)
        
        if sql_query.startswith("Error"):
            st.error(sql_query)
        else:
            st.subheader("Generated SQL Query")
            st.code(sql_query)

            if query_results is not None and not query_results.empty:
                st.subheader("Query Results")
                st.dataframe(query_results)

                # Chart Customization Section
                st.subheader("Customize Your Chart")

                # Row and Column Selection
                row_column_options = query_results.columns
                x_axis = st.selectbox("Select the column for the X-axis:", row_column_options)
                y_axis = st.selectbox("Select the column for the Y-axis:", row_column_options)

                # Chart Type Selection
                chart_type = st.radio(
                    "Select the chart type:",
                    options=["Bar Chart", "Line Chart", "Area Chart", "Pie Chart"]
                )

                # Render the Chart
                if x_axis and y_axis:
                    chart_data = query_results[[x_axis, y_axis]].dropna()

                    if chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
                        chart_data.set_index(x_axis, inplace=True)

                        if chart_type == "Bar Chart":
                            st.bar_chart(chart_data)
                        elif chart_type == "Line Chart":
                            st.line_chart(chart_data)
                        elif chart_type == "Area Chart":
                            st.area_chart(chart_data)
                    
                    elif chart_type == "Pie Chart":
                        # Pie chart requires grouping by categories
                        pie_data = chart_data.groupby(x_axis)[y_axis].sum()
                        
                        # Generate the pie chart
                        fig, ax = plt.subplots()
                        ax.pie(
                            pie_data, 
                            labels=pie_data.index, 
                            autopct='%1.1f%%', 
                            startangle=90
                        )
                        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
                        st.pyplot(fig)

if __name__ == "__main__":
    streamlit_interface()
