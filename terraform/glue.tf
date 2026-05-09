resource "aws_glue_catalog_database" "lakehouse" {
  name        = var.glue_database_name
  description = "Glue Data Catalog database for HarborWatch lakehouse tables."
}
