library(spatialLIBD)
library(SummarizedExperiment)

# Download spot-level DLPFC SpatialExperiment object
spe <- fetch_data(type = "spe")

# Keep sample 151673
sample_id <- "151673"
spe_sub <- spe[, spe$sample_id == sample_id]

# Extract metadata
meta <- as.data.frame(colData(spe_sub))

# Create output folder
out_dir <- "data/dlpfc_151673_raw/exported_from_R"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# Save all metadata columns first so we can inspect them
write.csv(meta, file.path(out_dir, "metadata_all_columns.csv"), row.names = FALSE)

# Save available column names
writeLines(colnames(meta), file.path(out_dir, "metadata_column_names.txt"))

# Extract expression matrix.
# Use logcounts if available; otherwise use counts.
assay_names <- assayNames(spe_sub)
writeLines(assay_names, file.path(out_dir, "assay_names.txt"))

if ("logcounts" %in% assay_names) {
  expr <- assay(spe_sub, "logcounts")
} else {
  expr <- assay(spe_sub, "counts")
}

# Use top 200 highly variable genes if column exists; otherwise first 200 genes.
row_meta <- as.data.frame(rowData(spe_sub))
write.csv(row_meta, file.path(out_dir, "gene_metadata_all_columns.csv"), row.names = FALSE)

if ("is_top_hvg" %in% colnames(row_meta)) {
  keep_genes <- rownames(spe_sub)[row_meta$is_top_hvg]
  keep_genes <- keep_genes[1:min(200, length(keep_genes))]
} else {
  keep_genes <- rownames(spe_sub)[1:200]
}

expr_small <- as.matrix(expr[keep_genes, ])
expr_small_df <- as.data.frame(t(expr_small))
expr_small_df$spot_id <- rownames(expr_small_df)
expr_small_df <- expr_small_df[, c("spot_id", setdiff(colnames(expr_small_df), "spot_id"))]
write.csv(expr_small_df, file.path(out_dir, "expression_matrix_small.csv"), row.names = FALSE)

cat("Export complete for sample", sample_id, "\n")
cat("Number of spots:", ncol(spe_sub), "\n")
cat("Number of genes exported:", length(keep_genes), "\n")
cat("Metadata columns written to metadata_column_names.txt\n")
