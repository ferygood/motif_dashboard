import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import re

# Configure page
st.set_page_config(
    page_title="🧬 Genomic Data Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    .stNumberInput > div > div > input {
        background-color: white;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.experimental_memo
def load_csv_data(file_path=None, uploaded_file=None):
    """Load and process CSV data"""
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        elif file_path and Path(file_path).exists():
            df = pd.read_csv(file_path)
        else:
            # Create sample data if no file provided
            sample_data = {
                'chr': ['chr2', 'chr4', 'chr1', 'chr3', 'chr5'],
                'start': [227070450, 179300015, 123456789, 98765432, 87654321],
                'end': [227070471, 179300036, 123456810, 98765453, 87654342],
                'motif': ['MA1987.1', 'MA1987.1', 'MA1988.2', 'MA1989.3', 'MA1987.1'],
                'strand': ['-', '+', '+', '-', '+'],
                'pvalue': [1.08e-09, 2.38e-09, 3.45e-08, 1.23e-07, 5.67e-09],
                'tefamily': ['HAL1', 'L1PA8A', 'L1PA2', 'AluSx', 'L1PA8A'],
                'class': ['L1', 'L1', 'L1', 'SINE', 'L1'],
                'length': [21, 21, 21, 18, 21],
                'gene': ['SAMPLE1', 'SAMPLE2', 'SAMPLE3', 'SAMPLE4', 'SAMPLE5'],
                'species': ['Human', 'Human', 'Human', 'Human', 'Human']
            }
            df = pd.DataFrame(sample_data)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Standardize column names if needed
        column_mapping = {
            'chromosome': 'chr',
            'te_family': 'tefamily',
            'classification': 'class'
        }
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_columns = ['chr', 'start', 'end', 'motif', 'strand', 'pvalue', 'tefamily', 'class', 'length', 'gene', 'species']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Clean and convert data types
        df['start'] = pd.to_numeric(df['start'], errors='coerce').fillna(0).astype(int)
        df['end'] = pd.to_numeric(df['end'], errors='coerce').fillna(0).astype(int)
        df['pvalue'] = pd.to_numeric(df['pvalue'], errors='coerce').fillna(0)
        df['length'] = pd.to_numeric(df['length'], errors='coerce').fillna(0).astype(int)
        
        # Remove rows with missing essential data
        df = df[(df['chr'] != '') & (df['start'] > 0) & (df['end'] > 0)]
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def natural_sort_chromosomes(chromosomes):
    """Sort chromosomes in natural order (chr1, chr2, ..., chr10, ..., chrX, chrY)"""
    def sort_key(chr_name):
        match = re.match(r'chr(\d+|[XYM])', str(chr_name))
        if match:
            value = match.group(1)
            if value.isdigit():
                return (0, int(value))
            else:
                return (1, value)
        return (2, str(chr_name))
    
    return sorted(chromosomes, key=sort_key)

def filter_data(df, filters):
    """Apply filters to the dataframe"""
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if value and column in filtered_df.columns:
            if column in ['pvalue_max', 'length_min']:
                continue  # Handle these separately
            filtered_df = filtered_df[filtered_df[column] == value]
    
    # Handle numeric filters
    if filters.get('pvalue_max'):
        filtered_df = filtered_df[filtered_df['pvalue'] <= filters['pvalue_max']]
    
    if filters.get('length_min'):
        filtered_df = filtered_df[filtered_df['length'] >= filters['length_min']]
    
    return filtered_df

def create_chromosome_chart(df):
    """Create chromosome distribution chart"""
    if df.empty:
        return go.Figure().add_annotation(text="No data to display", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    # Count hits per chromosome
    chr_counts = df['chr'].value_counts()
    
    # Sort chromosomes naturally
    sorted_chromosomes = natural_sort_chromosomes(chr_counts.index)
    counts = [chr_counts[chr] for chr in sorted_chromosomes]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=sorted_chromosomes,
            y=counts,
            marker=dict(
                color=counts,
                colorscale='Viridis',
                opacity=0.8,
                line=dict(color='rgba(102, 126, 234, 1)', width=2)
            ),
            hovertemplate='<b>%{x}</b><br>Hits: %{y}<br><extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Distribution of Hits by Chromosome",
        xaxis_title="Chromosome",
        yaxis_title="Number of Hits",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=12)
    )
    
    return fig

