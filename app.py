import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objs as go

# ---------- SETTINGS ----------
CSV_PATH = "data/znfs_genes_correlation_forNetwork.csv"  # Update as needed
# ------------------------------

st.set_page_config(layout="wide")
st.title("Gene Regulatory Network")

# Load CSV
df = pd.read_csv(CSV_PATH, index_col=0)

# Sidebar filters on landing page
st.markdown("### Filters")
col1, col2 = st.columns(2)

with col1:
    coef_direction = st.selectbox("Correlation direction", ["both", "positive", "negative"], index=0)

with col2:
    exp_filter = st.selectbox("Expression type", ["both", "up-regulated", "down-regulated"], index=0)

# Apply filters
if coef_direction == "positive":
    df = df[df["coef"] > 0]
elif coef_direction == "negative":
    df = df[df["coef"] < 0]

if exp_filter != "both":
    df = df[df["exp"] == exp_filter]

# Build main graph with signed weights
G = nx.Graph()

for _, row in df.iterrows():
    gene = row['KRAB-ZNF']
    te = row['Gene']
    coef = row['coef']
    exp = row['exp']

    G.add_node(gene, type='gene')
    G.add_node(te, type='te', exp=exp)
    G.add_edge(gene, te, weight=coef)

# Build a separate graph with positive weights for layout
G_pos_weight = nx.Graph()
for u, v, d in G.edges(data=True):
    G_pos_weight.add_edge(u, v, weight=abs(d['weight']))

# Use kamada_kawai_layout for clearer layout (fallback to spring_layout if needed)
try:
    pos = nx.kamada_kawai_layout(G_pos_weight)
except:
    pos = nx.spring_layout(G_pos_weight, seed=42)

# custom colors
custom_red = '#C41E3A'
custom_blue = "#5073F8"

# Edges
edge_trace = []
for u, v, d in G.edges(data=True):
    color = custom_red if d['weight'] > 0 else custom_blue # set color
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_trace.append(
        go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines',
            line=dict(width=2, color=color),
            hoverinfo='text',
            text=f'{u} ↔ {v}<br>coef={d["weight"]:.2f}',
            showlegend=False
        )
    )

# Nodes
node_x, node_y, node_text = [], [], []
node_color, node_border_color = [], []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

    if G.nodes[node]['type'] == 'gene':
        node_color.append('orange')
        node_border_color.append('black')
    else:
        node_color.append('lightgreen')
        exp = G.nodes[node].get('exp', 'up')
        node_border_color.append(custom_red if exp == 'up-regulated' else custom_blue)

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    text=node_text,
    textposition="top center",
    hoverinfo='text',
    marker=dict(
        size=15,
        color=node_color,
        line=dict(width=3, color=node_border_color)
    ),
    textfont=dict(
        color='black'
    )
)

# Plot
fig = go.Figure(data=edge_trace + [node_trace])
fig.update_layout(
    title='Correlation Network',
    showlegend=False,
    margin=dict(l=40, r=40, t=40, b=40),
    hovermode='closest',
    width=700,
    height=700,
    plot_bgcolor='rgba(0,0,0,0)',   # transparent background
    paper_bgcolor='rgba(0,0,0,0)',  # transparent paper background
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        visible=False
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        visible=False
    )
)

st.plotly_chart(fig, use_container_width=True)

# Display data table
st.markdown('### Correlation Table')
st.dataframe(df.reset_index(drop=True))
