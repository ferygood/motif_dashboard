import streamlit as st
import pandas as pd
from utils.sidebar_filters import sidebar_filters, filter_dataframe
from utils.swarmplot import plot_swarmplot 

@st.cache_data
def load_data():
    df = pd.read_csv("data/df_dashboard.csv", index_col=0)
    df["PVALUE"] = df["PVALUE"].apply(lambda x: f"{x:.2e}")
    return df

df = load_data()

st.title("KRAB-ZNF-related Motifs Features")

filters = sidebar_filters(df)

# Initialize session state variable to hold filtered dataframe or a flag
if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = df

if filters["apply"]:
    st.session_state.filtered_df = filter_dataframe(df, filters)

filtered_df = st.session_state.filtered_df
if filtered_df is df:
    st.write(f"### Total Results: {len(df)} rows")
else:
    st.write(f"### Filtered Results: {len(filtered_df)} rows")

st.dataframe(filtered_df.reset_index(drop=True))

# plot swarmplot
fig = plot_swarmplot(filtered_df)
st.plotly_chart(fig, use_container_width=True)