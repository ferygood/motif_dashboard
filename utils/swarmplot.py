import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_swarmplot(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["midpoint"] = (df["START"] + df["END"]) / 2

    chrom_order = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
    chrom_present = [c for c in chrom_order if c in df["CHROM"].unique()]
    df["CHROM"] = pd.Categorical(df["CHROM"], categories=chrom_present, ordered=True)

    fig = px.strip(
        df,
        x="midpoint",
        y="CHROM",
        orientation="h",
        hover_data=df.columns,
        stripmode="overlay"
    )
    fig.update_traces(jitter=0.3)  # apply jitter to avoid overlap
    fig.update_layout(
        title="Distribution of Midpoints by Chromosome",
        yaxis=dict(categoryorder="array", categoryarray=chrom_present)
    )
    return fig
