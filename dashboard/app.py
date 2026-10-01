import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

df = pd.read_csv("data/ONINE_FOOD_DELIVERY_ANALYSIS.csv")


# Page configuration
st.set_page_config(
    page_title="Online Food Delivery Analysis",
    page_icon="🍱",
    layout="wide"
)

st.title(":blue[Online Food Delivery Analysis]", anchor=False)

# Sidebar Filters

st.sidebar.header("Filters")

selected_city = st.sidebar.multiselect(
    "City",
    sorted(df["City"].dropna().unique().tolist()),
    default=sorted(df["City"].dropna().unique().tolist())
)

selected_cuisine = st.sidebar.multiselect(
    "Cuisine",
    sorted(df["Cuisine_Type"].dropna().unique().tolist()),
    default=sorted(df["Cuisine_Type"].dropna().unique().tolist())
)

selected_status = st.sidebar.multiselect(
    "Order Status",
    sorted(df["Order_Status"].dropna().unique().tolist()),
    default=sorted(df["Order_Status"].dropna().unique().tolist())
)

# Field Custom

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

df["Day_of_Week"] = df["Order_Date"].dt.day_name()

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

selected_date = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df.copy()

if selected_city:
    filtered_df = filtered_df[
        filtered_df["City"].isin(selected_city)
    ]

if selected_cuisine:
    filtered_df = filtered_df[
        filtered_df["Cuisine_Type"].isin(selected_cuisine)
    ]

if selected_status:
    filtered_df = filtered_df[
        filtered_df["Order_Status"].isin(selected_status)
    ]

filtered_df = filtered_df[
    (filtered_df["Order_Date"].dt.date >= selected_date[0]) &
    (filtered_df["Order_Date"].dt.date <= selected_date[1])
]

# KPI Calculations

total_orders = len(filtered_df)

delivered_df = filtered_df[
    filtered_df["Order_Status"] == "Delivered"
]

cancelled_orders = (
    filtered_df["Order_Status"] == "Cancelled"
).sum()

total_revenue = delivered_df["Final_Amount"].sum()

average_order_value = filtered_df["Order_Value"].mean()

average_delivery_time = delivered_df["Delivery_Time_Min"].mean()

cancellation_rate = (
    cancelled_orders / total_orders * 100
    if total_orders > 0 else 0
)

average_delivery_rating = delivered_df["Delivery_Rating"].mean()

profit_margin = filtered_df["Profit_Margin"].mean() * 100

total_profit = (
    delivered_df["Final_Amount"] *
    delivered_df["Profit_Margin"]
).sum()

# KPIs

st.subheader("Key Performance Indicators", anchor=False)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col2.metric(
    "Total Revenue",
    f"₹{total_revenue / 1_000_000:.2f} M"
)

col3.metric(
    "Average Order Value",
    f"₹{average_order_value:,.0f}"
)

col4.metric(
    "Average Delivery Time",
    f"{average_delivery_time:.1f} min"
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.2f}%"
)

col6.metric(
    "Average Delivery Rating",
    f"{average_delivery_rating:.2f} / 5"
)

col7.metric(
    "Profit Margin %",
    f"{profit_margin:.2f}%"
)

col8.metric(
    "Total Profit",
    f"₹{total_profit / 1_000_000:.2f} M"
)


df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
df["Order_Month"] = df["Order_Date"].dt.strftime("%b")
month_order = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]
df["Profit_Amount"] = df["Final_Amount"] * df["Profit_Margin"]


filtered_df["Order_Month"] = (
    pd.to_datetime(filtered_df["Order_Date"], errors="coerce")
    .dt.to_period("M")
    .astype(str)
)

filtered_df["Profit_Amount"] = (
    filtered_df["Final_Amount"] * filtered_df["Profit_Margin"]
)

# Monthly Order Trend

monthly_orders = (
    filtered_df
    .dropna(subset=["Order_Date"])
    .assign(
        Month=lambda x: x["Order_Date"].dt.strftime("%b")
    )
    .groupby("Month")
    .size()
    .reset_index(name="Total_Orders")
)

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        monthly_orders["Month"] = pd.Categorical(
            monthly_orders["Month"],
            categories=month_order,
            ordered=True
        )
        monthly_orders = monthly_orders.sort_values("Month")

        fig = px.line(
            monthly_orders,
            x="Month",
            y="Total_Orders",
            markers=True,
            title="Monthly Order Trend"
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Orders",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
# Monthly Revenue & Profit 

with col2:
    with st.container(border=True):
        monthly_revenue = filtered_df.groupby("Order_Month").agg(
        Revenue=("Final_Amount", "sum"),
        Profit=("Profit_Amount", "sum")
        ).reset_index()

        fig = px.bar(
            monthly_revenue,
            x="Order_Month",
            y=["Revenue", "Profit"],
            barmode="group",
            category_orders={
                "Order_Month": month_order
            },
            title="Monthly Revenue & Profit"
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount",
            legend_title="",
            hovermode="x unified",
            # Legend at bottom
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig, use_container_width=True)

# Cancellation Reason Analysis

cancellation_data = (
    filtered_df[
        filtered_df["Order_Status"] == "Cancelled"
    ]
    .groupby("Cancellation_Reason")
    .size()
    .reset_index(name="Cancelled_Orders")
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):

        fig = px.pie(
            cancellation_data,
            names="Cancellation_Reason",
            values="Cancelled_Orders",
            hole=0.4,
            title="Cancellation Reasons"
        )

        fig.update_traces(
            textinfo="percent+label"
        )

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

city_revenue = filtered_df.groupby("City")["Final_Amount"].sum().reset_index()

city_revenue = city_revenue.sort_values(
    by="Final_Amount",
    ascending=False
)
# City Chart

with col2:
    with st.container(border=True):

        fig = px.bar(
            city_revenue,
            x="City",
            y="Final_Amount",
            title="Revenue by City"
        )

        fig.update_layout(
            xaxis_title="City",
            yaxis_title="Revenue",

        )

        st.plotly_chart(fig, use_container_width=True)

# Orders by Day of Week and Month
with st.container(border=True):
    heatmap_data = (
        filtered_df
        .dropna(subset=["Order_Date", "Day_of_Week"])
        .assign(
            Month=lambda x: x["Order_Date"].dt.strftime("%b")
        )
        .groupby(["Month", "Day_of_Week"])
        .size()
        .reset_index(name="Order_Count")
    )

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    fig = px.density_heatmap(
        heatmap_data,
        x="Month",
        y="Day_of_Week",
        z="Order_Count",
        text_auto=True,
        category_orders={
            "Day_of_Week": day_order
        },
        title="Monthly Orders by Day of Week",
        labels={
            "Month": "Month",
            "Day_of_Week": "Day of Week",
            "Order_Count": "Orders"
        }
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Day of Week",
        xaxis=dict(
            dtick=1
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )