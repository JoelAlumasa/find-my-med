# andasy.hcl app configuration file generated for find-my-med on Monday, 24-Nov-25 16:41:31 CAT
#
# See https://github.com/quarksgroup/andasy-cli for information about how to use this file.

app_name = "find-my-med"

app {

  env = {}

  port = 8501

  compute {
    cpu      = 1
    memory   = 256
    cpu_kind = "shared"
  }

  process {
    name = "find-my-med"
  }

}
