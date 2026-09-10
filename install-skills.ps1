# Deprecated wrapper - use: node bin/cli.js install
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
node (Join-Path $root "bin\cli.js") $(if ($args[0]) { $args[0] } else { "skills" })