def main():
    # Header
    st.title("🧬 Genomic Data Interactive Dashboard")
    st.markdown("*Visualize and analyze genomic motif data with advanced filtering and interactive charts*")
    
    # Try to load my.csv automatically
    df = load_csv_data("my.csv")
    
    # Sidebar for filters and file upload
    with st.sidebar:
        st.header("📁 Data Source")
        
        # File upload option
        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=['csv'],
            help="Upload a CSV file to replace the current data"
        )
        
        if uploaded_file is not None:
            df = load_csv_data(uploaded_file=uploaded_file)
            st.success(f"✅ Loaded {len(df)} records from uploaded file")
        elif Path("my.csv").exists():
            st.info(f"📊 Auto-loaded my.csv with {len(df)} records")
        else:
            st.warning("⚠️ Using sample data (my.csv not found)")
        
        st.header("📊 Data Overview")
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Chromosomes", df['chr'].nunique())
            with col3:
                st.metric("Motifs", df['motif'].nunique())
        
        st.header("🔍 Filters")
        
        # Initialize filters
        filters = {}
        
        if not df.empty:
            # Chromosome filter
            chromosomes = [''] + natural_sort_chromosomes(df['chr'].unique())
            filters['chr'] = st.selectbox("Chromosome", chromosomes, index=0)
            
            # Motif filter
            motifs = [''] + sorted(df['motif'].unique())
            filters['motif'] = st.selectbox("Motif", motifs, index=0)
            
            # Strand filter
            strands = ['', '+', '-']
            filters['strand'] = st.selectbox("Strand", strands, index=0)
            
            # Class filter
            classes = [''] + sorted(df['class'].unique())
            filters['class'] = st.selectbox("Class", classes, index=0)
            
            # TE Family filter
            families = [''] + sorted(df['tefamily'].unique())
            filters['tefamily'] = st.selectbox("TE Family", families, index=0)
            
            # Gene filter
            genes = [''] + sorted([g for g in df['gene'].unique() if g])
            filters['gene'] = st.selectbox("Gene", genes, index=0)
            
            # Species filter
            species = [''] + sorted([s for s in df['species'].unique() if s])
            filters['species'] = st.selectbox("Species", species, index=0)
            
            # Numeric filters
            filters['pvalue_max'] = st.number_input(
                "Max P-value",
                min_value=0.0,
                value=0.0,
                format="%.2e",
                help="Filter for p-values less than or equal to this value"
            )
            
            filters['length_min'] = st.number_input(
                "Min Length",
                min_value=0,
                value=0,
                help="Filter for lengths greater than or equal to this value"
            )
            
            # Reset button
            if st.button("🔄 Reset All Filters", use_container_width=True):
                st.rerun()
    
    # Main content area
    if df.empty:
        st.error("No data available. Please upload a CSV file or ensure my.csv exists.")
        return
    
    # Apply filters
    filtered_df = filter_data(df, filters)
    
    # Display filtered stats
    if len(filtered_df) != len(df):
        st.info(f"Showing {len(filtered_df)} of {len(df)} records after filtering")
    
    # Two columns for chart and table
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Distribution Chart")
        chart = create_chromosome_chart(filtered_df)
        st.plotly_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("📋 Data Statistics")
        if not filtered_df.empty:
            stats_data = {
                'Metric': ['Total Records', 'Unique Chromosomes', 'Unique Motifs', 'Avg Length', 'Min P-value', 'Max P-value'],
                'Value': [
                    len(filtered_df),
                    filtered_df['chr'].nunique(),
                    filtered_df['motif'].nunique(),
                    f"{filtered_df['length'].mean():.1f}",
                    f"{filtered_df['pvalue'].min():.2e}",
                    f"{filtered_df['pvalue'].max():.2e}"
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No data matches the current filters")
    
    # Data table
    st.subheader("🗂️ Filtered Data Table")
    
    if not filtered_df.empty:
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['start'] = display_df['start'].apply(lambda x: f"{x:,}")
        display_df['end'] = display_df['end'].apply(lambda x: f"{x:,}")
        display_df['pvalue'] = display_df['pvalue'].apply(lambda x: f"{x:.2e}")
        
        # Rename columns for display
        display_df = display_df.rename(columns={
            'chr': 'CHR',
            'start': 'START',
            'end': 'END',
            'motif': 'MOTIF',
            'strand': 'STRAND',
            'pvalue': 'P-VALUE',
            'tefamily': 'TE FAMILY',
            'class': 'CLASS',
            'length': 'LENGTH',
            'gene': 'GENE',
            'species': 'SPECIES'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="genomic_data_filtered.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data matches the current filters")

if __name__ == "__main__":
    main()
