# sidebar_filters.py
import streamlit as st
import pandas as pd

def sidebar_filters(df):
    st.sidebar.header("Filter Options")

    with st.sidebar.expander("CHROM", expanded=False):
        chrom_filter = st.multiselect(
            "Select CHROM",
            options=sorted(df["CHROM"].dropna().unique()),
            default=[]
        )

    with st.sidebar.expander("MOTIF", expanded=False):
        motif_filter = st.multiselect(
            "Select MOTIF",
            options=sorted(df["MOTIF"].dropna().unique()),
            default=[]
        )

    with st.sidebar.expander("TE", expanded=False):
        te_filter = st.multiselect(
            "Select TE",
            options=sorted(df["TE"].dropna().unique()),
            default=[]
        )

    with st.sidebar.expander("Family ID", expanded=False):
        family_id_filter = st.multiselect(
            "Select Family ID",
            options=sorted(df["FAMILY"].dropna().unique()),
            default=[]
        )

    with st.sidebar.expander("Class ID", expanded=False):
        class_id_filter = st.multiselect(
            "Select Class ID",
            options=sorted(df["CLASS"].dropna().unique()),
            default=[]
        )

    with st.sidebar.expander("Species", expanded=False):
        species_filter = st.multiselect(
            "Select Species",
            options=sorted(df["SPECIES"].dropna().unique()),
            default=[]
        )

    with st.sidebar.expander("Gene", expanded=False):
        gene_filter = st.multiselect(
            "Select Genes",
            options=sorted(df["GENE"].dropna().unique()),
            default=[]
        )

    apply = st.sidebar.button("Apply Filters")

    return {
        "apply": apply,
        "chrom": chrom_filter,
        "motif": motif_filter,
        "te": te_filter,
        "family": family_id_filter,
        "class": class_id_filter,
        "species": species_filter,
        "gene": gene_filter
    }

def filter_dataframe(df, filters):
    filtered_df = df.copy()
    # Apply filters only if selections are made, otherwise don't filter
    if filters["chrom"]:
        filtered_df = filtered_df[filtered_df["CHROM"].isin(filters["chrom"])]

    if filters["motif"]:
        filtered_df = filtered_df[filtered_df["MOTIF"].isin(filters["motif"])]

    if filters["te"]:
        filtered_df = filtered_df[filtered_df["TE"].isin(filters["te"])]

    if filters["family"]:
        filtered_df = filtered_df[filtered_df["FAMILY"].isin(filters["family"])]

    if filters["class"]:
        filtered_df = filtered_df[filtered_df["CLASS"].isin(filters["class"])]

    if filters["species"]:
        filtered_df = filtered_df[filtered_df["SPECIES"].isin(filters["species"])]

    if filters["gene"]:
        filtered_df = filtered_df[filtered_df["GENE"].isin(filters["gene"])]

    return filtered_df
