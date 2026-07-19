#!/bin/bash

# Usage: ./fixallpaths.sh <folder_name>
# This script fixes all file path references in .xsq files

if [ -z "$1" ]; then
  echo "Error: Please provide a folder name"
  echo "Usage: ./fixallpaths.sh <folder_name>"
  exit 1
fi

DIR="$1"

if [ ! -d "$DIR" ]; then
  echo "Error: '$DIR' is not a valid directory"
  exit 1
fi

echo "Scanning $DIR for .xsq files..."

find "$DIR" -maxdepth 1 -type f -name "*.xsq" | while read -r file; do
  echo "Fixing paths in: $file"
  # Create a backup first
  cp "$file" "$file.bak"
  
  # Fix audio file paths
  # Fix typo in username and wrong location
  sed -i '' -E -e 's|/Users/elliottohara/Downloads/|/Users/elliott.ohara/xlights/Audio/|g' "$file"
  sed -i '' -E -e 's|/Users/elliotohara/Google Drive/xLights/2020 Halloween/Audio/|/Users/elliott.ohara/xlights/Audio/|g' "$file"
  # Fix projects path and remove 2022 Christmas subfolder
  sed -i '' -E -e 's|/Users/elliott.ohara/projects/xlights/2022 Christmas/Audio/|/Users/elliott.ohara/xlights/Audio/|g' "$file"
  sed -i '' -E -e 's|/Users/elliott.ohara/projects/xlights/Audio/|/Users/elliott.ohara/xlights/Audio/|g' "$file"
  # Remove Christmas subfolder from audio paths
  sed -i '' -E -e 's|/Users/elliott.ohara/xlights/Christmas/Audio/|/Users/elliott.ohara/xlights/Audio/|g' "$file"
  
  # Fix video file paths - remove Christmas subfolder
  sed -i '' -E -e 's|/Users/elliott.ohara/xlights/Christmas/Videos/|/Users/elliott.ohara/xlights/Videos/|g' "$file"
  sed -i '' -E -e 's|/Users/elliott.ohara/xlights/2022 Christmas/Videos/|/Users/elliott.ohara/xlights/Videos/|g' "$file"
  # Fix typo in username for video paths
  sed -i '' -E -e 's|/Users/elliottohara/Documents/xLights/2022 Christmas/ImportedMedia/|/Users/elliott.ohara/xlights/Christmas/ImportedMedia/|g' "$file"
  
  # Fix shader file paths - remove Christmas subfolder and fix typos
  sed -i '' -E -e 's|/Users/elliott.ohara/xlights/Christmas/Shaders/|/Users/elliott.ohara/xlights/Shaders/|g' "$file"
  sed -i '' -E -e 's|/Users/elliottohara/Documents/xLights/2022 Christmas/Shaders/|/Users/elliott.ohara/xlights/Shaders/|g' "$file"
  
  # Fix image file paths - remove Christmas subfolder
  sed -i '' -E -e 's|/Users/elliott.ohara/xlights/Christmas/Images/|/Users/elliott.ohara/xlights/Images/|g' "$file"
  sed -i '' -E -e 's|/Users/elliott.ohara/xlights/2022 Christmas/Images/|/Users/elliott.ohara/xlights/Images/|g' "$file"
  # Fix typo in username for image paths
  sed -i '' -E -e 's|/Users/elliottohara/Documents/xLights/2022 Christmas/Images/|/Users/elliott.ohara/xlights/Images/|g' "$file"
  
  # Fix SVG file paths (for Ripple effects and other SVG references)
  sed -i '' -E -e 's|/Users/elliott.ohara/projects/xlights/2022 Christmas/ImportedMedia/|/Users/elliott.ohara/xlights/Christmas/ImportedMedia/|g' "$file"
  
  # Fix xlights path references (from fixpaths.sh functionality)
  sed -i '' -E -e 's|xlights/Christmas/|xlights/|g' -e 's|xlights/Halloween/|xlights/|g' "$file"
  sed -i '' -E -e 's|2022 Christmas/Audio/|Audio/|g' -e 's|2022 Christmas/Video/|Video/|g' "$file"
done

echo "✅ Done! Backups saved as *.bak"

