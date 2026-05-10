resource "aws_sfn_state_machine" "lakehouse_pipeline" {
  name     = "${local.name_prefix}-lakehouse-pipeline"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "HarborWatch AWS lakehouse pipeline orchestration"
    StartAt = "RawToBronze"
    States = {
      RawToBronze = {
        Type     = "Task"
        Resource = "arn:aws:states:::glue:startJobRun.sync"
        Parameters = {
          JobName = aws_glue_job.raw_to_bronze.name
        }
        Next = "BronzeToSilverClean"
      }

      BronzeToSilverClean = {
        Type     = "Task"
        Resource = "arn:aws:states:::glue:startJobRun.sync"
        Parameters = {
          JobName = aws_glue_job.bronze_to_silver_clean.name
        }
        Next = "SilverToPortProximity"
      }

      SilverToPortProximity = {
        Type     = "Task"
        Resource = "arn:aws:states:::glue:startJobRun.sync"
        Parameters = {
          JobName = aws_glue_job.silver_to_port_proximity.name
        }
        Next = "PortProximityToVesselStops"
      }

      PortProximityToVesselStops = {
        Type     = "Task"
        Resource = "arn:aws:states:::glue:startJobRun.sync"
        Parameters = {
          JobName = aws_glue_job.port_proximity_to_vessel_stops.name
        }
        End = true
      }
    }
  })
}
