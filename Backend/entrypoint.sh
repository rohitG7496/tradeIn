#!/bin/bash
set -e

# Execute the CMD instruction passed by Dockerfile
exec "$@"
